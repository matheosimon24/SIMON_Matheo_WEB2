# SIMON_Matheo_WEB2 – Rattrapage WEB2 (HETIC)

Rattrapage individuel WEB2 de **Mathéo SIMON** sur le cas **MATRiCE** (planning de séances de formation).

Modules attribués : **F2 – Tests front**, **F3 – Bibliothèques UI**, **I3 – Structuration de flux**, **I4 – Webhooks & API tierce**.

Chaque module est un projet **indépendant** : il a ses propres dépendances, ses propres commandes et peut être vérifié sans installer les autres.

## Structure du dépôt

```
SIMON_Matheo_WEB2/
├── README.md            ← ce fichier : prérequis, installation, lancement, tests
├── JUSTIFICATIONS.md    ← choix techniques, alternatives, preuves et limites
├── SOURCES_IA.md        ← déclaration des usages de l'IA et des autres sources
├── f2-tests-front/      ← F2 : composant React testé (Vitest + Testing Library)
├── f3-ui/               ← F3 : vue planning accessible et responsive
├── i3-flux/             ← I3 : pipeline CLI de normalisation NDJSON
├── i4-webhooks/         ← I4 : récepteur de webhooks signés + partenaire simulé
└── preuves/             ← captures, traces de tests avant/après, résultats
```

## Prérequis

- Git
- Node.js 22 ou plus récent, avec npm — modules F2 et F3 (testé avec Node.js 24.20 et npm 11.19)
- Python 3.12 ou plus récent — modules I3 et I4 (testé avec Python 3.14)

## Installation, lancement et tests

Chaque module s'installe et se lance **depuis son propre dossier**. Résumé des commandes de test (détails dans chaque section ci-dessous) :

| Module | Dossier | Installation | Tests / lancement | Résultat attendu |
|---|---|---|---|---|
| F2 | `f2-tests-front` | `npm ci` | `npm test` | 8 tests verts |
| F2 (preuve avant) | `f2-tests-front` | | `npm run test:initial` | 3 tests rouges **attendus** |
| F3 | `f3-ui` | `npm ci` | `npm run dev` | page sur `http://localhost:5173` |
| I3 | `i3-flux` | `python -m venv .venv` puis `pip install -r requirements.txt` | `pytest -v` | 47 tests verts |
| I4 | `i4-webhooks` | `python -m venv .venv` puis `pip install -r requirements.txt` | `pytest -v` | 44 tests verts |

### F2 – Tests front

Petit projet React testable : le composant `PlanningList` du sujet (conservé tel quel), sa version corrigée, un adaptateur d'API simulé et une suite de 8 tests lancée sur les deux versions.

Toutes les commandes se lancent **depuis le dossier `f2-tests-front`** :

```bash
cd f2-tests-front
npm ci
```

`npm ci` installe exactement les versions verrouillées dans `package-lock.json`.

| Commande | Effet |
|---|---|
| `npm test` | Lance les 8 tests sur le **composant corrigé** (non interactif) → 8 verts |
| `npm run test:initial` | Lance les mêmes tests sur le **composant initial** → 3 rouges attendus (preuve des défauts) |
| `npm run dev` | Lance l'interface sur `http://localhost:5173` (choix de la version, simulation de panne) |

**Structure du module :**

```
f2-tests-front/
├── index.html
├── package.json / package-lock.json   ← scripts et dépendances verrouillées
├── vite.config.js                     ← configuration Vite + Vitest (jsdom)
├── vitest.initial.config.js           ← configuration de npm run test:initial
└── src/
    ├── PlanningList.initial.jsx       ← composant du sujet, NON modifié
    ├── PlanningList.jsx               ← composant corrigé
    ├── api/planningApi.js             ← adaptateur d'API simulé (règle A/B + Promotion)
    ├── donnees/seances.js             ← jeu de données du sujet
    ├── App.jsx / main.jsx             ← interface minimale
    ├── setupTests.js                  ← configuration commune des tests
    └── tests/
        ├── suitePlanningList.jsx      ← la suite de 8 tests, écrite une seule fois
        ├── PlanningList.test.jsx      ← suite sur le composant corrigé (npm test)
        └── initial.verif.jsx          ← suite sur le composant initial (npm run test:initial)
```

**Preuves :** [`preuves/f2/`](preuves/f2/) contient la trace des tests rouges avant correction et des tests verts après correction. Le tableau des scénarios et les limites sont dans [JUSTIFICATIONS.md](JUSTIFICATIONS.md#f2--tests-front).

### F3 – Bibliothèques UI

Vue planning simplifiée avec **Tailwind CSS** : en-tête, barre de filtres (groupe, domaine), cartes de séances regroupées par date, badges de domaine et de statut, détail en fenêtre modale et état vide. Utilisable au clavier et lisible de 360 px à 1280 px.

Toutes les commandes se lancent **depuis le dossier `f3-ui`** :

```bash
cd f3-ui
npm ci
npm run dev
```

Ouvrir l'adresse affichée (par défaut `http://localhost:5173`). `npm run build` produit la version de production dans `dist/`.

**Vérifier le rendu à 360 px et 1280 px :** outils développeur (`F12`) → mode appareil (`Ctrl + Maj + M`) → « Dimensions : Responsive » → saisir la largeur.

**Structure du module :**

```
f3-ui/
├── index.html
├── package.json / package-lock.json   ← scripts et dépendances verrouillées
├── vite.config.js                     ← Vite + plugin Tailwind CSS
└── src/
    ├── App.jsx                        ← page : filtres, séances par date, détail
    ├── index.css                      ← import de Tailwind
    ├── libelles.js                    ← libellés lisibles et format de date
    ├── donnees/seances.js             ← données du sujet, formateurs, règle de filtre
    └── composants/
        ├── BarreFiltres.jsx           ← filtres groupe / domaine + compteur annoncé
        ├── CarteSeance.jsx            ← carte d'une séance
        ├── Badges.jsx                 ← badges domaine, statut, période
        ├── DetailSeance.jsx           ← détail en <dialog> modal
        └── EtatVide.jsx               ← message et réinitialisation des filtres
```

**Preuves :** [`preuves/f3/`](preuves/f3/) contient les captures à 360 et 1280 px, le protocole clavier et la mesure de contraste.

### I3 – Structuration de flux

Pipeline en ligne de commande qui transforme `seances.ndjson` (formats variés, doublons, lignes invalides) en un flux propre : **lecture → validation → normalisation → déduplication → sortie**.

Toutes les commandes se lancent **depuis le dossier `i3-flux`** :

```bash
cd i3-flux
```

**Lancer le pipeline** (bibliothèque standard uniquement, aucune installation nécessaire) :

```bash
python pipeline.py donnees/seances.ndjson --sortie sortie
```

Résultat affiché : `{"lus": 12, "acceptes": 6, "rejets": 4, "doublons": 2}`. Les fichiers sont écrits dans `sortie/` :

| Fichier | Contenu |
|---|---|
| `acceptes.ndjson` | séances valides et normalisées, avec `source_line` |
| `rejets.ndjson` | lignes rejetées, avec `source_line`, `motif` et la ligne brute |
| `stats.json` | compteurs `lus`, `acceptes`, `rejets`, `doublons` |

**Lancer les tests** (PowerShell sous Windows) :

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest -v
```

Sous Linux / macOS, remplacer `.\.venv\Scripts\python` par `.venv/bin/python`.

**Structure du module :**

```
i3-flux/
├── pipeline.py          ← le pipeline (CLI)
├── donnees/
│   └── seances.ndjson   ← jeu de données du sujet (12 lignes, dont 1 malformée)
├── tests/
│   └── test_pipeline.py ← 47 tests pytest
├── requirements.txt     ← dépendances de test (versions figées)
├── pytest.ini           ← configuration de pytest
└── .gitattributes       ← fins de ligne LF pour les .ndjson
```

**Preuves :** [`preuves/i3/`](preuves/i3/) contient la sortie réelle du pipeline sur le fichier du sujet et la trace complète des tests.

### I4 – Webhooks & API tierce

Récepteur de webhooks **FastAPI** (signature HMAC, horodatage, taille, validation, déduplication) qui transmet chaque nouvel événement à un **partenaire simulé**, avec timeout, relances et quarantaine.

Toutes les commandes se lancent **depuis le dossier `i4-webhooks`** :

```bash
cd i4-webhooks
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Sous Linux / macOS, remplacer `.\.venv\Scripts\python` par `.venv/bin/python`.

**Lancer les tests** (44 tests, environ 15 s : deux tests attendent réellement les timeouts de 2 s) :

```bash
.\.venv\Scripts\python -m pytest -v
```

**Lancer la démonstration** (3 terminaux) :

```bash
# Terminal 1 – partenaire simulé (mode : ok, flaky, down, slow ou reject)
$env:PARTENAIRE_MODE="flaky"; .\.venv\Scripts\python -m uvicorn partenaire.app:app --port 8001

# Terminal 2 – récepteur
.\.venv\Scripts\python -m uvicorn recepteur.main:app --port 8000

# Terminal 3 – envoi d'un webhook signé, puis suivi de la livraison
.\.venv\Scripts\python scripts\envoyer_webhook.py --event-id evt-demo-1
.\.venv\Scripts\python scripts\envoyer_webhook.py --event-id evt-demo-1                    # doublon -> 200
.\.venv\Scripts\python scripts\envoyer_webhook.py --event-id evt-x --secret mauvais        # -> 401
.\.venv\Scripts\python scripts\envoyer_webhook.py --event-id evt-y --decalage -400         # -> 401
```

Sous Linux / macOS, terminal 1 : `PARTENAIRE_MODE=flaky .venv/bin/python -m uvicorn partenaire.app:app --port 8001`. Les variables reconnues sont listées dans [`.env.example`](i4-webhooks/.env.example).

**Contrat implémenté :**

| Route | Comportement |
|---|---|
| `GET /health` | `200 {"status": "ok"}` |
| `POST /webhooks/planning` | 413 si corps > 64 Ko ; 401 si horodatage à plus de 300 s ou signature invalide ; 400 si corps authentifié invalide ; 202 `duplicate:false` si nouveau ; 200 `duplicate:true` si déjà reçu (sans nouvelle livraison) |
| `GET /deliveries/{event_id}` | `{event_id, status: pending\|delivered\|quarantine, attempts}` ou 404 |
| Partenaire `POST /tickets` | en-tête `Idempotency-Key` ; modes `ok`, `flaky`, `down`, `slow`, `reject` |

**Structure du module :**

```
i4-webhooks/
├── recepteur/
│   ├── main.py          ← application FastAPI (routes, ordre des contrôles)
│   ├── signature.py     ← horodatage + HMAC-SHA256 sur le corps brut
│   ├── validation.py    ← contrat de l'événement et règles métier de la séance
│   ├── stockage.py      ← suivi des livraisons en mémoire
│   └── livraison.py     ← envoi au partenaire : timeout, relances, quarantaine
├── partenaire/app.py    ← partenaire simulé (modes, idempotence)
├── scripts/envoyer_webhook.py ← envoi d'un webhook signé pour la démonstration
├── tests/               ← test_recepteur.py, test_livraison.py, outils.py
├── requirements.txt     ← dépendances aux versions figées
├── pytest.ini
└── .env.example         ← variables d'environnement (sans secret réel)
```

**Preuves :** [`preuves/i4/`](preuves/i4/) contient la trace des 44 tests et les logs réels du récepteur et du partenaire pour les 5 modes.
