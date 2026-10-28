# Référence — Mission 05 (Académie Nour)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Inscrits | 252 | 310 | `inscrits` |
| Taux d'assiduité | 83,00 % | 82,53 % | `taux_assiduite` |
| Taux de remplissage | 81,29 % | 79,90 % | `taux_remplissage` |
| Paiements | 100 625,000 TND | 122 105,000 TND | `paiements_millimes` |
| Remboursements | 2 979,000 TND | 3 858,000 TND | `remboursements_millimes` |
| Encaissements nets | 97 646,000 TND | 118 247,000 TND | `encaissements_nets_millimes` |
| Encaissement attendu | 100 050,000 TND | 121 270,000 TND | `encaissement_attendu_millimes` |
| Taux d'encaissement | 97,60 % | 97,51 % | `taux_encaissement` |
| Présences | 1596 | 1942 | `presences` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_formation` | 7 | 7 |
| `dim_session` | 20 | 26 |
| `fact_presence` | 1923 | 2353 |
| `fact_paiement` | 377 | 455 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 9 | 4 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 6 | 2 |
| **total** | 26 | 10 |

## Historique (dim_session) après le dernier lot

| Clé métier | centre | valid_from | valid_to |
|---|---|---|---|
| SES-2601 | Tunis | 2026-01-02 | (courante) |
| SES-2602 | Sousse | 2026-01-02 | (courante) |
| SES-2603 | Sfax | 2026-01-02 | (courante) |
| SES-2604 | Tunis | 2026-01-02 | (courante) |
| SES-2605 | Tunis | 2026-01-05 | (courante) |
| SES-2606 | Sousse | 2026-01-12 | (courante) |
| SES-2607 | Tunis | 2026-01-17 | (courante) |
| SES-2608 | Sfax | 2026-01-26 | (courante) |
| SES-2609 | Sousse | 2026-01-27 | (courante) |
| SES-2610 | Tunis | 2026-01-31 | (courante) |
| SES-2611 | Tunis | 2026-02-09 | (courante) |
| SES-2612 | Sfax | 2026-02-17 | (courante) |
| SES-2613 | Sousse | 2026-03-02 | (courante) |
| SES-2614 | Tunis | 2026-03-03 | (courante) |
| SES-2615 | Sfax | 2026-03-09 | (courante) |
| SES-2616 | Sousse | 2026-03-14 | (courante) |
| SES-2617 | Tunis | 2026-03-30 | (courante) |
| SES-2618 | Sfax | 2026-03-31 | (courante) |
| SES-2619 | Sousse | 2026-04-21 | 2026-07-15 |
| SES-2619 | Sfax | 2026-07-15 | (courante) |
| SES-2620 | Tunis | 2026-04-20 | (courante) |
| SES-2621 | Tunis | 2026-05-30 | (courante) |
| SES-2622 | Sousse | 2026-06-01 | (courante) |
| SES-2623 | Sfax | 2026-06-02 | (courante) |
| SES-2624 | Tunis | 2026-06-15 | (courante) |
| SES-2625 | Sfax | 2026-06-29 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/encaissements_nets_par_mois_et_centre.png` · `visuels/encaissements_nets_par_mois_et_centre.svg`
- `visuels/assiduite_et_remplissage_par_centre.png` · `visuels/assiduite_et_remplissage_par_centre.svg`
- `visuels/encaissements_nets_et_attendus_par_formation.png` · `visuels/encaissements_nets_et_attendus_par_formation.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`
