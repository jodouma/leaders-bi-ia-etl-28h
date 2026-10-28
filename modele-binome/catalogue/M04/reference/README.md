# Référence — Mission 04 (Colis Rapide)

Valeurs calculées par le **générateur** (`authoring/generateurs/`) depuis la vérité terrain, sans passer par un ETL. C'est l'oracle de `controles/verifier.py`. Montants en millimes dans les JSON ; ici affichés en TND.

## Indicateurs

| Indicateur | après lot1 | après lot2 | code |
|---|---|---|---|
| Colis livrés | 2080 | 2497 | `colis_livres` |
| Colis à l'heure | 1759 | 2093 | `colis_a_l_heure` |
| Ponctualité | 84,57 % | 83,82 % | `ponctualite` |
| Retard moyen | 2,49 jours | 2,41 jours | `retard_moyen_jours` |
| Montant facturé | 26 977,730 TND | 32 172,580 TND | `montant_facture_millimes` |
| Pénalités de retard | 825,232 TND | 1 005,341 TND | `penalites_millimes` |
| Revenu facturé net de pénalités | 26 152,498 TND | 31 167,239 TND | `revenu_net_millimes` |
| Coût transporteur | 16 969,000 TND | 20 308,300 TND | `cout_transporteur_millimes` |
| Marge de livraison | 9 183,498 TND | 10 858,939 TND | `marge_livraison_millimes` |

## Lignes par table

| Table | après lot1 | après lot2 |
|---|---|---|
| `dim_date` | 181 | 243 |
| `dim_agence` | 7 | 8 |
| `dim_service` | 3 | 3 |
| `dim_tarif` | 16 | 16 |
| `fact_colis` | 2080 | 2497 |

## Rejets par motif (lignes)

| Motif | lot1 | lot2 |
|---|---|---|
| `cle_inconnue` | 11 | 5 |
| `id_conflit` | 6 | 2 |
| `id_manquant` | 5 | 2 |
| `quantite_invalide` | 7 | 2 |
| **total** | 29 | 11 |

## Historique (dim_agence) après le dernier lot

| Clé métier | zone | valid_from | valid_to |
|---|---|---|---|
| ARI | Grand Tunis | 2020-01-06 | (courante) |
| BIZ | Nord | 2021-04-12 | (courante) |
| GAB | Sud | 2023-02-01 | (courante) |
| NAB | Nord | 2020-09-01 | 2026-07-15 |
| NAB | Centre-Sahel | 2026-07-15 | (courante) |
| SFX | Sud | 2020-05-04 | (courante) |
| SOU | Centre-Sahel | 2019-11-18 | (courante) |
| TUN | Grand Tunis | 2019-03-01 | (courante) |

## Fichiers

- `attendu_lot1.json` : état attendu après `initial`.
- `attendu_lot2.json` : état attendu après `increment` **et** après `rejeu` (identique).
- `contrat_entrepot.json` : noms des tables et colonnes, SCD2, vue d'analyse, indicateurs, axes — lu par le vérificateur.
- `visuels/revenu_net_par_mois_et_zone.png` · `visuels/revenu_net_par_mois_et_zone.svg`
- `visuels/ponctualite_par_agence.png` · `visuels/ponctualite_par_agence.svg`
- `visuels/revenu_cout_marge_par_tranche.png` · `visuels/revenu_cout_marge_par_tranche.svg`
- `visuels/retard_moyen_par_agence.png` · `visuels/retard_moyen_par_agence.svg`
- `visuels/rejets_par_motif.png` · `visuels/rejets_par_motif.svg`

## Facturation : lignes ignorées (ce ne sont pas des rejets)

| Lignes de `facturation.sqlite` | lot1 | lot2 |
|---|---|---|
| Factures `ANNULEE` ignorées | 46 | 7 |
| Pénalités `ANNULEE` ignorées | 28 | 11 |
| Factures de colis déjà chargés (recopiées au lot 2) | 0 | 14 |
| Pénalités `APPLIQUEE` de colis déjà chargés (recopiées au lot 2) | 0 | 2 |
