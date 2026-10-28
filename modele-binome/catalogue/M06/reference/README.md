# Référence — Mission 06 (Dar Azur)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Nuitées vendues | 4456 | 6918 | `nuitees_vendues` |
| Chambres disponibles (chambres × nuits) | 11584 | 15552 | `chambres_disponibles` |
| Taux d'occupation | 38,47 % | 44,48 % | `taux_occupation` |
| Montant des séjours | 992 422,000 TND | 1 794 296,500 TND | `montant_sejours_millimes` |
| Remboursements | 42 874,000 TND | 76 556,000 TND | `remboursements_millimes` |
| Revenu net d'annulations | 949 548,000 TND | 1 717 740,500 TND | `revenu_net_millimes` |
| RevPAR | 81,971 TND | 110,451 TND | `revpar_millimes` |
| Commissions des canaux | 130 569,230 TND | 225 838,075 TND | `commissions_millimes` |
| Séjours acceptés | 1896 | 2360 | `sejours` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_etablissement` | 4 | 4 |
| `dim_canal` | 4 | 5 |
| `fact_sejour` | 1896 | 2360 |
| `fact_annulation` | 107 | 135 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 9 | 4 |
| `id_conflit` | 8 | 4 |
| `id_manquant` | 6 | 2 |
| `quantite_invalide` | 6 | 3 |
| **total** | 29 | 13 |

## Historique (dim_canal) après le dernier lot

| Clé métier | taux_commission_pct (%) | valid_from | valid_to |
|---|---|---|---|
| DIR | 0 | 2025-01-01 | (courante) |
| ENT | 10 | 2025-01-01 | (courante) |
| OTA | 18 | 2025-01-01 | 2026-07-15 |
| OTA | 15 | 2026-07-15 | (courante) |
| TOP | 25 | 2025-01-01 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/revenu_net_par_mois_et_etablissement.png` · `visuels/revenu_net_par_mois_et_etablissement.svg`
- `visuels/taux_occupation_par_etablissement.png` · `visuels/taux_occupation_par_etablissement.svg`
- `visuels/revpar_par_mois.png` · `visuels/revpar_par_mois.svg`
- `visuels/occupation_semestre_ete_par_etablissement.png` · `visuels/occupation_semestre_ete_par_etablissement.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
