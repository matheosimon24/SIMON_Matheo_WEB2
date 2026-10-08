# F3 – Protocole clavier

Page lancée avec `npm run dev` (dossier `f3-ui`), souris non utilisée. Tester à 1280 px puis à 360 px (outils développeur, mode appareil).

| # | Action | Résultat attendu | Observé (cocher ✅ ou noter l’écart) |
|---|---|---|---|
| 1 | `Tab` depuis le haut de la page | Le focus arrive sur le filtre « Groupe », avec un contour bleu épais visible | ✅ |
| 2 | `Tab` | Le focus passe au filtre « Domaine » | ✅ |
| 3 | Sur « Groupe » : `Alt + Flèche bas`, choisir « Promotion » avec les flèches, `Entrée` | La liste se met à jour (2 séances) ; le compteur indique « 2 séances affichées » | ✅ |
| 4 | Sur « Domaine » : choisir « Cyber » | État vide « Aucune séance ne correspond à ces filtres » | ✅ |
| 5 | `Tab` jusqu'à « Réinitialiser les filtres », `Entrée` | Les 6 séances réapparaissent, les filtres reviennent à « Tous » | ✅ |
| 6 | `Tab` jusqu'au premier « Voir le détail », `Entrée` | La fenêtre de détail s'ouvre ; le focus est sur « Fermer » | ✅ |
| 7 | `Tab` plusieurs fois dans la fenêtre | Le focus n'atteint jamais un élément de la page derrière la fenêtre (page rendue inerte) ; il peut passer à la barre d'adresse du navigateur puis revenir sur « Fermer » | ✅ |
| 8 | `Échap` | La fenêtre se ferme ; le focus revient sur le bouton « Voir le détail » de la même carte | ✅ |
| 9 | `Entrée` à nouveau, puis `Entrée` sur « Fermer » | La fenêtre se ferme ; le focus revient sur le même bouton | ✅ |
| 10 | `Tab` / `Maj + Tab` sur toute la page | Ordre logique : filtres, puis cartes de gauche à droite et de haut en bas ; aucun élément sauté | ✅ |

Vérifications automatisées complémentaires (dans le navigateur, via `document.activeElement`) :
- après l'étape 6 : élément actif = bouton « Fermer », `dialog` ouvert en mode modal (`:modal`) ;
- après l'étape 8 : élément actif = « Voir le détail de « React composants » », plus de `dialog` dans la page.

## Noms accessibles vérifiés

| Élément | Nom accessible |
|---|---|
| Filtre groupe | « Groupe » (label associé par `for` / `id`) |
| Filtre domaine | « Domaine » |
| Zone de filtres | rôle `search`, « Filtres du planning » |
| Bouton d'une carte | « Voir le détail de « React composants » » (texte caché `sr-only`) |
| Fenêtre de détail | titre de la séance (`aria-labelledby`), description = explication du statut (`aria-describedby`) |
| Badge de statut | « Statut : Confirmée » (icône masquée avec `aria-hidden`) |
