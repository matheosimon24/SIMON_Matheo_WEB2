"""Tests de la livraison au partenaire : succès, 503 puis succès, erreur persistante, 400 sans relance,
timeout, 429, partenaire injoignable, idempotence.

Le partenaire simulé tourne dans un VRAI serveur HTTP (uvicorn, port local libre) : le timeout
de 2 s et les erreurs réseau sont donc réellement testés, pas seulement simulés.
"""

import asyncio
import socket
import threading
import time

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from partenaire.app import creer_partenaire
from recepteur.livraison import livrer
from recepteur.main import creer_app
from recepteur.stockage import StockageLivraisons
from tests.outils import MAINTENANT, SECRET, envoyer, evenement


def port_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def partenaire():
    """Démarre le partenaire simulé dans un thread, le temps des tests du module."""
    app = creer_partenaire(mode_par_defaut="ok", attente_lente=3.0)
    port = port_libre()
    serveur = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=serveur.run, daemon=True)
    thread.start()
    while not serveur.started:
        time.sleep(0.02)
    yield app, f"http://127.0.0.1:{port}/tickets"
    serveur.should_exit = True
    thread.join(timeout=5)


class Attentes:
    """Remplace asyncio.sleep : enregistre les pauses demandées au lieu d'attendre réellement."""

    def __init__(self):
        self.demandees = []

    async def __call__(self, secondes):
        self.demandees.append(secondes)


def recepteur(url, attentes):
    app = creer_app(secret=SECRET, horloge=lambda: MAINTENANT, url_partenaire=url, attendre=attentes)
    return TestClient(app)


def livraison(client, event_id):
    return client.get(f"/deliveries/{event_id}").json()


# Avec TestClient, la tâche de fond (livraison) est terminée quand la requête POST rend la main.

def test_partenaire_ok_livre_en_une_tentative(partenaire):
    app_partenaire, url = partenaire
    attentes = Attentes()
    with recepteur(url + "?mode=ok", attentes) as client:
        assert envoyer(client, evenement("evt-ok")).status_code == 202
        assert livraison(client, "evt-ok") == {"event_id": "evt-ok", "status": "delivered", "attempts": 1}
    assert attentes.demandees == []
    assert app_partenaire.state.tickets["evt-ok"]["event_id"] == "evt-ok"


def test_503_puis_succes(partenaire):
    _, url = partenaire
    attentes = Attentes()
    with recepteur(url + "?mode=flaky", attentes) as client:
        envoyer(client, evenement("evt-flaky"))
        assert livraison(client, "evt-flaky") == {"event_id": "evt-flaky", "status": "delivered", "attempts": 2}
    assert attentes.demandees == [0.2]


def test_erreur_persistante_quarantaine_apres_3_tentatives(partenaire):
    _, url = partenaire
    attentes = Attentes()
    with recepteur(url + "?mode=down", attentes) as client:
        envoyer(client, evenement("evt-down"))
        assert livraison(client, "evt-down") == {"event_id": "evt-down", "status": "quarantine", "attempts": 3}
    assert attentes.demandees == [0.2, 0.4]


def test_400_sans_relance(partenaire):
    app_partenaire, url = partenaire
    attentes = Attentes()
    with recepteur(url + "?mode=reject", attentes) as client:
        envoyer(client, evenement("evt-reject"))
        assert livraison(client, "evt-reject") == {"event_id": "evt-reject", "status": "quarantine", "attempts": 1}
    assert attentes.demandees == []
    assert app_partenaire.state.tentatives["evt-reject"] == 1  # une seule requête reçue


def test_partenaire_lent_timeout_puis_quarantaine(partenaire):
    _, url = partenaire
    attentes = Attentes()
    debut = time.monotonic()
    with recepteur(url + "?mode=slow", attentes) as client:
        envoyer(client, evenement("evt-slow"))
        assert livraison(client, "evt-slow") == {"event_id": "evt-slow", "status": "quarantine", "attempts": 3}
    duree = time.monotonic() - debut
    # 3 tentatives coupées à 2 s chacune (le partenaire répond en 3 s) : environ 6 s, jamais 9 s.
    assert 5.5 < duree < 8.5
    assert attentes.demandees == [0.2, 0.4]


def test_doublon_ne_relance_pas_de_livraison(partenaire):
    app_partenaire, url = partenaire
    attentes = Attentes()
    with recepteur(url + "?mode=ok", attentes) as client:
        envoyer(client, evenement("evt-double"))
        reponse = envoyer(client, evenement("evt-double"))
        assert reponse.status_code == 200 and reponse.json()["duplicate"] is True
        assert livraison(client, "evt-double")["attempts"] == 1
    assert app_partenaire.state.tentatives["evt-double"] == 1


def test_partenaire_injoignable_relance_puis_quarantaine():
    attentes = Attentes()
    with recepteur(f"http://127.0.0.1:{port_libre()}/tickets", attentes) as client:
        envoyer(client, evenement("evt-injoignable"))
        assert livraison(client, "evt-injoignable")["status"] == "quarantine"
        assert livraison(client, "evt-injoignable")["attempts"] == 3
    assert attentes.demandees == [0.2, 0.4]


def test_idempotence_cote_partenaire(partenaire):
    """Même Idempotency-Key envoyée deux fois : un seul ticket créé."""
    app_partenaire, url = partenaire
    corps = {"event_id": "evt-idem", "session": evenement()["session"]}
    entetes = {"Idempotency-Key": "evt-idem"}
    premiere = httpx.post(url, json=corps, headers=entetes)
    seconde = httpx.post(url, json=corps, headers=entetes)
    assert premiere.status_code == 201
    assert seconde.status_code == 200
    assert premiere.json() == seconde.json()
    assert [t for t in app_partenaire.state.tickets if t == "evt-idem"] == ["evt-idem"]


# --- Cas non couverts par les modes du partenaire : réponses simulées avec httpx.MockTransport ---

def livrer_avec_reponses(codes):
    """Lance livrer() face à un faux partenaire qui renvoie successivement les codes donnés."""
    restants = list(codes)
    stockage = StockageLivraisons()
    stockage.enregistrer_si_nouveau("evt-mock")
    attentes = Attentes()
    transport = httpx.MockTransport(lambda requete: httpx.Response(restants.pop(0)))
    asyncio.run(livrer(evenement("evt-mock"), "http://partenaire/tickets", stockage, attentes, transport))
    return stockage.lire("evt-mock"), attentes.demandees


def test_429_est_relance():
    etat, attentes = livrer_avec_reponses([429, 201])
    assert etat["status"] == "delivered" and etat["attempts"] == 2
    assert attentes == [0.2]


@pytest.mark.parametrize("code", [400, 401, 404, 409, 422])
def test_autres_4xx_sans_relance(code):
    etat, attentes = livrer_avec_reponses([code])
    assert etat == {"event_id": "evt-mock", "status": "quarantine", "attempts": 1}
    assert attentes == []


def test_5xx_puis_succes_a_la_troisieme():
    etat, attentes = livrer_avec_reponses([500, 502, 200])
    assert etat["status"] == "delivered" and etat["attempts"] == 3
    assert attentes == [0.2, 0.4]
