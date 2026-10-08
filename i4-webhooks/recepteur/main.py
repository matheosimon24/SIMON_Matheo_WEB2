"""Récepteur de webhooks MATRiCE (FastAPI).

Lancement : uvicorn recepteur.main:app --port 8000
"""

import json
import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from recepteur.signature import WebhookNonAuthentifie, verifier_webhook
from recepteur.stockage import StockageLivraisons
from recepteur.validation import EvenementInvalide, valider_evenement

TAILLE_MAX_OCTETS = 64 * 1024  # 64 Ko

# Secret de développement local, imposé par le sujet. En production il viendrait d'un
# gestionnaire de secrets ; ici il peut être remplacé par la variable d'environnement.
SECRET_PAR_DEFAUT = "matrice-local-only"

journal = logging.getLogger("matrice.webhooks")


def creer_app(secret=None, horloge=time.time):
    """Fabrique l'application. horloge est injectable pour tester l'ancienneté sans attendre."""
    secret = secret or os.environ.get("MATRICE_WEBHOOK_SECRET", SECRET_PAR_DEFAUT)
    app = FastAPI(title="MATRiCE – récepteur de webhooks")
    stockage = StockageLivraisons()
    app.state.stockage = stockage

    def erreur(code, message):
        return JSONResponse(status_code=code, content={"detail": message})

    @app.get("/health")
    def sante():
        return {"status": "ok"}

    @app.post("/webhooks/planning")
    async def recevoir(request: Request):
        # 1. Taille : vérifiée AVANT tout calcul, pour ne pas traiter un corps énorme.
        longueur = request.headers.get("content-length")
        if longueur and longueur.isdigit() and int(longueur) > TAILLE_MAX_OCTETS:
            journal.warning("webhook refusé : corps trop volumineux (%s octets)", longueur)
            return erreur(413, "corps supérieur à 64 Ko")
        corps_brut = await request.body()  # octets exacts reçus, nécessaires à la signature
        if len(corps_brut) > TAILLE_MAX_OCTETS:
            journal.warning("webhook refusé : corps trop volumineux (%d octets)", len(corps_brut))
            return erreur(413, "corps supérieur à 64 Ko")

        # 2. Authentification : horodatage puis signature HMAC.
        try:
            verifier_webhook(
                secret,
                request.headers.get("x-timestamp"),
                request.headers.get("x-signature"),
                corps_brut,
                maintenant=horloge(),
            )
        except WebhookNonAuthentifie as e:
            journal.warning("webhook refusé (401) : %s", e)
            return erreur(401, str(e))

        # 3. Contenu : JSON valide et conforme au contrat (le corps est maintenant authentifié).
        try:
            evenement = json.loads(corps_brut)
            valider_evenement(evenement)
        except json.JSONDecodeError:
            journal.warning("webhook refusé (400) : JSON invalide")
            return erreur(400, "corps JSON invalide")
        except EvenementInvalide as e:
            journal.warning("webhook refusé (400) : %s", "; ".join(e.args[0]))
            return erreur(400, e.args[0])

        # 4. Déduplication par event_id.
        event_id = evenement["event_id"]
        if not stockage.enregistrer_si_nouveau(event_id):
            journal.info("événement %s déjà reçu : doublon ignoré, aucune nouvelle livraison", event_id)
            return JSONResponse(status_code=200, content={"event_id": event_id, "duplicate": True})

        journal.info("événement %s accepté", event_id)
        return JSONResponse(status_code=202, content={"event_id": event_id, "duplicate": False})

    @app.get("/deliveries/{event_id}")
    def etat_livraison(event_id: str):
        livraison = stockage.lire(event_id)
        if livraison is None:
            return erreur(404, "événement inconnu")
        return livraison

    return app


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s : %(message)s")
app = creer_app()
