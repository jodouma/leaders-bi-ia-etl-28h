# Schémas V7 — édition « Solen BI 22 h »

Seize schémas conceptuels originaux, en français, pour grands débutants. Style Leaders : blanc, marine `#2B3180`, deep `#07152F`, orange `#FF9A3C`, pale `#F3F5FC`, encre `#1A1F4D` ; polices Inter et Plus Jakarta Sans (`authoring/assets/fonts`, SIL OFL 1.1). Aucun schéma n'imite une interface ni une capture d'écran.

Chaque schéma existe en deux formats, dessinés à partir des mêmes coordonnées :

- `docs/images/diagrams/v7-<nom>.svg` : 1600 px de large, glyphes convertis en contours (aucune police requise), avec `<title>` et `<desc>` ;
- `docs/images/diagrams/v7-<nom>.png` : 2400 px de large.

## Régénérer

Depuis la racine du dépôt :

```sh
.venv/bin/python authoring/visuals/generate.py
.venv/bin/python authoring/visuals/generate.py --only v7-etoile v7-cles   # ne réécrit que ces images
```

Dépendances : Python 3.11+, Pillow, fontTools. Le script :

1. dessine les 16 schémas ;
2. échoue si un texte sort de son cadre (largeurs calculées depuis les métriques des polices), chevauche un autre texte, est traversé par un trait ou une flèche, a un contraste WCAG inférieur à 4,5:1 avec son fond, ou fait moins de 26 px (viewBox) ;
3. supprime les anciens `v6-*` de `docs/images/diagrams/` ;
4. écrit la planche `docs/images/diagrams/v7-contact-sheet.png` et `authoring/visuals/manifest.json` (titres, descriptions, dimensions, SHA-256, état des compteurs).

Après une modification, ouvrir la planche et les PNG modifiés pour une inspection visuelle.

## Compteurs de chargement (`v7-chargements`)

Si `authoring/generateurs/v7-data.json` existe au moment de la génération, les compteurs sont lus dans :

```json
{ "chargements": {
    "lot1":  { "lues": 0, "inserees": 0, "rejets": 0, "faits": 0 },
    "lot2":  { "lues": 0, "nouvelles": 0, "deja_connues": 3, "faits": 0 },
    "rejeu": { "lues": 0, "inserees": 0, "faits": 0 } } }
```

Toute valeur absente ou non entière est affichée « n » (aucun chiffre inventé) et listée dans `manifest.json` → `load_counters.placeholders_n`. Exceptions issues du contrat : `lot2.deja_connues` vaut 3 et `rejeu.inserees` vaut 0 par défaut.

## Liste

| Nom | Contenu |
| --- | --- |
| `v7-direction-decision` | Direction → question métier → données → indicateur → décision ; exemple « où passe la marge ? » ; retour à la question si l'indicateur ne répond pas. |
| `v7-codex-controle` | Codex propose → l'étudiant contrôle (diff, verifier, pytest) → le binôme relit (Codex lecture seule + humain) → l'équipe livre. |
| `v7-trois-emplacements` | Mon ordinateur, ordinateur du binôme, GitHub ; commit, push, pull, PR ; aucun lien direct entre ordinateurs. |
| `v7-cycle-pr` | Boucle en 15 étapes, de « main à jour » à « pull », couleurs par acteur (auteur, partenaire, GitHub, les deux). |
| `v7-postes-wsl` | Windows (app Codex, Power BI, PowerShell) / Ubuntu WSL2 (~/solen-bi, Python, Git, agent) / GitHub ; variante Ubuntu natif + poste Windows pour Power BI. |
| `v7-pipeline` | SQLite + CSV + Excel + JSON → ETL en 6 étapes → entrepôt en étoile → app locale + Power BI ; rejets.csv avec motif. |
| `v7-etoile` | dim_date, dim_produit, dim_boutique (SCD2) au centre ; fact_vente et fact_retour ; six relations 1 → *. |
| `v7-cles` | Clé métier NBE vs clés techniques 2 et 5 ; deux versions de Nabeul. |
| `v7-nettoyage` | 6 lignes brutes → 3 acceptées + 1 doublon ignoré + 2 rejets (id_manquant, cle_inconnue) ; formats normalisés. |
| `v7-chargements` | Chargement initial (lot1) → incrément (lot2, 3 lignes connues) → rejeu (0 insertion) ; compteurs « n » ou lus. |
| `v7-scd2-frise` | NBE : v1 Cap Bon [2026-01-01, 2026-07-15), v2 Nord-Est [2026-07-15, NULL) ; ventes du 14 et du 15 juillet. |
| `v7-indicateur-controle` | Ventes nettes après vs avant dédoublonnage ; contrôle : ligne_id distincts = lignes de fact_vente. |
| `v7-tokens-contexte` | Tokens, taille du contexte, effort, quota : une image, quatre définitions. |
| `v7-tache-modele-effort` | Six tâches → GPT-6 Luna (seul modèle annoncé pour Free) → effort (commencer High) → raison → preuve. |
| `v7-seances` | S1–S5 (4 h) avec épisodes Solen, ≈ 8 h personnel, soutenance 2 h ; barre à l'échelle des heures. |
| `v7-soutenance` | 120 min = 10 + 100 + 10 ; N = 5 → 20 min, N = 8 → 12,5 min, N ≥ 11 → 100/11 ≈ 9,1 min : impossible. |

## Licences

Illustrations originales. Polices Inter et Plus Jakarta Sans sous SIL OFL 1.1 : conserver `Inter-OFL.txt` et `PlusJakartaSans-OFL.txt` avec les sources redistribuées.
