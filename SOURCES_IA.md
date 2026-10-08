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

- **Fichiers concernés :** tout le dossier `f2-tests-front/` (sauf `PlanningList.initial.jsx`, recopié du sujet), `preuves/f2/`, section F2 du README et de JUSTIFICATIONS.md
- **Requêtes représentatives :**
  - Mise en place d'un projet React + Vite + Vitest minimal avec dépendances verrouillées
  - Écriture d'une suite de tests couvrant les 6 scénarios du sujet, le nom accessible et le clavier, réutilisable sur les deux versions du composant
  - Correction minimale du composant pour faire passer les tests
- **Ce que l'IA a produit :** la configuration du projet, l'adaptateur simulé, la suite de tests, le composant corrigé, l'interface de comparaison et une première version de la documentation.
- **Adaptations :** découpage en branches (initialisation, tests, correction, documentation) pour que l'historique montre les tests rouges **avant** la correction ; documentation en français ; choix dans l'interface entre la version initiale et la version corrigée pour la démonstration.
- **Vérifications :**
  - `npm run test:initial` lancé par moi-même : 3 tests rouges, dont j'ai lu et compris les messages (attendu / reçu) ;
  - `npm test` après correction : 8 tests verts ;
  - comparaison des deux versions dans le navigateur (panne simulée, changement rapide de filtre) ;
  - comparaison ligne à ligne entre la version initiale et la version corrigée pour vérifier que la correction reste minimale.

### F3 – Bibliothèques UI

- **Fichiers concernés :** tout le dossier `f3-ui/`, `preuves/f3/contraste.md`, `preuves/f3/protocole-clavier.md`, section F3 du README et de JUSTIFICATIONS.md
- **Requêtes représentatives :**
  - Mise en place d'un projet React + Vite + Tailwind CSS v4
  - Réalisation de la vue planning (filtres, cartes, badges, détail modal, état vide) en respectant l'accessibilité demandée
  - Mesure des contrastes des couleurs utilisées et rédaction d'un protocole clavier
- **Ce que l'IA a produit :** le code de l'interface, le calcul des contrastes dans le navigateur, le protocole clavier et une première version de la documentation.
- **Adaptations :** choix de Tailwind plutôt que MUI pour garder des éléments natifs ; ajout d'un filtre « Domaine » pour rendre l'état vide atteignable ; documentation en français.
- **Vérifications :**
  - test dans le navigateur à 1280 px et 360 px (pas de défilement horizontal à 360 px) ;
  - parcours clavier : ouverture du détail, focus sur « Fermer », fermeture par Échap et retour du focus vérifiés par l'élément actif du navigateur ;
  - protocole clavier refait par moi-même et coché dans `preuves/f3/protocole-clavier.md` ;
  - captures d'écran réalisées par moi-même dans les outils développeur ;
  - ratios de contraste calculés à partir des couleurs réellement rendues par le navigateur.

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
  - lancement de la suite de tests (47 tests verts) ;
  - relecture du code fonction par fonction ;
  - test de cas non prévus par le sujet : une valeur de type liste (`"period": []`) faisait planter le pipeline. Le défaut a été corrigé (contrôle du type avant la valeur) et couvert par un nouveau test.

### I4 – Webhooks & API tierce

*À compléter.*

## Autres sources

*À compléter (documentation officielle consultée, etc.).*
