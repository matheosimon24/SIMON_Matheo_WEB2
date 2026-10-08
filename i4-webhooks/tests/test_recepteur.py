"""Tests du récepteur : santé, signature, ancienneté, taille, contenu, doublon, suivi des livraisons."""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from recepteur.main import creer_app
from tests.outils import MAINTENANT, SECRET, entetes_signes, envoyer, evenement


@pytest.fixture
def client():
    app = creer_app(secret=SECRET, horloge=lambda: MAINTENANT)
    with TestClient(app) as c:
        yield c


def test_sante(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok"}


# --- Signature -------------------------------------------------------------

def test_signature_valide_acceptee(client):
    reponse = envoyer(client, evenement())
    assert reponse.status_code == 202
    assert reponse.json() == {"event_id": "evt-001", "duplicate": False}


def test_signature_invalide_refusee(client):
    reponse = envoyer(client, evenement(), secret="mauvais-secret")
    assert reponse.status_code == 401
    assert client.get("/deliveries/evt-001").status_code == 404  # rien n'a été enregistré


def test_corps_modifie_apres_signature_refuse(client):
    corps = json.dumps(evenement()).encode()
    h = entetes_signes(corps)
    falsifie = corps.replace(b'"t1"', b'"t2"')
    assert client.post("/webhooks/planning", content=falsifie, headers=h).status_code == 401


def test_signature_calculee_sur_le_corps_brut(client):
    # Même JSON, mais espaces et ordre des clés différents : la signature porte sur ces octets exacts.
    corps = b'{ "type": "session.updated",  "event_id": "evt-brut", "occurred_at": "2026-10-19T08:30:00Z",' \
            b' "session": {"id": "s01", "date": "2026-10-19", "period": "am", "group": "A", "mode": "DG",' \
            b' "title": "React", "domain": "web", "teacherId": "t1", "status": "confirmed"} }'
    assert envoyer(client, corps).status_code == 202


@pytest.mark.parametrize("entetes", [
    {"X-Signature": ""},
    {"X-Signature": "md5=abc"},
    {"X-Timestamp": ""},
    {"X-Timestamp": "hier"},
])
def test_entetes_absents_ou_mal_formes_refuses(client, entetes):
    assert envoyer(client, evenement(), entetes=entetes).status_code == 401


# --- Ancienneté ------------------------------------------------------------

@pytest.mark.parametrize("decalage, attendu", [
    (-301, 401),  # trop ancien (rejeu)
    (301, 401),   # trop dans le futur
    (-300, 202),  # limite exacte acceptée
    (300, 202),
])
def test_anciennete_du_timestamp(client, decalage, attendu):
    reponse = envoyer(client, evenement(), timestamp=MAINTENANT + decalage)
    assert reponse.status_code == attendu


# --- Taille ----------------------------------------------------------------

def test_corps_trop_volumineux_refuse(client):
    corps = json.dumps({**evenement(), "remplissage": "x" * (64 * 1024)}).encode()
    assert len(corps) > 64 * 1024
    assert envoyer(client, corps).status_code == 413


def test_corps_a_la_limite_accepte(client):
    base = json.dumps({**evenement(), "remplissage": ""}).encode()
    corps = base.replace(b'"remplissage": ""', b'"remplissage": "' + b"x" * (64 * 1024 - len(base)) + b'"')
    assert len(corps) == 64 * 1024
    assert envoyer(client, corps).status_code == 202


# --- Contenu authentifié mais invalide (400) ---------------------------------

def test_json_invalide_authentifie(client):
    assert envoyer(client, b'{"event_id": "evt-001",').status_code == 400


@pytest.mark.parametrize("modif, extrait", [
    (lambda e: e.update(event_id=""), "event_id"),
    (lambda e: e.update(type="session.deleted"), "type"),
    (lambda e: e.update(occurred_at="2026-10-19T08:30:00"), "fuseau"),
    (lambda e: e.update(occurred_at="hier"), "ISO 8601"),
    (lambda e: e["session"].update(mode="AUTO"), "AUTO"),
    (lambda e: e["session"].update(teacherId=None), "confirmed exige un formateur"),
    (lambda e: e["session"].update(date="2026-02-30"), "date"),
    (lambda e: e["session"].update(period=[]), "period"),
    (lambda e: e.update(session="s01"), "session"),
])
def test_evenement_invalide_refuse(client, modif, extrait):
    e = evenement()
    modif(e)
    reponse = envoyer(client, e)
    assert reponse.status_code == 400
    assert extrait in json.dumps(reponse.json(), ensure_ascii=False)


def test_mode_auto_valide(client):
    e = evenement(mode="AUTO", teacherId=None, status="proposed")
    assert envoyer(client, e).status_code == 202


# --- Doublon et suivi --------------------------------------------------------

def test_doublon_renvoie_200_sans_nouvel_enregistrement(client):
    assert envoyer(client, evenement()).status_code == 202
    avant = client.get("/deliveries/evt-001").json()

    reponse = envoyer(client, evenement())
    assert reponse.status_code == 200
    assert reponse.json() == {"event_id": "evt-001", "duplicate": True}
    assert client.get("/deliveries/evt-001").json() == avant


def test_suivi_livraison_inconnue(client):
    assert client.get("/deliveries/inconnu").status_code == 404


# --- Logs ----------------------------------------------------------------------

def test_logs_ne_contiennent_jamais_le_secret_ni_la_signature(client, caplog):
    caplog.set_level(logging.INFO, logger="matrice.webhooks")
    corps = json.dumps(evenement()).encode()
    signature = entetes_signes(corps)["X-Signature"]
    envoyer(client, evenement())
    envoyer(client, evenement(), secret="mauvais-secret")
    envoyer(client, evenement())
    assert caplog.text  # des logs ont bien été produits
    assert SECRET not in caplog.text
    assert signature.removeprefix("sha256=") not in caplog.text
