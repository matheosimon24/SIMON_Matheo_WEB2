# Justifications techniques

Ce document explique, pour chaque module, les choix techniques réalisés, les alternatives envisagées, les preuves produites et les limites connues.

## F2 – Tests front

- **Choix techniques :** *à compléter*
- **Alternatives envisagées :** *à compléter*
- **Preuves :** *à compléter*
- **Limites :** *à compléter*

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
- `preuves/i3/tests.txt` : trace des 32 tests pytest, tous verts.
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
