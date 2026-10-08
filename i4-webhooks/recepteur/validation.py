"""Validation du contenu d'un événement authentifié (contrat + règles métier des séances)."""

import re
from datetime import date, datetime

GROUPES = {"A", "B", "Promotion"}
MODES = {"DG", "CE", "AUTO"}
PERIODES = {"am", "pm"}
STATUTS = {"proposed", "confirmed"}
FORMATEURS = {"t1", "t2", "t3"}
DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class EvenementInvalide(Exception):
    """Levée quand l'événement est authentifié mais invalide (réponse 400)."""


def est_texte_non_vide(valeur):
    return isinstance(valeur, str) and valeur.strip() != ""


def est_parmi(valeur, autorisees):
    # Contrôle du type d'abord : une liste ou un objet JSON ne peut pas être cherché dans un set.
    return isinstance(valeur, str) and valeur in autorisees


def valider_occurred_at(valeur):
    """ISO 8601 AVEC fuseau horaire (ex. 2026-10-19T08:30:00+02:00 ou ...Z)."""
    if not isinstance(valeur, str):
        return "occurred_at doit être une date ISO 8601"
    try:
        moment = datetime.fromisoformat(valeur)
    except ValueError:
        return "occurred_at n'est pas une date ISO 8601"
    if moment.tzinfo is None:
        return "occurred_at doit préciser un fuseau horaire"
    return None


def valider_date(valeur):
    if not isinstance(valeur, str) or not DATE_ISO.match(valeur):
        return False
    try:
        date.fromisoformat(valeur)
    except ValueError:
        return False  # ex. 2026-02-30
    return True


def valider_session(session):
    """Retourne la liste des erreurs de la séance (vide si elle est conforme)."""
    if not isinstance(session, dict):
        return ["session doit être un objet"]
    erreurs = []
    for champ in ("id", "title", "domain"):
        if not est_texte_non_vide(session.get(champ)):
            erreurs.append(f"session.{champ} vide ou invalide")
    if not valider_date(session.get("date")):
        erreurs.append("session.date invalide (YYYY-MM-DD attendu)")
    if not est_parmi(session.get("period"), PERIODES):
        erreurs.append("session.period invalide (am ou pm)")
    if not est_parmi(session.get("group"), GROUPES):
        erreurs.append("session.group invalide")
    if not est_parmi(session.get("mode"), MODES):
        erreurs.append("session.mode invalide")
    if not est_parmi(session.get("status"), STATUTS):
        erreurs.append("session.status invalide")
    teacher = session.get("teacherId")
    if teacher is not None and not est_parmi(teacher, FORMATEURS):
        erreurs.append("session.teacherId invalide")

    # Règles métier
    if session.get("mode") == "AUTO" and (teacher is not None or session.get("status") != "proposed"):
        erreurs.append("le mode AUTO exige teacherId null et le statut proposed")
    if session.get("status") == "confirmed" and teacher is None:
        erreurs.append("le statut confirmed exige un formateur")
    return erreurs


def valider_evenement(evenement):
    """Lève EvenementInvalide avec toutes les erreurs trouvées."""
    if not isinstance(evenement, dict):
        raise EvenementInvalide(["le corps doit être un objet JSON"])
    erreurs = []
    if not est_texte_non_vide(evenement.get("event_id")):
        erreurs.append("event_id vide ou absent")
    if evenement.get("type") != "session.updated":
        erreurs.append("type doit valoir session.updated")
    erreur_date = valider_occurred_at(evenement.get("occurred_at"))
    if erreur_date:
        erreurs.append(erreur_date)
    erreurs.extend(valider_session(evenement.get("session")))
    if erreurs:
        raise EvenementInvalide(erreurs)
