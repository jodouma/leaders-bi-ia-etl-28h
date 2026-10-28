# Référence — Mission 10 (Pixel Studio)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Heures | 10 300,00 h (1030000 centièmes) | 12 381,50 h (1238150 centièmes) | `heures_centiemes` |
| Coût de charge | 377 400,125 TND | 453 097,875 TND | `cout_charge_millimes` |
| Factures | 470 453,450 TND | 596 866,400 TND | `factures_millimes` |
| Avoirs | 9 606,000 TND | 10 856,000 TND | `avoirs_millimes` |
| Facturé net | 460 847,450 TND | 586 010,400 TND | `facture_net_millimes` |
| Marge de contribution | 83 447,325 TND | 132 912,525 TND | `marge_contribution_millimes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_collaborateur` | 15 | 15 |
| `dim_projet` | 20 | 21 |
| `fact_temps` | 1981 | 2384 |
| `fact_facture` | 63 | 86 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 8 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 4 | 2 |
| `quantite_invalide` | 6 | 3 |
| **total** | 24 | 11 |

## Historique (dim_projet) après le dernier lot

| Clé métier | chef_projet | valid_from | valid_to |
|---|---|---|---|
| INT01 | Bilel Chaouch | 2025-01-01 | (courante) |
| PX01 | Hela Mansour | 2025-11-03 | (courante) |
| PX02 | Nour Jebali | 2026-01-05 | (courante) |
| PX03 | Hela Mansour | 2026-02-02 | (courante) |
| PX04 | Bilel Chaouch | 2025-09-15 | (courante) |
| PX05 | Bilel Chaouch | 2025-12-01 | (courante) |
| PX06 | Nour Jebali | 2026-03-02 | (courante) |
| PX07 | Hela Mansour | 2026-01-12 | 2026-07-15 |
| PX07 | Nour Jebali | 2026-07-15 | (courante) |
| PX08 | Hela Mansour | 2026-01-19 | (courante) |
| PX09 | Bilel Chaouch | 2025-06-02 | (courante) |
| PX10 | Nour Jebali | 2026-04-06 | (courante) |
| PX11 | Bilel Chaouch | 2026-02-16 | (courante) |
| PX12 | Hela Mansour | 2026-05-04 | (courante) |
| PX13 | Nour Jebali | 2026-02-09 | (courante) |
| PX14 | Hela Mansour | 2025-10-06 | (courante) |
| PX15 | Bilel Chaouch | 2026-01-26 | (courante) |
| PX16 | Nour Jebali | 2026-03-16 | (courante) |
| PX17 | Bilel Chaouch | 2026-04-13 | (courante) |
| PX18 | Hela Mansour | 2026-02-23 | (courante) |
| PX19 | Nour Jebali | 2026-04-20 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/cout_charge_par_mois_et_type.png` · `visuels/cout_charge_par_mois_et_type.svg`
- `visuels/marge_contribution_par_projet.png` · `visuels/marge_contribution_par_projet.svg`
- `visuels/facture_cout_marge_par_type.png` · `visuels/facture_cout_marge_par_type.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
