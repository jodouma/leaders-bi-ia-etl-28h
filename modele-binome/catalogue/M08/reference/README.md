# Référence — Mission 08 (TechniServ)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Interventions | 1560 | 2030 | `interventions` |
| Interventions correctives | 981 | 1333 | `interventions_correctives` |
| Délai total des correctifs | 19331 | 26905 | `delai_total_correctif_heures` |
| Délai moyen d'intervention | 19,71 h | 20,18 h | `delai_moyen_heures` |
| Heures facturées | 4387 | 5757 | `heures_facturees` |
| Coût de main-d'œuvre | 235 522,500 TND | 305 267,500 TND | `cout_main_oeuvre_millimes` |
| Coût des pièces | 221 769,600 TND | 298 407,000 TND | `cout_pieces_millimes` |
| Coût d'intervention | 457 292,100 TND | 603 674,500 TND | `cout_intervention_millimes` |
| Revenu de contrat | 529 000,000 TND | 707 800,000 TND | `revenu_contrat_millimes` |
| Marge de service | 71 707,900 TND | 104 125,500 TND | `marge_service_millimes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_contrat` | 10 | 10 |
| `dim_equipement` | 48 | 49 |
| `fact_intervention` | 1560 | 2030 |
| `fact_revenu_contrat` | 58 | 78 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 10 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 4 | 2 |
| `quantite_invalide` | 6 | 2 |
| **total** | 26 | 10 |

## Historique (dim_equipement) après le dernier lot

| Clé métier | contrat_id | valid_from | valid_to |
|---|---|---|---|
| EQ-001 | CT-01 | 2024-01-01 | (courante) |
| EQ-002 | CT-01 | 2024-01-01 | (courante) |
| EQ-003 | CT-01 | 2024-01-01 | (courante) |
| EQ-004 | CT-01 | 2024-01-01 | (courante) |
| EQ-005 | CT-01 | 2024-01-01 | (courante) |
| EQ-006 | CT-01 | 2024-01-01 | (courante) |
| EQ-007 | CT-02 | 2023-06-01 | (courante) |
| EQ-008 | CT-02 | 2023-06-01 | (courante) |
| EQ-009 | CT-02 | 2023-06-01 | (courante) |
| EQ-010 | CT-02 | 2023-06-01 | (courante) |
| EQ-011 | CT-02 | 2023-06-01 | (courante) |
| EQ-012 | CT-02 | 2023-06-01 | (courante) |
| EQ-013 | CT-03 | 2024-09-01 | (courante) |
| EQ-014 | CT-03 | 2024-09-01 | (courante) |
| EQ-015 | CT-03 | 2024-09-01 | (courante) |
| EQ-016 | CT-03 | 2024-09-01 | (courante) |
| EQ-017 | CT-03 | 2024-09-01 | 2026-07-15 |
| EQ-017 | CT-09 | 2026-07-15 | (courante) |
| EQ-018 | CT-04 | 2025-02-01 | (courante) |
| EQ-019 | CT-04 | 2025-02-01 | (courante) |
| EQ-020 | CT-04 | 2025-02-01 | (courante) |
| EQ-021 | CT-04 | 2025-02-01 | (courante) |
| EQ-022 | CT-04 | 2025-02-01 | (courante) |
| EQ-023 | CT-04 | 2025-02-01 | (courante) |
| EQ-024 | CT-05 | 2023-01-01 | (courante) |
| EQ-025 | CT-05 | 2023-01-01 | (courante) |
| EQ-026 | CT-05 | 2023-01-01 | (courante) |
| EQ-027 | CT-05 | 2023-01-01 | (courante) |
| EQ-028 | CT-05 | 2023-01-01 | (courante) |
| EQ-029 | CT-05 | 2023-01-01 | (courante) |
| EQ-030 | CT-05 | 2023-01-01 | (courante) |
| EQ-031 | CT-06 | 2025-09-01 | (courante) |
| EQ-032 | CT-06 | 2025-09-01 | (courante) |
| EQ-033 | CT-06 | 2025-09-01 | (courante) |
| EQ-034 | CT-07 | 2024-04-01 | (courante) |
| EQ-035 | CT-07 | 2024-04-01 | (courante) |
| EQ-036 | CT-07 | 2024-04-01 | (courante) |
| EQ-037 | CT-07 | 2024-04-01 | (courante) |
| EQ-038 | CT-08 | 2026-03-01 | (courante) |
| EQ-039 | CT-08 | 2026-03-01 | (courante) |
| EQ-040 | CT-08 | 2026-03-01 | (courante) |
| EQ-041 | CT-09 | 2025-11-01 | (courante) |
| EQ-042 | CT-09 | 2025-11-01 | (courante) |
| EQ-043 | CT-09 | 2025-11-01 | (courante) |
| EQ-044 | CT-10 | 2025-05-01 | (courante) |
| EQ-045 | CT-10 | 2025-05-01 | (courante) |
| EQ-046 | CT-10 | 2025-05-01 | (courante) |
| EQ-047 | CT-10 | 2025-05-01 | (courante) |
| EQ-048 | CT-10 | 2025-05-01 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/cout_intervention_par_mois_et_categorie.png` · `visuels/cout_intervention_par_mois_et_categorie.svg`
- `visuels/revenu_cout_marge_par_contrat.png` · `visuels/revenu_cout_marge_par_contrat.svg`
- `visuels/delai_moyen_par_mois.png` · `visuels/delai_moyen_par_mois.svg`
- `visuels/cout_top10_equipements.png` · `visuels/cout_top10_equipements.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
