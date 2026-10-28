# Référence — Mission 03 (Medina Distribution)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Montant facturé | 245 596,350 TND | 292 453,560 TND | `montant_facture_millimes` |
| Avoirs | 2 665,590 TND | 3 446,680 TND | `avoirs_millimes` |
| Ventes nettes | 242 930,760 TND | 289 006,880 TND | `ventes_nettes_millimes` |
| Coût d'achat des unités nettes | 210 339,700 TND | 249 932,500 TND | `cout_achat_net_millimes` |
| Marge commerciale | 32 591,060 TND | 39 074,380 TND | `marge_commerciale_millimes` |
| Taux d'avoir | 1,09 % | 1,18 % | `taux_avoir` |
| Cartons nets | 21668 | 25658 | `unites_nettes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_produit` | 14 | 14 |
| `dim_client` | 10 | 11 |
| `fact_facture` | 2053 | 2458 |
| `fact_avoir` | 100 | 126 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 4 | 2 |
| `quantite_invalide` | 6 | 2 |
| **total** | 24 | 10 |

## Historique (dim_client) après le dernier lot

| Clé métier | segment | valid_from | valid_to |
|---|---|---|---|
| CL01 | épicerie | 2022-03-01 | (courante) |
| CL02 | restaurant | 2023-06-15 | (courante) |
| CL03 | hôtel | 2021-11-02 | (courante) |
| CL04 | épicerie | 2023-02-01 | 2026-07-15 |
| CL04 | grande surface | 2026-07-15 | (courante) |
| CL05 | grande surface | 2020-09-14 | (courante) |
| CL06 | restaurant | 2024-01-08 | (courante) |
| CL07 | épicerie | 2022-05-20 | (courante) |
| CL08 | hôtel | 2021-04-12 | (courante) |
| CL09 | grande surface | 2022-10-03 | (courante) |
| CL10 | restaurant | 2024-03-18 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/ventes_nettes_par_mois_et_segment.png` · `visuels/ventes_nettes_par_mois_et_segment.svg`
- `visuels/ventes_nettes_et_marge_par_client.png` · `visuels/ventes_nettes_et_marge_par_client.svg`
- `visuels/marge_commerciale_par_produit.png` · `visuels/marge_commerciale_par_produit.svg`
- `visuels/taux_avoir_par_client.png` · `visuels/taux_avoir_par_client.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
