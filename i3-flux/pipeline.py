"""Pipeline I3 : lecture -> validation -> normalisation -> déduplication -> sortie.

Usage :
    python pipeline.py donnees/seances.ndjson --sortie sortie

Produit dans le dossier de sortie :
    acceptes.ndjson  séances valides et normalisées, avec source_line
    rejets.ndjson    lignes rejetées, avec source_line et motif
    stats.json       compteurs lus / acceptes / rejets / doublons

Mémoire : le fichier est lu ligne par ligne et chaque résultat est écrit
immédiatement. Seul l'ensemble des id déjà acceptés reste en mémoire,
la consommation ne dépend donc pas de la taille totale du fichier.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# --- Valeurs autorisées (règles du sujet) ---------------------------------

PERIODES = {"am": "am", "matin": "am", "pm": "pm", "après-midi": "pm", "apres-midi": "pm"}
STATUTS = {"proposed": "proposed", "propose": "proposed", "confirmed": "confirmed", "confirme": "confirmed"}
GROUPES = {"A", "B", "Promotion"}
MODES = {"DG", "CE", "AUTO"}
FORMATEURS = {"t1", "t2", "t3"}

# Champs attendus, dans l'ordre utilisé pour la sortie.
CHAMPS = ["id", "date", "period", "group", "mode", "title", "domain", "teacherId", "status"]

DATE_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")  # YYYY-MM-DD
DATE_FR = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")   # DD/MM/YYYY


class LigneInvalide(Exception):
    """Levée quand une ligne doit être rejetée ; le message est le motif."""


# --- Normalisation des champs ---------------------------------------------

def normaliser_date(valeur):
    """Retourne la date au format YYYY-MM-DD, ou lève LigneInvalide.

    On utilise datetime.date (une date de calendrier, sans heure ni fuseau) :
    le résultat ne dépend donc pas du fuseau horaire de la machine.
    """
    if not isinstance(valeur, str):
        raise LigneInvalide("date absente ou non textuelle")
    if m := DATE_ISO.match(valeur):
        annee, mois, jour = m.groups()
    elif m := DATE_FR.match(valeur):
        jour, mois, annee = m.groups()
    else:
        raise LigneInvalide(f"format de date invalide : {valeur!r}")
    try:
        return date(int(annee), int(mois), int(jour)).isoformat()
    except ValueError:
        # Exemple : 2026-02-30 a le bon format mais n'existe pas.
        raise LigneInvalide(f"date inexistante : {valeur!r}") from None


def normaliser_seance(objet):
    """Valide un objet JSON et retourne la séance normalisée.

    Toutes les erreurs de la ligne sont rassemblées dans un seul motif,
    pour que le rejet soit le plus explicite possible.
    """
    if not isinstance(objet, dict):
        raise LigneInvalide("la ligne n'est pas un objet JSON")

    erreurs = []
    seance = {}

    manquants = [champ for champ in CHAMPS if champ not in objet]
    if manquants:
        raise LigneInvalide("champs manquants : " + ", ".join(manquants))

    # id, titre et domaine : chaînes non vides
    for champ in ("id", "title", "domain"):
        valeur = objet[champ]
        if not isinstance(valeur, str) or not valeur.strip():
            erreurs.append(f"{champ} vide ou invalide")
        else:
            seance[champ] = valeur.strip()

    try:
        seance["date"] = normaliser_date(objet["date"])
    except LigneInvalide as e:
        erreurs.append(str(e))

    if objet["period"] in PERIODES:
        seance["period"] = PERIODES[objet["period"]]
    else:
        erreurs.append(f"période invalide : {objet['period']!r}")

    if objet["group"] in GROUPES:
        seance["group"] = objet["group"]
    else:
        erreurs.append(f"groupe invalide : {objet['group']!r}")

    if objet["mode"] in MODES:
        seance["mode"] = objet["mode"]
    else:
        erreurs.append(f"mode invalide : {objet['mode']!r}")

    if objet["teacherId"] is None or objet["teacherId"] in FORMATEURS:
        seance["teacherId"] = objet["teacherId"]
    else:
        erreurs.append(f"teacherId invalide : {objet['teacherId']!r}")

    if objet["status"] in STATUTS:
        seance["status"] = STATUTS[objet["status"]]
    else:
        erreurs.append(f"statut invalide : {objet['status']!r}")

    # Règles métier, vérifiées seulement si les champs concernés sont valides.
    if seance.get("mode") == "AUTO" and "teacherId" in seance and "status" in seance:
        if seance["teacherId"] is not None or seance["status"] != "proposed":
            erreurs.append("le mode AUTO exige teacherId null et le statut proposed")
    if seance.get("status") == "confirmed" and "teacherId" in seance and seance["teacherId"] is None:
        erreurs.append("le statut confirmed exige un formateur")

    if erreurs:
        raise LigneInvalide("; ".join(erreurs))

    return {champ: seance[champ] for champ in CHAMPS}


# --- Traitement du flux ----------------------------------------------------

def traiter_flux(lignes):
    """Traite un flux de lignes (bytes) et produit un résultat par ligne.

    Chaque résultat est un tuple (type, donnees) avec type parmi
    "accepte", "rejet" ou "doublon". C'est un générateur : rien n'est
    accumulé, sauf l'ensemble des id déjà acceptés.
    """
    ids_vus = set()
    for numero, brute in enumerate(lignes, start=1):
        # Fin de ligne retirée (LF ou CRLF) ; BOM éventuel retiré en ligne 1.
        brute = brute.rstrip(b"\r\n")
        if numero == 1 and brute.startswith(b"\xef\xbb\xbf"):
            brute = brute[3:]

        try:
            texte = brute.decode("utf-8")
        except UnicodeDecodeError:
            yield "rejet", {"source_line": numero, "motif": "encodage invalide (UTF-8 attendu)"}
            continue

        # 1. Lecture JSON
        try:
            objet = json.loads(texte)
        except json.JSONDecodeError as e:
            motif = "ligne vide" if not texte.strip() else f"JSON malformé : {e.msg}"
            yield "rejet", {"source_line": numero, "motif": motif, "ligne": texte}
            continue

        # 2 et 3. Validation + normalisation (avant la déduplication)
        try:
            seance = normaliser_seance(objet)
        except LigneInvalide as e:
            yield "rejet", {"source_line": numero, "motif": str(e), "ligne": texte}
            continue

        # 4. Déduplication : seule la première occurrence valide d'un id est gardée.
        if seance["id"] in ids_vus:
            yield "doublon", {"source_line": numero, "id": seance["id"]}
            continue
        ids_vus.add(seance["id"])

        yield "accepte", {"source_line": numero, **seance}


def executer(chemin_entree, dossier_sortie):
    """Lance le pipeline complet et retourne les statistiques."""
    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    stats = {"lus": 0, "acceptes": 0, "rejets": 0, "doublons": 0}
    compteurs = {"accepte": "acceptes", "rejet": "rejets", "doublon": "doublons"}

    # newline="\n" : sortie identique sous Windows et Linux.
    with open(chemin_entree, "rb") as entree, \
         open(dossier_sortie / "acceptes.ndjson", "w", encoding="utf-8", newline="\n") as acceptes, \
         open(dossier_sortie / "rejets.ndjson", "w", encoding="utf-8", newline="\n") as rejets:
        for type_resultat, donnees in traiter_flux(entree):
            stats["lus"] += 1
            stats[compteurs[type_resultat]] += 1
            if type_resultat == "accepte":
                acceptes.write(json.dumps(donnees, ensure_ascii=False) + "\n")
            elif type_resultat == "rejet":
                rejets.write(json.dumps(donnees, ensure_ascii=False) + "\n")

    # Invariant demandé par le sujet.
    assert stats["lus"] == stats["acceptes"] + stats["rejets"] + stats["doublons"]

    with open(dossier_sortie / "stats.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return stats


def main(argv=None):
    parser = argparse.ArgumentParser(description="Normalise un fichier NDJSON de séances MATRiCE.")
    parser.add_argument("entree", help="fichier NDJSON à traiter")
    parser.add_argument("--sortie", default="sortie", help="dossier de sortie (défaut : sortie)")
    args = parser.parse_args(argv)

    if not Path(args.entree).is_file():
        print(f"Erreur : fichier introuvable : {args.entree}", file=sys.stderr)
        return 2

    stats = executer(args.entree, args.sortie)
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
