# Référence — Mission 01 (Carthage Market)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Ventes brutes | 18 804,510 TND | 22 353,670 TND | `ventes_brutes_millimes` |
| Remises | 206,260 TND | 344,040 TND | `remises_millimes` |
| Retours | 367,487 TND | 473,444 TND | `retours_millimes` |
| Ventes nettes | 18 437,023 TND | 21 880,226 TND | `ventes_nettes_millimes` |
| Coût d'achat des unités nettes | 12 786,330 TND | 15 242,310 TND | `cout_achat_net_millimes` |
| Marge sur coût d'achat | 5 650,693 TND | 6 637,916 TND | `marge_cout_achat_millimes` |
| Part des franchisés | 44,10 % | 44,51 % | `part_franchises` |
| Taux de retour | 1,95 % | 2,12 % | `taux_retour` |
| Unités nettes | 5038 | 5983 | `unites_nettes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_produit` | 12 | 12 |
| `dim_magasin` | 7 | 8 |
| `fact_vente` | 2150 | 2570 |
| `fact_retour` | 59 | 80 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 3 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 4 | 2 |
| `quantite_invalide` | 6 | 3 |
| **total** | 24 | 10 |

## Historique (dim_magasin) après le dernier lot

| Clé métier | region | valid_from | valid_to |
|---|---|---|---|
| ARI | Grand Tunis | 2020-02-17 | (courante) |
| BIZ | Nord | 2021-06-07 | (courante) |
| GAB | Sud | 2023-03-20 | (courante) |
| HAM | Cap Bon | 2022-04-11 | 2026-07-15 |
| HAM | Sahel | 2026-07-15 | (courante) |
| LAC | Grand Tunis | 2017-09-04 | (courante) |
| SFX | Sud | 2019-05-13 | (courante) |
| SOU | Sahel | 2018-11-05 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/ventes_nettes_par_mois_et_region.png` · `visuels/ventes_nettes_par_mois_et_region.svg`
- `visuels/ventes_nettes_et_marge_par_magasin.png` · `visuels/ventes_nettes_et_marge_par_magasin.svg`
- `visuels/ventes_nettes_et_marge_par_famille.png` · `visuels/ventes_nettes_et_marge_par_famille.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
