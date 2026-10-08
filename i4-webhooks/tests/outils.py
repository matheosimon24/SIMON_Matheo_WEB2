"""Fonctions communes aux tests : fabriquer un événement valide et le signer comme le ferait MATRiCE."""

import json

from recepteur.signature import calculer_signature

SECRET = "matrice-local-only"
MAINTENANT = 1_790_000_000  # instant fixe (secondes Unix) : les tests ne dépendent pas de l'heure réelle


def evenement(event_id="evt-001", **modifs_session):
    session = {
        "id": "s01", "date": "2026-10-19", "period": "am", "group": "A", "mode": "DG",
        "title": "React composants", "domain": "web", "teacherId": "t1", "status": "confirmed",
    }
    session.update(modifs_session)
    return {
        "event_id": event_id,
        "type": "session.updated",
        "occurred_at": "2026-10-19T08:30:00+02:00",
        "session": session,
    }


def entetes_signes(corps, timestamp=MAINTENANT, secret=SECRET):
    ts = str(timestamp)
    return {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Signature": "sha256=" + calculer_signature(secret, ts, corps),
    }


def envoyer(client, contenu, timestamp=MAINTENANT, secret=SECRET, entetes=None):
    """Envoie un webhook signé. contenu peut être un dict (sérialisé ici) ou des octets bruts."""
    corps = contenu if isinstance(contenu, bytes) else json.dumps(contenu).encode("utf-8")
    h = entetes_signes(corps, timestamp, secret)
    if entetes:
        h.update(entetes)
    return client.post("/webhooks/planning", content=corps, headers=h)
