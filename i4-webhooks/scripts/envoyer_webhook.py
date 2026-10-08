"""Envoie un webhook signé au récepteur (comme le ferait MATRiCE), puis affiche le suivi de livraison.

Usage (récepteur et partenaire lancés) :
    python scripts/envoyer_webhook.py --event-id evt-demo-1
    python scripts/envoyer_webhook.py --event-id evt-demo-1            # 2e envoi : doublon
    python scripts/envoyer_webhook.py --event-id evt-faux --secret mauvais   # signature invalide -> 401
"""

import argparse
import hashlib
import hmac
import json
import os
import time

import httpx


def main():
    parser = argparse.ArgumentParser(description="Envoie un webhook session.updated signé.")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--event-id", default=f"evt-{int(time.time())}")
    parser.add_argument("--secret", default=os.environ.get("MATRICE_WEBHOOK_SECRET", "matrice-local-only"))
    parser.add_argument("--decalage", type=int, default=0, help="décale l'horodatage (ex. -400 pour un webhook trop ancien)")
    args = parser.parse_args()

    evenement = {
        "event_id": args.event_id,
        "type": "session.updated",
        "occurred_at": "2026-10-19T08:30:00+02:00",
        "session": {
            "id": "s01", "date": "2026-10-19", "period": "am", "group": "A", "mode": "DG",
            "title": "React composants", "domain": "web", "teacherId": "t1", "status": "confirmed",
        },
    }
    corps = json.dumps(evenement).encode("utf-8")
    timestamp = str(int(time.time()) + args.decalage)
    signature = hmac.new(args.secret.encode(), timestamp.encode() + b"." + corps, hashlib.sha256).hexdigest()

    reponse = httpx.post(
        f"{args.url}/webhooks/planning",
        content=corps,
        headers={"Content-Type": "application/json", "X-Timestamp": timestamp, "X-Signature": f"sha256={signature}"},
    )
    print(f"POST /webhooks/planning -> {reponse.status_code} {reponse.text}")

    if reponse.status_code in (200, 202):
        # La livraison se fait en arrière-plan : on suit son état quelques secondes.
        for _ in range(20):
            suivi = httpx.get(f"{args.url}/deliveries/{args.event_id}").json()
            if suivi["status"] != "pending":
                break
            time.sleep(0.5)
        print(f"GET /deliveries/{args.event_id} -> {suivi}")


if __name__ == "__main__":
    main()
