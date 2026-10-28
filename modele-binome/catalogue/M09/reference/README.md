# Référence — Mission 09 (Scène Libre)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Billets vendus | 2345 | 2757 | `billets_vendus` |
| Billets remboursés | 208 | 268 | `billets_rembourses` |
| Billets nets | 2137 | 2489 | `billets_nets` |
| Taux de remplissage | 34,92 % | 32,12 % | `taux_remplissage` |
| Recettes des billets | 109 897,000 TND | 129 085,000 TND | `recettes_billets_millimes` |
| Remboursements | 9 880,000 TND | 12 928,000 TND | `remboursements_millimes` |
| Frais de distribution | 5 346,945 TND | 6 290,070 TND | `frais_distribution_millimes` |
| Recettes nettes | 94 670,055 TND | 109 866,930 TND | `recettes_nettes_millimes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_evenement` | 14 | 17 |
| `dim_canal` | 4 | 5 |
| `fact_billet` | 2345 | 2757 |
| `fact_remboursement` | 208 | 268 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 6 | 2 |
| **total** | 25 | 10 |

## Historique (dim_canal) après le dernier lot

| Clé métier | frais_pour_mille | valid_from | valid_to |
|---|---|---|---|
| GUI | 0 | 2025-09-01 | (courante) |
| PAR | 60 | 2025-11-15 | (courante) |
| REV | 90 | 2025-09-01 | 2026-07-15 |
| REV | 110 | 2026-07-15 | (courante) |
| WEB | 45 | 2025-09-01 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/recettes_nettes_par_mois_et_type.png` · `visuels/recettes_nettes_par_mois_et_type.svg`
- `visuels/taux_remplissage_par_evenement.png` · `visuels/taux_remplissage_par_evenement.svg`
- `visuels/recettes_nettes_et_remboursements_par_type.png` · `visuels/recettes_nettes_et_remboursements_par_type.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`

## À savoir pour M09

- La vue d'analyse ajoute **une ligne « capacité » par événement** (canal `(capacité)`) : c'est elle qui donne le dénominateur du taux de remplissage. Par canal, ce taux est vide (`null`) : la capacité d'une salle ne dépend d'aucun canal.
- L'axe `par_mois` = mois de la **date de l'événement** (date du spectacle après report), pas de la vente.
- Dans `scd2.versions`, `attribut` (frais en pour mille) est écrit en texte (`"90"`) ; dans `scd2.frontieres`, il reste un entier (`90`). Le vérificateur compare l'attribut en texte des deux côtés. La colonne `frais_pour_mille` de l'entrepôt est bien un INTEGER.
- Événements annulés : `EV05` (le 2026-04-10, lot 1) et `EV12` (le 2026-07-18, lot 2) ; tous leurs billets sont remboursés. `EV08` est reporté au 2026-07-11 : seules les demandes `REMBOURSE` comptent.
