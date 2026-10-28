# Échantillon Pixel Studio — le calcul à la main

12 lignes de `temps.csv`, le classeur des coûts complet, les 20 projets, 3 factures et 2 avoirs dans `facturation.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

Taux horaires coût (feuille Profils) : développeur 32,500 TND · designer 29,000 · chef de projet 41,000 · consultant 47,500.

## 1. Décision ligne par ligne (`temps.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | temps_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | E-01 | 2026-03-02 · 'C01' · 'PX01' · heures 7.5 | gardée |
| 3 | E-02 | 03/03/2026 · 'C01' · 'PX01' · heures 7,5 | gardée |
| 4 | E-03 | 4 mars 2026 · 'C02' · 'PX02' · heures 3 | gardée |
| 5 | E-03 | 4 mars 2026 · 'C02' · 'PX02' · heures 3 | ignorée : doublon exact de la ligne 4 |
| 6 | E-04 | 2026-03-04 · ' c03 ' · 'PX01' · heures 1,25 | gardée |
| 7 | E-05 | 2026-03-05 · 'C04' · 'INT01' · heures 2 | gardée |
| 8 | E-06 | 2026-03-05 · 'C02' · 'PX02' · heures 4 | rejet `id_conflit` |
| 9 | E-06 | 2026-03-05 · 'C02' · 'PX02' · heures 4,5 | rejet `id_conflit` |
| 10 | (vide) | 2026-03-06 · 'C01' · 'PX01' · heures 3 | rejet `id_manquant` |
| 11 | E-07 | 2026-03-06 · 'C99' · 'PX01' · heures 2 | rejet `cle_inconnue` |
| 12 | E-08 | 2026-03-06 · 'C01' · 'PX01' · heures -2 | rejet `quantite_invalide` |
| 13 | E-09 | 2026-03-06 · 'C01' · ' px02' · heures 6.25 | gardée |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Heures et coût de charge

Une virgule ou un point sépare les décimales : `7,5` = `7.5` = 7 h 30 = **750 centièmes d'heure**. `1,25` = 1 h 15 = 125. Coût = heures × taux du profil (le profil vient du classeur, pas du CSV).

| temps_id | Date ISO | Collaborateur (profil) | Projet | Heures lues → centièmes | Calcul du coût | Coût de charge |
|---|---|---|---|---|---|---|
| E-01 | 2026-03-02 | C01 (développeur) | PX01 | `7.5` → 750 | 7,5 h × 32,500 | 243,750 TND |
| E-02 | 2026-03-03 | C01 (développeur) | PX01 | `7,5` → 750 | 7,5 h × 32,500 | 243,750 TND |
| E-03 | 2026-03-04 | C02 (designer) | PX02 | `3` → 300 | 3,0 h × 29,000 | 87,000 TND |
| E-04 | 2026-03-04 | C03 (chef de projet) | PX01 | `1,25` → 125 | 1,25 h × 41,000 | 51,250 TND |
| E-05 | 2026-03-05 | C04 (consultant) | INT01 | `2` → 200 | 2,0 h × 47,500 | 95,000 TND |
| E-09 | 2026-03-06 | C01 (développeur) | PX02 | `6.25` → 625 | 6,25 h × 32,500 | 203,125 TND |

**Heures = 2750 centièmes = 27,5 h. Coût de charge = 923,875 TND** (923875 millimes).

## 3. Factures et avoirs (`facturation.sqlite`)

- `F-001` : PX02 (forfait, jalon 1), 900,000 TND, `EMISE` → gardée.
- `F-002` : `ANNULEE` (la même facture saisie deux fois) → ignorée (ce n'est pas un rejet).
- `F-003` : PX01 (régie de mars), 1 200,000 TND, `EMISE` → gardée.
- `AV-001` : avoir de 150,000 TND sur `F-003` → gardé, compté **en moins** sur PX01 (projet de la facture d'origine).
- `AV-002` : la facture `F-099` n'existe pas → rejet `cle_inconnue` (source `facturation.sqlite`).

**Factures = 2 100,000 TND · Avoirs = 150,000 TND · Facturé net = 1 950,000 TND.**

## 4. Marge de contribution

Marge de contribution = facturé net − coût de charge = 1 950,000 TND − 923,875 TND = **1 026,125 TND**. Ce n'est pas un bénéfice : aucun frais général n'est déduit.

| Projet | Heures | Coût de charge | Facturé net | Marge de contribution |
|---|---|---|---|---|
| INT01 | 2,0 h | 95,000 TND | 0,000 TND | -95,000 TND |
| PX01 | 16,25 h | 538,750 TND | 1 050,000 TND | 511,250 TND |
| PX02 | 9,25 h | 290,125 TND | 900,000 TND | 609,875 TND |

INT01 est le projet interne : ses heures coûtent mais ne sont jamais facturées (marge négative, c'est normal).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_temps` : 6 lignes · `fact_facture` : 3 lignes (2 factures + 1 avoir) · `dim_collaborateur` : 15 · `dim_projet` : 20 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
