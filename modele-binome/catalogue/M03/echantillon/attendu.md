# Échantillon Medina Distribution — le calcul à la main

12 lignes de `factures.csv`, le fichier des coûts complet, 10 clients, 4 avoirs dans `avoirs.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`factures.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | ligne_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | FE-001-1 | 2026-03-02 · 'CL01' · PR01 · qté 4 · prix 14.070 | gardée |
| 3 | FE-001-2 | 02/03/2026 · 'CL01' · PR09 · qté 10 · prix 7,860 | gardée |
| 4 | FE-002-1 | 3 mars 2026 · ' cl05 ' · PR03 · qté 20 · prix 17.2 | gardée |
| 5 | FE-002-2 | 2026-03-03 · 'CL05' · PR07 · qté 40 · prix 3,315 | gardée |
| 6 | FE-002-2 | 2026-03-03 · 'CL05' · PR07 · qté 40 · prix 3,315 | ignorée : doublon exact de la ligne 5 |
| 7 | FE-003-1 | 2026-03-04 · 'Cl02' · PR10 · qté 6 · prix 8.450 | gardée |
| 8 | FE-004-1 | 2026-03-05 · 'CL08' · PR06 · qté 3 · prix 56,160 | gardée |
| 9 | FE-005-1 | 2026-03-06 · 'CL06' · PR13 · qté 5 · prix 21.430 | rejet `id_conflit` |
| 10 | FE-005-1 | 2026-03-06 · 'CL06' · PR13 · qté 6 · prix 21.430 | rejet `id_conflit` |
| 11 | (vide) | 2026-03-07 · 'CL01' · PR02 · qté 2 · prix 17.460 | rejet `id_manquant` |
| 12 | FE-007-1 | 2026-03-09 · 'CL99' · PR01 · qté 1 · prix 14.500 | rejet `cle_inconnue` |
| 13 | FE-008-1 | 2026-03-09 · 'CL07' · PR12 · qté 0 · prix 25.870 | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Montant facturé et coût d'achat

Une virgule ou un point sépare les décimales : `7,860` = `7.860` = 7 860 millimes ; `17.2` = 17 200 millimes. Le prix est le prix **négocié** de la ligne, pas le prix tarif.

| ligne_id | Date ISO | Client | Produit | Calcul | Montant facturé | Coût d'achat |
|---|---|---|---|---|---|---|
| FE-001-1 | 2026-03-02 | CL01 | PR01 | 4 × 14,070 | 56,280 TND | 4 × 11,900 = 47,600 TND |
| FE-001-2 | 2026-03-02 | CL01 | PR09 | 10 × 7,860 | 78,600 TND | 10 × 6,900 = 69,000 TND |
| FE-002-1 | 2026-03-03 | CL05 | PR03 | 20 × 17,200 | 344,000 TND | 20 × 19,600 = 392,000 TND |
| FE-002-2 | 2026-03-03 | CL05 | PR07 | 40 × 3,315 | 132,600 TND | 40 × 2,700 = 108,000 TND |
| FE-003-1 | 2026-03-04 | CL02 | PR10 | 6 × 8,450 | 50,700 TND | 6 × 6,700 = 40,200 TND |
| FE-004-1 | 2026-03-05 | CL08 | PR06 | 3 × 56,160 | 168,480 TND | 3 × 45,000 = 135,000 TND |

**Montant facturé = 830,660 TND** (830660 millimes). Coût d'achat des cartons facturés = 791,800 TND.

Remarque : la ligne `FE-002-1` (huile végétale vendue 17,200 TND à l'Hypermarché Zahra) est vendue **sous** son coût d'achat (19,600 TND) : c'est un prix d'appel négocié.

## 3. Avoirs (`avoirs.sqlite`, table `avoir`)

- `AV-0001` : `RETOUR` de 2 plateaux de yaourt (ligne `FE-003-1`, CL02), statut `EMIS` → **16,900 TND gardés** ; 2 cartons repris.
- `AV-0002` : `REMISE` sur la ligne `FE-002-1` (erreur de prix), 0 carton, statut `EMIS` → **17,200 TND gardés**.
- `AV-0003` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `AV-0004` : la ligne `FE-099-1` n'existe pas → rejet `cle_inconnue` (source `avoirs.sqlite`).

**Avoirs = 34,100 TND.**

## 4. Ventes nettes, coût d'achat, marge commerciale, taux d'avoir

- Ventes nettes = montant facturé − avoirs = 830,660 TND − 34,100 TND = **796,560 TND**.
- Cartons repris : 2 × 6,700 (coût du yaourt) = 13,400 TND. La `REMISE` ne reprend aucun carton.
- Coût d'achat des unités nettes = 791,800 TND − 13,400 TND = **778,400 TND**.
- Marge commerciale = ventes nettes − coût d'achat des unités nettes = **18,160 TND**.
- Taux d'avoir = avoirs / montant facturé = 34100 / 830660 = **4,11 %**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_facture` : 6 lignes · `fact_avoir` : 2 lignes · `dim_produit` : 14 · `dim_client` : 10 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
