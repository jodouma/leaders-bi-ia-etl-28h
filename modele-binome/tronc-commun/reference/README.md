# Référence — Mission 00 (Maison Zitouna)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Ventes brutes | 78 067,830 TND | 95 849,090 TND | `ventes_brutes_millimes` |
| Retours | 3 758,330 TND | 4 404,630 TND | `retours_millimes` |
| Ventes nettes | 74 309,500 TND | 91 444,460 TND | `ventes_nettes_millimes` |
| Coût d'achat des unités nettes | 45 317,800 TND | 55 837,600 TND | `cout_achat_net_millimes` |
| Marge sur coût d'achat | 28 991,700 TND | 35 606,860 TND | `marge_cout_achat_millimes` |
| Taux de retour | 4,81 % | 4,60 % | `taux_retour` |
| Unités nettes | 3605 | 4264 | `unites_nettes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_produit` | 8 | 8 |
| `dim_boutique` | 3 | 4 |
| `fact_vente` | 1960 | 2345 |
| `fact_retour` | 76 | 99 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 7 | 2 |
| **total** | 26 | 10 |

## Historique (dim_boutique) après le dernier lot

| Clé métier | zone | valid_from | valid_to |
|---|---|---|---|
| NBE | Cap Bon | 2021-05-10 | 2026-07-15 |
| NBE | Nord-Est | 2026-07-15 | (courante) |
| SFX | Sud | 2022-09-19 | (courante) |
| TUN | Grand Tunis | 2018-04-02 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/ventes_nettes_par_mois_et_zone.png` · `visuels/ventes_nettes_par_mois_et_zone.svg`
- `visuels/ventes_nettes_et_marge_par_boutique.png` · `visuels/ventes_nettes_et_marge_par_boutique.svg`
- `visuels/taux_retour_par_mois.png` · `visuels/taux_retour_par_mois.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
