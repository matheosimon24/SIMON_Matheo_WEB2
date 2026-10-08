"""Partenaire simulé : reçoit les tickets envoyés par MATRiCE.

Lancement : uvicorn partenaire.app:app --port 8001
Mode de simulation : variable d'environnement PARTENAIRE_MODE (défaut « ok »),
ou paramètre de requête ?mode=... qui le remplace pour une requête.

Modes (contrat du sujet) :
  ok      succès immédiat
  flaky   503 à la première tentative d'un ticket, puis succès
  down    503 permanent
  slow    réponse après 3 s (au-delà du timeout de 2 s du récepteur)
  reject  400 permanent
"""

import asyncio
import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

MODES = {"ok", "flaky", "down", "slow", "reject"}
journal = logging.getLogger("partenaire")


def creer_partenaire(mode_par_defaut="ok", attente_lente=3.0):
    app = FastAPI(title="Partenaire simulé")
    app.state.tickets = {}      # Idempotency-Key -> ticket créé
    app.state.tentatives = {}   # Idempotency-Key -> nombre de requêtes reçues

    @app.post("/tickets")
    async def creer_ticket(request: Request, mode: str | None = None):
        mode = mode or mode_par_defaut
        if mode not in MODES:
            return JSONResponse(status_code=400, content={"detail": f"mode inconnu : {mode}"})
        cle = request.headers.get("idempotency-key")
        if not cle:
            return JSONResponse(status_code=400, content={"detail": "en-tête Idempotency-Key obligatoire"})

        app.state.tentatives[cle] = app.state.tentatives.get(cle, 0) + 1
        journal.info("ticket %s : requête n°%d (mode %s)", cle, app.state.tentatives[cle], mode)

        if mode == "down":
            return JSONResponse(status_code=503, content={"detail": "service indisponible"})
        if mode == "reject":
            return JSONResponse(status_code=400, content={"detail": "ticket refusé"})
        if mode == "flaky" and app.state.tentatives[cle] == 1:
            return JSONResponse(status_code=503, content={"detail": "indisponible temporairement"})
        if mode == "slow":
            await asyncio.sleep(attente_lente)

        # Idempotence : la même clé ne crée jamais un deuxième ticket.
        if cle in app.state.tickets:
            return JSONResponse(status_code=200, content=app.state.tickets[cle])
        ticket = {"ticket_id": f"T-{len(app.state.tickets) + 1:04d}", "event_id": cle}
        app.state.tickets[cle] = ticket
        return JSONResponse(status_code=201, content=ticket)

    @app.get("/tickets")
    def lister_tickets():
        """Pour la démonstration : tickets réellement créés."""
        return list(app.state.tickets.values())

    return app


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s : %(message)s")
app = creer_partenaire(os.environ.get("PARTENAIRE_MODE", "ok"))
