"""Livraison d'un événement au partenaire, avec timeout, relances et quarantaine.

Règles du contrat :
- timeout de 2 s par tentative, 3 tentatives au maximum ;
- relance sur timeout, erreur réseau, 429 et 5xx ;
- pas de relance sur les autres 4xx (la requête est refusée, la renvoyer ne changerait rien) ;
- attente de 0,2 s puis 0,4 s entre les tentatives ;
- échec final -> quarantine (à traiter par un humain ou une reprise ultérieure).
"""

import asyncio
import logging

import httpx

from recepteur.stockage import LIVRE, QUARANTAINE

TIMEOUT_SECONDES = 2.0
TENTATIVES_MAX = 3
ATTENTES = (0.2, 0.4)  # avant la 2e puis avant la 3e tentative

journal = logging.getLogger("matrice.webhooks")


def doit_relancer(code_http):
    return code_http == 429 or code_http >= 500


async def livrer(evenement, url_partenaire, stockage, attendre=asyncio.sleep, transport=None):
    """Envoie l'événement au partenaire. attendre et transport sont injectables pour les tests."""
    event_id = evenement["event_id"]
    # Idempotency-Key = event_id : si une tentative a réussi chez le partenaire mais que la réponse
    # s'est perdue (timeout), la tentative suivante ne crée pas de deuxième ticket.
    entetes = {"Idempotency-Key": event_id}
    corps = {"event_id": event_id, "session": evenement["session"]}

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDES, transport=transport) as client:
        for tentative in range(1, TENTATIVES_MAX + 1):
            stockage.compter_tentative(event_id)
            try:
                reponse = await client.post(url_partenaire, json=corps, headers=entetes)
            except httpx.TimeoutException:
                raison, relancer = "timeout (> 2 s)", True
            except httpx.TransportError as e:
                raison, relancer = f"erreur réseau ({type(e).__name__})", True
            else:
                if reponse.is_success:
                    stockage.changer_statut(event_id, LIVRE)
                    journal.info("livraison %s : réussie (HTTP %d, tentative %d)",
                                 event_id, reponse.status_code, tentative)
                    return
                raison, relancer = f"HTTP {reponse.status_code}", doit_relancer(reponse.status_code)

            if not relancer:
                stockage.changer_statut(event_id, QUARANTAINE)
                journal.warning("livraison %s : %s, erreur définitive sans relance -> quarantine",
                                event_id, raison)
                return
            if tentative == TENTATIVES_MAX:
                stockage.changer_statut(event_id, QUARANTAINE)
                journal.warning("livraison %s : %s, %d tentatives épuisées -> quarantine",
                                event_id, raison, tentative)
                return

            attente = ATTENTES[tentative - 1]
            journal.info("livraison %s : %s (tentative %d), nouvelle tentative dans %.1f s",
                         event_id, raison, tentative, attente)
            await attendre(attente)
