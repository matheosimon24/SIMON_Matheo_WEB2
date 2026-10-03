# Justifications techniques

Ce document explique, pour chaque module, les choix techniques réalisés, les alternatives envisagées, les preuves produites et les limites connues.

## F2 – Tests front

### Choix techniques

- **Vitest + Testing Library + jsdom :** Vitest s'intègre directement à Vite (même configuration, même transformation du JSX) ; Testing Library teste le composant comme un utilisateur le perçoit (rôles, noms accessibles, textes) plutôt que son code interne ; jsdom simule le DOM dans Node, sans navigateur.
- **Requêtes par rôle accessible** (`getByRole('combobox', { name: 'Groupe' })`, `getByRole('alert')`, `getByRole('status')`) : si le nom accessible du filtre disparaît, les tests échouent. L'accessibilité est donc vérifiée par tous les tests, pas seulement par le test 7.
- **Promesses pilotées par le test** (`creerLoadSessionsPilote`) : chaque appel à `loadSessions` renvoie une promesse que le test résout ou rejette au moment choisi. On contrôle exactement l'ordre des réponses (indispensable pour le test « désordre »), sans `setTimeout` ni attente réelle : les tests sont rapides et déterministes.
- **Une seule suite, deux composants :** `suitePlanningList.jsx` est une fonction qui reçoit le composant à tester. Elle est lancée sur la version initiale (`npm run test:initial`, rouge attendu) et sur la version corrigée (`npm test`, vert). Les preuves avant/après portent donc exactement sur les mêmes tests.
- **Composant initial conservé sans modification** (`PlanningList.initial.jsx`) pour que la preuve « avant » reste reproductible à tout moment.
- **Dépendances verrouillées :** versions exactes dans `package.json` et `package-lock.json` versionné ; `npm ci` réinstalle exactement le même arbre de dépendances.

### Défauts trouvés et corrections

| Défaut du composant initial | Test qui le détecte | Correction minimale |
|---|---|---|
| **Échec réseau non géré :** pas de `.catch()`, `setLoading(false)` n'est jamais appelé → « Chargement… » affiché pour toujours, aucun moyen de réessayer, rejet de promesse non géré | Test 5 | `.catch()` qui mémorise l'erreur, `.finally()` qui arrête le chargement, message `role="alert"` et bouton « Réessayer » (compteur `tentative` dans les dépendances de l'effet) |
| **Réponses dans le désordre (race condition) :** une réponse lente d'un ancien filtre écrase la réponse du filtre actuel → le filtre affiche « B » mais la liste montre A | Test 6 | Drapeau `ignore` passé à `true` par la fonction de nettoyage de `useEffect` : une réponse obsolète est ignorée (technique recommandée par la documentation React) |
| **Résultat vide muet :** liste vide sans explication, impossible de distinguer « rien à afficher » d'un problème | Test 4 | Message « Aucune séance pour ce groupe. » |

### Tableau des scénarios

| # | Scénario | Entrée | Attente | Risque couvert |
|---|---|---|---|---|
| 1 | Chargement | Requête initiale en attente | `role="status"` « Chargement… » affiché ; `loadSessions` appelé avec `{ group: 'all' }` | L'utilisateur ne sait pas que des données arrivent ; mauvais paramètre envoyé à l'API |
| 2 | Succès | La requête renvoie les 6 séances | Les 6 titres sont affichés dans l'ordre ; le chargement disparaît | Données non affichées ou chargement qui reste affiché |
| 3 | Groupe A inclut Promotion | Choix « Groupe A » avec l'adaptateur réel | s01, s03, s04, s06 affichées ; s02 et s05 (groupe B) absentes | Règle métier « A affiche A + Promotion » cassée ; séances de B visibles par A |
| 4 | Résultat vide | La requête renvoie `[]` | Message « Aucune séance… » ; pas de chargement | Écran vide sans explication |
| 5 | Erreur puis nouvelle tentative | 1re requête rejetée, puis clic sur « Réessayer », 2e requête réussie | `role="alert"` « Impossible de charger… » ; chargement arrêté ; 2e appel à `loadSessions` ; séances affichées et erreur retirée | Chargement infini, erreur silencieuse, aucune reprise possible |
| 6 | Réponses dans le désordre | Choix A puis B ; la réponse B arrive avant la réponse A | Filtre sur « B » et liste de B (+ Promotion), la réponse A est ignorée | Liste incohérente avec le filtre affiché (réponse obsolète) |
| 7 | Nom accessible du filtre | Rendu initial | `combobox` nommé « Groupe » avec les options Tous, Groupe A, Groupe B, Promotion | Filtre inutilisable avec un lecteur d'écran |
| 8 | Utilisation au clavier | Tab, puis choix de « Promotion » sur l'élément qui a le focus | Le filtre reçoit le focus ; `loadSessions` appelé avec `Promotion` ; le focus reste sur le filtre | Filtre inaccessible au clavier ; focus perdu après le changement |

Résultat : version initiale **3 rouges (4, 5, 6) / 5 verts** ; version corrigée **8 verts**.

### Protocole clavier manuel (navigateur)

Le test 8 ne peut pas simuler l'ouverture native d'un `<select>` (voir limites). Vérification manuelle avec `npm run dev`, version « Corrigée » :

1. `Tab` jusqu'au filtre « Groupe » → contour de focus visible sur le filtre.
2. `Flèche bas` → la valeur passe à « Groupe A » et le chargement se relance.
3. `Alt + Flèche bas` → la liste des options s'ouvre ; `Flèches` puis `Entrée` → option choisie.
4. Panne simulée cochée : `Tab` atteint le bouton « Réessayer », `Entrée` relance le chargement.

### Alternatives envisagées

- **Jest** : très répandu, mais demande une configuration supplémentaire (Babel) pour le JSX et les modules ES dans un projet Vite. Vitest réutilise la configuration de Vite.
- **Faux minuteurs (`vi.useFakeTimers`) avec l'adaptateur à délais** pour le test du désordre : possible, mais plus fragile et moins lisible que des promesses résolues explicitement dans l'ordre voulu.
- **MSW (Mock Service Worker)** pour simuler le réseau : utile avec un vrai `fetch`, inutile ici puisque le composant reçoit `loadSessions` en paramètre (injection de dépendance).
- **`AbortController`** pour annuler la requête obsolète au lieu de l'ignorer : meilleur pour le réseau, mais il faudrait changer la signature de `loadSessions` (signal) ; le drapeau `ignore` est la correction la plus petite.
- **Tests de bout en bout (Playwright)** : testeraient le vrai navigateur et le vrai clavier, mais sont hors du périmètre d'un petit projet de tests de composant.

### Preuves

- `preuves/f2/avant-tests-rouges.txt` : `npm run test:initial`, 3 tests rouges et le rejet de promesse non géré.
- `preuves/f2/apres-tests-verts.txt` : `npm test`, 8 tests verts.
- Reproductibles à tout moment avec les deux commandes ci-dessus.

### Limites de la stratégie

- **jsdom n'est pas un vrai navigateur :** pas de rendu visuel, pas de comportement natif du `<select>` au clavier (flèches), pas de contour de focus. Le clavier est donc vérifié en partie par les tests (Tab, focus conservé) et en partie à la main (protocole ci-dessus).
- **Le réseau est simulé :** les tests vérifient la réaction du composant aux promesses, pas les vrais cas réseau (délai d'expiration, requête annulée, réponse mal formée).
- **La requête obsolète n'est pas annulée**, seulement ignorée : elle consomme toujours du réseau.
- **La nouvelle tentative est manuelle** (bouton) : pas de relance automatique.
- **Les tests dépendent des textes** (« Chargement », « Aucune séance », « Impossible de charger ») : changer un libellé oblige à mettre à jour les tests.
- **Le test 3 valide la règle A + Promotion de l'adaptateur**, puisque c'est lui qui filtre ; le composant se contente d'afficher ce qu'il reçoit.

## F3 – Bibliothèques UI

- **Choix techniques :** *à compléter*
- **Alternatives envisagées :** *à compléter*
- **Preuves :** *à compléter*
- **Limites :** *à compléter*

## I3 – Structuration de flux

### Choix techniques

- **Python, bibliothèque standard uniquement** (`json`, `re`, `datetime`, `argparse`) : aucune dépendance à installer pour lancer le pipeline. `pytest` ne sert qu'aux tests.
- **Ordre des étapes imposé par le sujet :** lecture → validation → normalisation → déduplication → sortie. La validation se fait **avant** la déduplication : une ligne invalide ne « réserve » jamais un `id`, c'est la première occurrence **valide** qui est retenue (testé par `test_validation_avant_deduplication`).
- **Une ligne en erreur n'interrompt pas les suivantes :** chaque erreur (JSON malformé, encodage, valeur invalide) est attrapée, transformée en rejet avec motif, et le traitement continue.
- **Vérification du type avant la valeur :** la fonction `est_parmi()` vérifie qu'une valeur est un texte avant de la chercher dans la liste des valeurs autorisées. Sans ce contrôle, une liste ou un objet JSON à la place d'un texte (ex. `"period": []`) provoquait une `TypeError` qui arrêtait tout le pipeline ; c'est désormais un rejet comme un autre (testé par `test_valeur_non_textuelle_rejetee_sans_planter`).
- **Motifs de rejet détaillés :** toutes les erreurs d'une même ligne sont rassemblées dans le motif (ex. `période invalide : 'soir'`). La ligne brute est ajoutée dans `rejets.ndjson` pour pouvoir corriger la source sans la rouvrir.
- **Règles métier vérifiées après les champs :** « AUTO exige teacherId null + proposed » et « confirmed exige un formateur » ne sont testées que si les champs concernés sont eux-mêmes valides, pour éviter des motifs en cascade.
- **Indépendance vis-à-vis du fuseau horaire :** les dates sont validées avec `datetime.date`, qui représente une date de calendrier sans heure ni fuseau. `2026-02-30` est rejetée car `date(2026, 2, 30)` lève une erreur. Aucune fonction dépendant de l'heure locale n'est utilisée.
- **Même fichier = même résultat :** le traitement est déterministe (ordre du fichier conservé, ordre des champs fixé, pas d'horodatage dans les sorties) et les fichiers sont écrits en UTF-8 avec des fins de ligne `\n` quel que soit le système. Le fichier d'entrée est lu en binaire : BOM et fins de ligne CRLF (Windows) sont gérés et donnent le même résultat.
- **Invariant vérifié dans le code :** `lus = acceptes + rejets + doublons` est contrôlé par un `assert` avant l'écriture de `stats.json`.
- **Les doublons ne sont pas écrits dans `rejets.ndjson` :** ce sont des lignes valides, comptées à part dans `stats.json`, conformément à l'invariant du sujet.

### Usage mémoire

Le fichier est lu **ligne par ligne** et `traiter_flux()` est un **générateur** : chaque ligne est traitée puis écrite immédiatement dans le fichier de sortie, sans être accumulée. La seule donnée qui grandit avec le fichier est l'**ensemble des `id` déjà acceptés** (nécessaire à la déduplication). La mémoire utilisée est donc proportionnelle au nombre d'`id` distincts, et non à la taille du fichier : un fichier de plusieurs Go de séances se traite sans le charger entièrement.

### Alternatives envisagées

- **Charger tout le fichier** (`readlines()` ou pandas) : plus simple à écrire, mais la mémoire grandit avec la taille du fichier, et une seule ligne malformée fait échouer `pandas.read_json(lines=True)` en entier. Rejeté.
- **Bibliothèque de validation (Pydantic)** : pratique pour décrire un schéma, mais ajoute une dépendance et des messages d'erreur moins maîtrisés pour un besoin limité à 9 champs. Les règles explicites en Python restent courtes et faciles à expliquer.
- **Dédupliquer avant de valider** : contraire au sujet, et une ligne invalide pourrait faire perdre la version valide d'une séance.
- **Écrire les doublons dans un fichier `doublons.ndjson`** : possible pour la traçabilité, mais non demandé ; les doublons sont comptés dans `stats.json`.

### Preuves

- `preuves/i3/sortie/` : sortie réelle du pipeline sur le fichier du sujet (`acceptes.ndjson`, `rejets.ndjson`, `stats.json`).
- `preuves/i3/execution.txt` : statistiques affichées par la commande (`12 = 6 + 4 + 2`).
- `preuves/i3/tests.txt` : trace des 47 tests pytest, tous verts.
- Résultat détaillé : acceptés s01, s02, s03, s04, s05, s06 ; rejetés bad1 (titre vide), bad2 (date inexistante), bad3 (période « soir »), bad4 (JSON malformé) ; doublons lignes 4 (s01) et 10 (s02).

### Limites

- L'ensemble des `id` vus reste en mémoire : pour des centaines de millions d'`id`, il faudrait une structure externe (base, fichier trié).
- Les valeurs sont comparées de façon stricte : `Matin` ou `PM` en majuscules sont rejetés, faute de règle dans le sujet.
- Le domaine est seulement vérifié comme texte non vide, le sujet ne fixant pas de liste fermée.
- Les champs supplémentaires éventuels sont ignorés en sortie (seuls les 9 champs attendus sont conservés).
- Le pipeline n'est pas reprenable : en cas d'arrêt brutal, il faut le relancer depuis le début (sans risque, puisque le résultat est déterministe).

## I4 – Webhooks & API tierce

- **Choix techniques :** *à compléter*
- **Alternatives envisagées :** *à compléter*
- **Preuves :** *à compléter*
- **Limites :** *à compléter*
