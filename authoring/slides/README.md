# Présentation Solen BI 22 h · V7

[Retour au cours](../../README.md)

80 diapositives françaises en 16:9 pour **Langage avancé : IA, Codex et BI — votre première mission chez Solen Digital**. Une idée par diapositive ; les explications détaillées, les sources et leurs dates sont dans les notes du présentateur.

Fichiers produits : `presentation/Solen_CODEX_BI_22h.pptx` (modifiable) et `presentation/Solen_CODEX_BI_22h.pdf` (conversion du même PPTX).

## Plan

| Partie | Contenu | Diapositives |
|---|---|---|
| A | Bienvenue chez Solen Digital : mail de mission, binôme, contrat 22 h, route A → B → C, poste | 1–11 |
| B | Ce que vous saurez faire : dix thèmes, matrice compétence → mission → action → preuve | 12–16 |
| C | Git et GitHub de zéro : trois emplacements, huit mots, cycle de PR, rôles, revue, dépannage | 17–25 |
| D | Codex Free (faits datés du 28/10/2026) : offre, efforts, ressources, fiche tâche, huit habitudes, Skills, quota | 26–37 |
| E | Notions BI avec les chiffres de Maison Zitouna, dont le graphique natif par zone | 38–55 |
| F | Les cinq séances (minutage 240 min), choix de mission, S5 : app, Power BI, recommandation | 56–67 |
| G | Catalogue des dix missions et règles communes | 68–70 |
| H | Soutenance : formule 120 min, script de 6 min, critères publics, questions individuelles | 71–75 |
| I | Sources officielles, licences, clôture | 76–80 |

## Reconstruire

Node.js 18 ou plus récent, `pptxgenjs` 4.0.1, Python 3, LibreOffice pour le PDF. Depuis la racine du cours (`github/`) :

```sh
npm install --prefix authoring/slides
python3 authoring/slides/make_content.py
node authoring/slides/build_slides.js
soffice --headless --convert-to pdf --outdir presentation presentation/Solen_CODEX_BI_22h.pptx
```

- `slides.json` est la source du contenu (titre, mise en page, données, notes par diapositive). On la modifie à la main.
- `make_content.py` **valide** sans rien réécrire : 70 à 90 diapositives, sections A → I dans l'ordre, titre et notes partout, chaque image présente (schémas du manifeste `authoring/visuals/manifest.json`, captures du registre `docs/images/captures/REGISTRE.json` avec la légende « Capture réelle, macOS »), notes datées dans les parties D et I, cinq séances de 240 min avec deux pauses, un seul graphique dont les valeurs égalent `modele-binome/tronc-commun/reference/attendu_lot2.json` (`agregats.par_zone`, ventes nettes en millimes).
- `build_slides.js` écrit le PPTX et `layout_manifest.json` (position et taille de chaque zone de texte). Une image manquante arrête la construction. Aucun téléchargement, aucun appel IA.
- `SOLEN_ASSET_ROOT` peut désigner une autre copie complète du cours ; inutile aux étudiants.

Après chaque modification, régénérer le PDF puis le relire page par page (par exemple `pdftoppm -r 60 -png`), pas une ancienne conversion.

## Ce qui est éditable

Titres, textes, tableaux, cartes, frise de minutage, compteurs de chargement et le graphique « Ventes nettes par zone, après le lot 2 » (graphique PowerPoint natif ; valeurs en millimes, étiquettes au format `40 887,210`) sont des objets PowerPoint. Les 14 schémas `docs/images/diagrams/v7-*.png` et les 2 captures sont des images ; leurs sources sont dans `authoring/visuals/` et `docs/images/`.

Le schéma `v7-chargements.png` n'est pas inséré : il affiche « n » et « 3 déjà connues ». La diapositive « Charger · compléter · rejouer » le redessine en objets natifs avec les compteurs de la référence (lot 2 : 413 lues, 15 déjà chargées, 385 ajoutées ; 2345 faits). Le schéma `v7-tache-modele-effort.png` est remplacé par un tableau natif lisible (il reste dans le livret 03).

## Marque, polices, provenance

- Thème Leaders : marine `#2B3180`, deep `#07152F`, orange `#FF9A3C`, pale `#F3F5FC`. Arial et Courier New dans les objets PowerPoint ; Inter et Plus Jakarta Sans (SIL OFL 1.1) seulement dans les schémas.
- Logos fournis, proportions gardées : Leaders (`authoring/assets/leaders-logo.jpeg`) et Solen Digital. `assets/solen-digital-horizontal-1200.png` est une copie réduite (1200 px, transparence gardée) de `authoring/assets/solen-digital-horizontal.png`, pour alléger le fichier ; sur fond sombre, le logo Solen est posé sur un panneau blanc arrondi. Logos et pied de page sont dans le masque « SOLEN » des diapositives claires.
- Chaque visuel porte son statut : « SCHÉMA · pas une capture » ou « CAPTURE RÉELLE · macOS ». Aucune interface n'est simulée ; il n'y a pas encore de capture Power BI ni de capture Codex Free (prévol Windows Ines/Rayan à venir).
- Chiffres : `modele-binome/tronc-commun/reference/` et `echantillon/attendu.md`, livrets 00–06 (`authoring/content/*.json`), `prompts/README.md`, `modele-binome/powerbi/README.md`, fiches `modele-binome/catalogue/M01…M10/fiche_mission.md`. Faits officiels : `docs/setup/sources.json`, vérifiés le 28/10/2026.

## Limites connues

Contrôles d'édition seulement : construction, validation OOXML, conversion LibreOffice sur macOS et relecture des 80 pages rendues. Ce n'est ni un essai sur un compte Codex Free, ni une manipulation Power BI sous Windows, ni un pilote chronométré : les durées restent des estimations. Le livret 04 (catalogue) n'existait pas encore lors de cette construction ; les diapositives G s'appuient sur les fiches de mission.
