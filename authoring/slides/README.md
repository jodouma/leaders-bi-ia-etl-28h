# Présentation Solen BI 22 h · V7

[Retour au cours](../../README.md)

87 diapositives françaises en 16:9 pour **Langage avancé : IA, Codex et BI — votre première mission chez Solen Digital**. Une idée par diapositive ; les explications détaillées, les sources et leurs dates sont dans les notes du présentateur.

Fichiers produits : `presentation/Solen_CODEX_BI_22h.pptx` (modifiable) et `presentation/Solen_CODEX_BI_22h.pdf` (conversion du même PPTX).

## Plan

| Partie | Contenu | Diapositives |
|---|---|---|
| A | Bienvenue chez Solen Digital : mail de mission, binôme, contrat 22 h, route A → B → C, poste (WSL2 puis Ubuntu natif) | 1–12 |
| B | Ce que vous saurez faire : dix thèmes, matrice compétence → mission → action → preuve | 13–17 |
| C | Git et GitHub de zéro : trois emplacements, huit mots, cycle de PR en deux diapositives, rôles (PR n°1 par A, PR n°2 par B dès S1), revue, dépannage, les deux « workflows » (gestes humains / GitHub Actions) | 18–27 |
| D | Codex Free (faits datés du 28/10/2026) : offre, efforts, ressources, fiche tâche en deux diapositives, huit habitudes, Skills, quota | 28–40 |
| E | Notions BI avec les chiffres de Maison Zitouna (nettoyage en deux diapositives), dont le graphique natif par zone | 41–59 |
| F | Séance 0 chez soi (≈ 2 h), les cinq séances (minutage 240 min : S1 ouvre sur 30 min de vérification des postes, S4 finit par 50 min « Passer à votre mission », S5 commence par la mission), de la fin de S3 à la soutenance avec les ≈ 8 h personnelles (2 + 4 + 2), app (trois captures recadrées), Power BI, recommandation | 60–72 |
| G | Catalogue des dix missions (deux diapositives de cinq) et règles communes | 73–76 |
| H | Soutenance : formule 120 min en deux diapositives, script de 6 min, critères publics, questions individuelles | 77–82 |
| I | Sources officielles (titres seuls, adresses dans les notes), licences, clôture | 83–87 |

## Lisibilité (revue visuelle du 28/10/2026)

- Schémas et captures en pleine largeur : `build_slides.js` refuse un schéma sous 85 % de la largeur de la diapositive et une capture sous 80 %. Le champ `crop` de `slides.json` ([gauche, haut, droite, bas] en pixels de l'image source) cadre la zone utile : le titre interne du schéma, qui répète celui de la diapositive, est retiré ; un schéma trop haut est montré en deux diapositives. Les images sources ne sont pas modifiées.
- Les puces qui ne tiennent plus sous un schéma sont dans les notes (« Points à dire : … ») ; `takeaway` affiche une phrase sous le schéma quand la place le permet.
- Aucun texte de contenu sous 14 pt ; seuls le pied de page et le numéro de diapositive sont à 12 pt.
- Minutages (décisions pédagogiques V7 du 28/10/2026, D1–D2) : la répartition explications / pratique de chaque séance est écrite dans le champ `split` de la diapositive de séance (S1 58/162, S2 et S3 66/154, S4 50/170, S5 35/185) ; la barre est proportionnelle aux minutes.

## Reconstruire

Node.js 18 ou plus récent, `pptxgenjs` 4.0.1, Python 3, LibreOffice pour le PDF. Depuis la racine du cours (`github/`) :

```sh
npm install --prefix authoring/slides
python3 authoring/slides/make_content.py
node authoring/slides/build_slides.js
soffice --headless --convert-to pdf --outdir presentation presentation/Solen_CODEX_BI_22h.pptx
```

- `slides.json` est la source du contenu (titre, mise en page, données, notes par diapositive). On la modifie à la main.
- `make_content.py` **valide** sans rien réécrire : 70 à 100 diapositives, sections A → I dans l'ordre, titre et notes partout, chaque image présente (schémas du manifeste `authoring/visuals/manifest.json`, captures du registre `docs/images/captures/REGISTRE.json` avec la légende « Capture réelle, macOS »), notes datées dans les parties D et I, cinq séances de 240 min avec deux pauses, un seul graphique dont les valeurs égalent `modele-binome/tronc-commun/reference/attendu_lot2.json` (`agregats.par_zone`, ventes nettes en millimes).
- `build_slides.js` écrit le PPTX et `layout_manifest.json` (position et taille de chaque zone de texte). Une image manquante arrête la construction. Aucun téléchargement, aucun appel IA.
- `SOLEN_ASSET_ROOT` peut désigner une autre copie complète du cours ; inutile aux étudiants.

Après chaque modification, régénérer le PDF puis le relire page par page (par exemple `pdftoppm -r 60 -png`), pas une ancienne conversion.

## Ce qui est éditable

Titres, textes, tableaux, cartes, frise de minutage, compteurs de chargement et le graphique « Ventes nettes par zone, après le lot 2 » (graphique PowerPoint natif ; valeurs en millimes, étiquettes au format `40 887,210`) sont des objets PowerPoint. Les 14 schémas `docs/images/diagrams/v7-*.png` et les 2 captures sont des images, recadrées à l'affichage (`crop`) ; leurs sources sont dans `authoring/visuals/` et `docs/images/`.

Le schéma `v7-chargements.png` n'est pas inséré : il affiche « n » et « 3 déjà connues ». La diapositive « Charger · compléter · rejouer » le redessine en objets natifs avec les compteurs de la référence (lot 2 : 413 lues, 15 déjà chargées, 385 ajoutées ; 2345 faits). Le schéma `v7-tache-modele-effort.png` est remplacé par un tableau natif lisible (il reste dans le livret 03).

## Marque, polices, provenance

- Thème Leaders : marine `#2B3180`, deep `#07152F`, orange `#FF9A3C`, pale `#F3F5FC`. Arial et Courier New dans les objets PowerPoint ; Inter et Plus Jakarta Sans (SIL OFL 1.1) seulement dans les schémas.
- Logos fournis, proportions gardées : Leaders (`authoring/assets/leaders-logo.jpeg`) et Solen Digital. `assets/solen-digital-horizontal-1200.png` est une copie réduite (1200 px, transparence gardée) de `authoring/assets/solen-digital-horizontal.png`, pour alléger le fichier ; sur fond sombre, le logo Solen est posé sur un panneau blanc arrondi. Logos et pied de page sont dans le masque « SOLEN » des diapositives claires.
- Chaque visuel porte son statut : « SCHÉMA · pas une capture » ou « CAPTURE RÉELLE · macOS ». Aucune interface n'est simulée ; il n'y a pas encore de capture Power BI ni de capture Codex Free (prévol Windows Ines/Rayan à venir).
- Chiffres : `modele-binome/tronc-commun/reference/` et `echantillon/attendu.md`, livrets 00–06 (`authoring/content/*.json`), `prompts/README.md`, `modele-binome/powerbi/README.md`, fiches `modele-binome/catalogue/M01…M10/fiche_mission.md`. Faits officiels : `docs/setup/sources.json`, vérifiés le 28/10/2026.

## Limites connues

Contrôles d'édition seulement : construction, validation OOXML, conversion LibreOffice sur macOS et relecture des 87 pages rendues (planches à 30 dpi, gros plans à 80 dpi). Ce n'est ni un essai sur un compte Codex Free, ni une manipulation Power BI sous Windows, ni un pilote chronométré : les durées restent des estimations. Les diapositives G s'appuient sur les fiches de mission (`catalogue/M0x/fiche_mission.md`), reprises dans le livret 04. Le schéma `v7-seances.png` (diapositive 7) date d'avant la séance 0 et le nouveau minutage de S4–S5 : les notes de la diapositive donnent la version à jour, le schéma reste à régénérer dans `authoring/visuals/`.
