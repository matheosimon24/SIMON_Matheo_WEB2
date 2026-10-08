# F3 – Mesure de contraste

## Méthode

- Page lancée avec `npm run dev`, mesurée dans le navigateur (Chromium).
- Pour chaque élément : couleur du texte et couleur de fond **réellement calculées par le navigateur** (`getComputedStyle`, en remontant les parents jusqu'au premier fond opaque), converties en sRGB.
- Ratio calculé avec la formule WCAG 2.1 : `(L1 + 0,05) / (L2 + 0,05)`, où L1 et L2 sont les luminances relatives de la couleur la plus claire et de la plus foncée.
- Seuils WCAG 2.1 :
  - texte normal : **4,5:1** (AA), 7:1 (AAA) ;
  - grand texte (≥ 24 px, ou ≥ 18,66 px en gras) : 3:1 (AA) ;
  - éléments non textuels (bordures porteuses de sens, contour de focus) : **3:1** (critère 1.4.11).
- Vérification croisée possible avec le WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/) en saisissant les couleurs hexadécimales ci-dessous.

## Résultats

| Élément | Texte | Fond | Ratio | Taille / graisse | Niveau atteint |
|---|---|---|---|---|---|
| Titre `h1` | `#0f172b` | `#ffffff` | **17,83:1** | 30 px / 700 | AAA |
| Sur-titre « MATRiCE » | `#193cb8` | `#ffffff` | **8,82:1** | 14 px / 600 | AAA |
| Description de l'en-tête | `#314158` | `#ffffff` | **10,36:1** | 16 px / 400 | AAA |
| Label de filtre | `#1d293d` | `#ffffff` | **14,62:1** | 14 px / 600 | AAA |
| Texte du filtre (`select`) | `#0f172b` | `#ffffff` | **17,83:1** | 16 px / 400 | AAA |
| Compteur de résultats | `#314158` | `#ffffff` | **10,36:1** | 14 px / 400 | AAA |
| Titre de date `h2` | `#0f172b` | `#f8fafc` | **17,04:1** | 20 px / 700 | AAA |
| Titre de carte `h3` | `#0f172b` | `#ffffff` | **17,83:1** | 18 px / 600 | AAA |
| Intitulé (Domaine, Groupe…) | `#314158` | `#ffffff` | **10,36:1** | 14 px / 400 | AAA |
| Valeur (Groupe A, formateur…) | `#0f172b` | `#ffffff` | **17,83:1** | 14 px / 500 | AAA |
| Bouton « Voir le détail » | `#ffffff` | `#1447e6` | **6,83:1** | 14 px / 600 | AA |
| Badge domaine Web | `#024a70` | `#dff2fe` | **8,24:1** | 14 px / 500 | AAA |
| Badge domaine Data | `#4d179a` | `#ede9fe` | **9,29:1** | 14 px / 500 | AAA |
| Badge domaine Cyber | `#8b0836` | `#ffe4e6` | **8,00:1** | 14 px / 500 | AAA |
| Badge domaine Projet | `#0f172b` | `#e2e8f0` | **14,46:1** | 14 px / 500 | AAA |
| Badge statut « Confirmée » | `#004f3b` | `#ecfdf5` | **9,14:1** | 14 px / 500 | AAA |
| Badge statut « Proposée » | `#7b3306` | `#fffbeb` | **8,73:1** | 14 px / 500 | AAA |
| Badge période (Matin…) | `#1d293d` | `#ffffff` | **14,62:1** | 14 px / 500 | AAA |

### Éléments non textuels (seuil 3:1)

| Élément | Couleur | Fond | Ratio | Résultat |
|---|---|---|---|---|
| Bordure du badge « Confirmée » (pleine) | `#007a55` | `#ffffff` | **5,36:1** | conforme |
| Bordure du badge « Proposée » (pointillée) | `#bb4d00` | `#ffffff` | **5,03:1** | conforme |
| Contour de focus, sur une carte | `#1447e6` | `#ffffff` | **6,83:1** | conforme |
| Contour de focus, sur le fond de page | `#1447e6` | `#f8fafc` | **6,53:1** | conforme |

## Conclusion

Tous les textes dépassent le niveau **AA (4,5:1)** ; tous sauf le bouton bleu atteignent le niveau **AAA (7:1)**. Le bouton (6,83:1) reste largement au-dessus du seuil AA. Les bordures de statut et le contour de focus dépassent le seuil de 3:1 des éléments non textuels.
