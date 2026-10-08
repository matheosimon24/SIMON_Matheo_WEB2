"""Suivi des événements reçus et de leur livraison, en mémoire.

Limite (acceptée par le sujet, documentée) : tout est perdu au redémarrage du serveur.
Après un redémarrage, un événement déjà reçu serait donc accepté une deuxième fois ;
l'en-tête Idempotency-Key envoyé au partenaire évite quand même un ticket en double chez lui.
"""

EN_ATTENTE = "pending"
LIVRE = "delivered"
QUARANTAINE = "quarantine"


class StockageLivraisons:
    def __init__(self):
        self._livraisons = {}

    def enregistrer_si_nouveau(self, event_id):
        """Retourne True si l'événement est nouveau (et l'enregistre « pending »), False si c'est un doublon.

        Pas d'« await » entre le test et l'écriture : dans la boucle asyncio, deux requêtes
        ne peuvent pas s'intercaler ici, donc pas de double enregistrement.
        """
        if event_id in self._livraisons:
            return False
        self._livraisons[event_id] = {"event_id": event_id, "status": EN_ATTENTE, "attempts": 0}
        return True

    def lire(self, event_id):
        livraison = self._livraisons.get(event_id)
        return dict(livraison) if livraison else None

    def compter_tentative(self, event_id):
        self._livraisons[event_id]["attempts"] += 1

    def changer_statut(self, event_id, statut):
        self._livraisons[event_id]["status"] = statut
