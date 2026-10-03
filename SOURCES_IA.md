# Sources et usages de l'IA

Ce document déclare, comme demandé par le sujet, les usages de l'intelligence artificielle et des autres sources pendant le rattrapage : outil utilisé, fichiers concernés, requêtes représentatives, adaptations faites et vérifications réalisées.

L'IA a été utilisée comme assistant. Le code et les choix techniques ont été relus, compris et vérifiés personnellement.

## Outil utilisé

- **Claude (Claude Code, Anthropic)** — assistant de développement.

## Usages par étape

### Organisation du projet

- **Fichiers concernés :** `README.md`, `JUSTIFICATIONS.md`, `SOURCES_IA.md`, `.gitignore`
- **Requêtes représentatives :**
  - Analyse du sujet PDF et proposition d'un plan de travail étape par étape
  - Choix entre un dépôt unique et plusieurs dépôts pour les 4 modules
- **Ce que l'IA a produit :** une analyse du sujet, un planning, une proposition de structure de dépôt (un dépôt unique, un dossier par module) et les squelettes des fichiers de documentation.
- **Adaptations :** documentation et messages de commit en français ; commits réalisés par moi-même.
- **Vérifications :** relecture de la structure par rapport aux consignes de rendu du sujet (page 2) et à la checklist (page 10).

### F2 – Tests front

*À compléter.*

### F3 – Bibliothèques UI

*À compléter.*

### I3 – Structuration de flux

- **Fichiers concernés :** `i3-flux/donnees/seances.ndjson`, `i3-flux/pipeline.py`, `i3-flux/tests/test_pipeline.py`, `i3-flux/requirements.txt`, `i3-flux/pytest.ini`, `i3-flux/.gitattributes`, section I3 du README et de JUSTIFICATIONS.md, `preuves/i3/`
- **Requêtes représentatives :**
  - Transcription des deux tableaux du sujet en fichier NDJSON, en conservant volontairement les valeurs à normaliser
  - Écriture du pipeline CLI en Python (lecture ligne par ligne, validation, normalisation, déduplication, sorties)
  - Écriture des tests pytest couvrant les cas demandés (valide, invalide, doublon, JSON malformé, fichier vide)
- **Ce que l'IA a produit :** le fichier de données, le code du pipeline, les tests et une première version de la documentation du module.
- **Adaptations :** découpage en étapes avec une branche Git par étape (données, pipeline, tests, documentation) ; messages et documentation en français ; choix de Python pour rester cohérent avec le module I4.
- **Vérifications :**
  - résultat attendu déduit des règles du sujet, ligne par ligne (12 lus = 6 acceptés + 4 rejets + 2 doublons), puis comparé à la sortie réelle ;
  - exécution du pipeline par moi-même depuis le terminal ;
  - lancement de la suite de tests (32 tests verts) ;
  - relecture du code fonction par fonction.

### I4 – Webhooks & API tierce

*À compléter.*

## Autres sources

*À compléter (documentation officielle consultée, etc.).*
