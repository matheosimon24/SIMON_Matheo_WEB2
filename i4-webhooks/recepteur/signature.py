"""Vérification de l'authenticité d'un webhook : horodatage + signature HMAC-SHA256."""

import hashlib
import hmac

# Écart maximal toléré entre l'horodatage du webhook et l'heure de réception (contrat : 300 s).
ECART_MAX_SECONDES = 300


class WebhookNonAuthentifie(Exception):
    """Levée quand le webhook doit être refusé avec un 401. Le message ne contient jamais le secret."""


def calculer_signature(secret, timestamp, corps_brut):
    """Signature attendue : HMAC-SHA256(secret, timestamp + "." + corps brut), en hexadécimal.

    On signe les OCTETS reçus, sans re-sérialiser le JSON : un simple changement d'espaces
    ou d'ordre des clés donnerait sinon une autre signature.
    """
    message = timestamp.encode("ascii") + b"." + corps_brut
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def verifier_webhook(secret, entete_timestamp, entete_signature, corps_brut, maintenant):
    """Vérifie l'horodatage puis la signature ; lève WebhookNonAuthentifie en cas d'échec."""
    # 1. Horodatage : entier en secondes Unix, à moins de 300 s de l'heure de réception.
    if not entete_timestamp or not (entete_timestamp.isascii() and entete_timestamp.isdigit()):
        raise WebhookNonAuthentifie("en-tête X-Timestamp absent ou invalide")
    if abs(maintenant - int(entete_timestamp)) > ECART_MAX_SECONDES:
        # Protège contre le rejeu d'un ancien webhook intercepté.
        raise WebhookNonAuthentifie("horodatage trop éloigné de l'heure de réception")

    # 2. Signature : format « sha256=<hex> ».
    if not entete_signature or not entete_signature.startswith("sha256="):
        raise WebhookNonAuthentifie("en-tête X-Signature absent ou mal formé")
    recue = entete_signature.removeprefix("sha256=")
    attendue = calculer_signature(secret, entete_timestamp, corps_brut)
    # compare_digest compare en temps constant : le temps de réponse ne révèle pas
    # combien de caractères sont corrects (attaque temporelle).
    if not hmac.compare_digest(recue, attendue):
        raise WebhookNonAuthentifie("signature invalide")
