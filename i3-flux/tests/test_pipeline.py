"""Tests du pipeline I3.

Cas demandés par le sujet : ligne valide, invalide, doublon, JSON malformé, fichier vide.
S'y ajoutent le fichier complet du sujet, le déterminisme et quelques cas limites.
"""

import json
from pathlib import Path

import pytest

from pipeline import LigneInvalide, executer, main, normaliser_seance, traiter_flux

FICHIER_SUJET = Path(__file__).resolve().parent.parent / "donnees" / "seances.ndjson"


def seance(**modifs):
    """Séance valide de référence, dont on peut modifier certains champs."""
    base = {
        "id": "s01", "date": "2026-10-19", "period": "am", "group": "A", "mode": "DG",
        "title": "React composants", "domain": "web", "teacherId": "t1", "status": "confirmed",
    }
    base.update(modifs)
    return base


def lignes(*objets):
    """Transforme des objets (ou des chaînes brutes) en lignes bytes, comme un fichier lu en binaire."""
    resultat = []
    for o in objets:
        texte = o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)
        resultat.append((texte + "\n").encode("utf-8"))
    return resultat


def lire_ndjson(chemin):
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


# --- Ligne valide -----------------------------------------------------------

def test_ligne_valide_est_normalisee():
    brute = seance(date="19/10/2026", period="matin", status="confirme")
    assert normaliser_seance(brute) == seance()


@pytest.mark.parametrize("periode, attendu", [
    ("matin", "am"), ("am", "am"), ("après-midi", "pm"), ("apres-midi", "pm"), ("pm", "pm"),
])
def test_periodes_normalisees(periode, attendu):
    assert normaliser_seance(seance(period=periode))["period"] == attendu


def test_mode_auto_valide():
    resultat = normaliser_seance(seance(mode="AUTO", teacherId=None, status="propose"))
    assert resultat["teacherId"] is None
    assert resultat["status"] == "proposed"


# --- Lignes invalides -------------------------------------------------------

@pytest.mark.parametrize("modifs, motif", [
    ({"date": "2026-02-30"}, "date inexistante"),
    ({"date": "19-10-2026"}, "format de date invalide"),
    ({"period": "soir"}, "période invalide"),
    ({"group": "C"}, "groupe invalide"),
    ({"mode": "VISIO"}, "mode invalide"),
    ({"teacherId": "t9"}, "teacherId invalide"),
    ({"status": "annule"}, "statut invalide"),
    ({"title": ""}, "title vide"),
    ({"mode": "AUTO", "teacherId": "t1", "status": "proposed"}, "AUTO exige"),
    ({"mode": "AUTO", "teacherId": None, "status": "confirmed"}, "AUTO exige"),
    ({"teacherId": None, "status": "confirmed"}, "confirmed exige un formateur"),
])
def test_ligne_invalide_rejetee_avec_motif(modifs, motif):
    with pytest.raises(LigneInvalide, match=motif):
        normaliser_seance(seance(**modifs))


def test_champ_manquant_rejete():
    incomplete = seance()
    del incomplete["status"]
    with pytest.raises(LigneInvalide, match="champs manquants : status"):
        normaliser_seance(incomplete)


def test_json_qui_n_est_pas_un_objet_rejete():
    resultats = list(traiter_flux(lignes("[1, 2, 3]")))
    assert resultats[0][0] == "rejet"
    assert "pas un objet" in resultats[0][1]["motif"]


@pytest.mark.parametrize("champ", ["period", "group", "mode", "teacherId", "status"])
@pytest.mark.parametrize("valeur", [[], {}, 42])
def test_valeur_non_textuelle_rejetee_sans_planter(champ, valeur):
    # Une liste ou un objet JSON à la place d'un texte doit donner un rejet, pas une erreur Python.
    flux = lignes(seance(id="a", **{champ: valeur}), seance(id="b"))
    resultats = list(traiter_flux(flux))
    assert [t for t, _ in resultats] == ["rejet", "accepte"]
    assert "invalide" in resultats[0][1]["motif"]


def test_ligne_invalide_n_interrompt_pas_les_suivantes():
    flux = lignes(seance(id="a", period="soir"), seance(id="b"))
    types = [t for t, _ in traiter_flux(flux)]
    assert types == ["rejet", "accepte"]


# --- Doublons ---------------------------------------------------------------

def test_doublon_garde_la_premiere_occurrence():
    flux = lignes(seance(title="Original"), seance(title="Copie"))
    resultats = list(traiter_flux(flux))
    assert resultats[0] == ("accepte", {"source_line": 1, **seance(title="Original")})
    assert resultats[1] == ("doublon", {"source_line": 2, "id": "s01"})


def test_validation_avant_deduplication():
    # La première occurrence est invalide : c'est la deuxième (valide) qui doit être retenue.
    flux = lignes(seance(date="2026-02-30"), seance(title="Valide"))
    resultats = list(traiter_flux(flux))
    assert [t for t, _ in resultats] == ["rejet", "accepte"]
    assert resultats[1][1]["title"] == "Valide"


# --- JSON malformé ----------------------------------------------------------

def test_json_malforme_rejete_puis_traitement_continue():
    flux = lignes('{"id":"bad4","title":"JSON tronqué"', seance())
    resultats = list(traiter_flux(flux))
    assert resultats[0][0] == "rejet"
    assert resultats[0][1]["source_line"] == 1
    assert resultats[0][1]["motif"].startswith("JSON malformé")
    assert resultats[1][0] == "accepte"


def test_encodage_invalide_rejete():
    resultats = list(traiter_flux([b"\xff\xfe pas de l'UTF-8\n"]))
    assert resultats[0][0] == "rejet"
    assert "encodage" in resultats[0][1]["motif"]


def test_ligne_vide_rejetee():
    resultats = list(traiter_flux([b"\n"]))
    assert resultats == [("rejet", {"source_line": 1, "motif": "ligne vide", "ligne": ""})]


# --- Fichier vide -----------------------------------------------------------

def test_fichier_vide(tmp_path):
    entree = tmp_path / "vide.ndjson"
    entree.write_bytes(b"")
    stats = executer(entree, tmp_path / "sortie")
    assert stats == {"lus": 0, "acceptes": 0, "rejets": 0, "doublons": 0}
    assert (tmp_path / "sortie" / "acceptes.ndjson").read_text(encoding="utf-8") == ""
    assert (tmp_path / "sortie" / "rejets.ndjson").read_text(encoding="utf-8") == ""


# --- Fichier complet du sujet -----------------------------------------------

def test_fichier_du_sujet(tmp_path):
    stats = executer(FICHIER_SUJET, tmp_path)

    assert stats == {"lus": 12, "acceptes": 6, "rejets": 4, "doublons": 2}
    assert json.loads((tmp_path / "stats.json").read_text(encoding="utf-8")) == stats

    acceptes = lire_ndjson(tmp_path / "acceptes.ndjson")
    assert [(a["source_line"], a["id"]) for a in acceptes] == [
        (1, "s01"), (2, "s02"), (3, "s03"), (5, "s04"), (6, "s05"), (11, "s06"),
    ]
    assert acceptes[0]["date"] == "2026-10-19"      # 19/10/2026 normalisée
    assert acceptes[0]["status"] == "confirmed"     # confirme normalisé
    assert acceptes[-1]["period"] == "pm"           # après-midi normalisé

    rejets = lire_ndjson(tmp_path / "rejets.ndjson")
    assert [r["source_line"] for r in rejets] == [7, 8, 9, 12]
    assert all(r["motif"] for r in rejets)


def test_meme_fichier_meme_resultat(tmp_path):
    executer(FICHIER_SUJET, tmp_path / "run1")
    executer(FICHIER_SUJET, tmp_path / "run2")
    for nom in ("acceptes.ndjson", "rejets.ndjson", "stats.json"):
        assert (tmp_path / "run1" / nom).read_bytes() == (tmp_path / "run2" / nom).read_bytes()


def test_fins_de_ligne_windows_et_bom(tmp_path):
    # Même contenu, mais avec un BOM UTF-8 et des fins de ligne CRLF.
    contenu = FICHIER_SUJET.read_bytes().replace(b"\n", b"\r\n")
    entree = tmp_path / "windows.ndjson"
    entree.write_bytes(b"\xef\xbb\xbf" + contenu)
    executer(FICHIER_SUJET, tmp_path / "unix")
    executer(entree, tmp_path / "windows")
    assert (tmp_path / "unix" / "acceptes.ndjson").read_bytes() == \
           (tmp_path / "windows" / "acceptes.ndjson").read_bytes()


# --- Ligne de commande ------------------------------------------------------

def test_cli_fichier_introuvable(tmp_path, capsys):
    code = main([str(tmp_path / "absent.ndjson"), "--sortie", str(tmp_path)])
    assert code == 2
    assert "introuvable" in capsys.readouterr().err


def test_cli_affiche_les_stats(tmp_path, capsys):
    code = main([str(FICHIER_SUJET), "--sortie", str(tmp_path)])
    assert code == 0
    assert json.loads(capsys.readouterr().out) == {"lus": 12, "acceptes": 6, "rejets": 4, "doublons": 2}
