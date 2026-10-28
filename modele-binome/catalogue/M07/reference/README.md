# Référence — Mission 07 (FibreNet)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Abonnés actifs fin de mois | 1657 | 2226 | `actifs_fin_mois` |
| MRR (revenu mensuel récurrent) | 128 465,800 TND | 174 124,300 TND | `mrr_millimes` |
| Départs du mois | 31 | 44 | `departs` |
| Taux de départ | 1,89 % | 2,00 % | `taux_depart` |
| Abonnés actifs début de mois | 1641 | 2204 | `actifs_debut_mois` |
| Nouveaux abonnements | 47 | 66 | `nouveaux` |
| Montant facturé | 130 560,900 TND | 176 825,400 TND | `facture_millimes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_compte` | 205 | 217 |
| `dim_offre` | 5 | 6 |
| `fact_facture` | 1688 | 2270 |
| `fact_abonnement_mois` | 1688 | 2270 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 9 | 7 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 5 | 2 |
| **total** | 25 | 13 |

## Historique (dim_offre) après le dernier lot

| Clé métier | gamme | valid_from | valid_to |
|---|---|---|---|
| FN-F100 | confort | 2023-06-01 | (courante) |
| FN-F20 | essentiel | 2023-01-02 | (courante) |
| FN-F300 | confort | 2024-03-01 | 2026-07-15 |
| FN-F300 | pro | 2026-07-15 | (courante) |
| FN-F50 | essentiel | 2023-01-02 | (courante) |
| FN-PRO1G | pro | 2024-09-02 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/mrr_par_mois_et_gamme.png` · `visuels/mrr_par_mois_et_gamme.svg`
- `visuels/actifs_fin_de_mois.png` · `visuels/actifs_fin_de_mois.svg`
- `visuels/nouveaux_et_departs_par_mois.png` · `visuels/nouveaux_et_departs_par_mois.svg`
- `visuels/taux_depart_par_mois.png` · `visuels/taux_depart_par_mois.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`

## Lecture mois par mois (après le dernier lot)

Les abonnés et le MRR sont des stocks de fin de mois. Les totaux « Indicateurs » ci-dessus additionnent les mois (abonnés-mois, MRR cumulé) : pour un mois, lisez ce tableau (agrégat `par_mois`).

| Mois | Actifs début | Nouveaux | Départs | Actifs fin | Taux de départ | MRR | Facturé |
|---|---|---|---|---|---|---|---|
| 2026-01 | 265 | 9 | 4 | 270 | 1,51 % | 20 765,200 TND | 20 994,800 TND |
| 2026-02 | 270 | 6 | 3 | 273 | 1,11 % | 21 253,100 TND | 21 382,800 TND |
| 2026-03 | 273 | 11 | 11 | 273 | 4,03 % | 21 193,100 TND | 22 160,200 TND |
| 2026-04 | 273 | 8 | 3 | 278 | 1,10 % | 21 452,600 TND | 21 662,300 TND |
| 2026-05 | 278 | 6 | 2 | 282 | 0,72 % | 21 831,300 TND | 21 921,100 TND |
| 2026-06 | 282 | 7 | 8 | 281 | 2,84 % | 21 970,500 TND | 22 439,700 TND |
| 2026-07 | 281 | 9 | 8 | 282 | 2,85 % | 22 500,400 TND | 22 648,700 TND |
| 2026-08 | 282 | 10 | 5 | 287 | 1,77 % | 23 158,100 TND | 23 615,800 TND |
