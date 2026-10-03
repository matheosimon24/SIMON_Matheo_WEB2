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

> Les dossiers des modules sont ajoutés au fur et à mesure de l'avancement.

## Prérequis

- Git
- Node.js (version LTS) et npm — modules F2 et F3
- Python 3.12 ou plus récent — modules I3 et I4

## Installation, lancement et tests

*À compléter pour chaque module au fur et à mesure.*

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

*À venir.*

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

*À venir.*
