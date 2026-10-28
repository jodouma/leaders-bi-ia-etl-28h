# Référence — Mission 02 (Souk Express)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| CA brut | 220 909,500 TND | 265 265,400 TND | `ca_brut_millimes` |
| Remises | 9 539,800 TND | 11 783,900 TND | `remises_millimes` |
| Remboursements | 10 146,717 TND | 11 323,017 TND | `remboursements_millimes` |
| CA net | 201 222,983 TND | 242 158,483 TND | `ca_net_millimes` |
| Nombre de commandes | 1266 | 1526 | `nb_commandes` |
| Panier moyen net | 158,944 TND | 158,688 TND | `panier_moyen_net_millimes` |
| Unités nettes | 3212 | 3873 | `unites_nettes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_produit` | 15 | 15 |
| `dim_canal` | 6 | 7 |
| `fact_commande` | 2050 | 2460 |
| `fact_remboursement` | 123 | 141 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 6 | 2 |
| **total** | 25 | 10 |

## Historique (dim_canal) après le dernier lot

| Clé métier | famille | valid_from | valid_to |
|---|---|---|---|
| APP | application | 2024-09-15 | (courante) |
| BZL | marketplace | 2024-01-10 | (courante) |
| GCO | réseaux sociaux | 2023-06-01 | (courante) |
| SHM | marketplace | 2025-03-03 | (courante) |
| VSO | réseaux sociaux | 2023-06-01 | 2026-07-15 |
| VSO | marketplace | 2026-07-15 | (courante) |
| WEB | site | 2023-02-01 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/ca_net_par_mois_et_famille.png` · `visuels/ca_net_par_mois_et_famille.svg`
- `visuels/ca_brut_et_net_par_canal.png` · `visuels/ca_brut_et_net_par_canal.svg`
- `visuels/panier_moyen_net_par_canal.png` · `visuels/panier_moyen_net_par_canal.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
