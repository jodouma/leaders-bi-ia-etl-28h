# Échantillon Souk Express — le calcul à la main

12 lignes de `commandes.csv`, le catalogue complet, 6 canaux, 4 remboursements dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`commandes.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | ligne_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | E-01-1 | 2026-03-02 · 'WEB' · P01 · qté 2 · prix 45.000 · remise '' | gardée |
| 3 | E-01-2 | 02/03/2026 · 'WEB' · P12 · qté 1 · prix 18,5 · remise '' | gardée |
| 4 | E-02-1 | 3 mars 2026 · ' bzl ' · P02 · qté 1 · prix 89,900 · remise '9,000' | gardée |
| 5 | E-03-1 | 2026-03-05 · 'VSO' · P03 · qté 3 · prix 15.900 · remise '0' | gardée |
| 6 | E-03-1 | 2026-03-05 · 'VSO' · P03 · qté 3 · prix 15.900 · remise '0' | ignorée : doublon exact de la ligne 5 |
| 7 | E-04-1 | 2026-03-06 · 'App' · P06 · qté 2 · prix 32,500 · remise '6.5' | gardée |
| 8 | E-05-1 | 2026-03-07 · 'SHM' · P01 · qté 1 · prix 40.500 · remise '4,050' | gardée |
| 9 | E-06-1 | 2026-03-07 · 'WEB' · P12 · qté 1 · prix 18.500 · remise '' | rejet `id_conflit` |
| 10 | E-06-1 | 2026-03-07 · 'WEB' · P12 · qté 2 · prix 18.500 · remise '' | rejet `id_conflit` |
| 11 | (vide) | 2026-03-08 · 'GCO' · P01 · qté 1 · prix 45.000 · remise '' | rejet `id_manquant` |
| 12 | E-08-1 | 2026-03-09 · 'WEB' · X99 · qté 1 · prix 9.000 · remise '' | rejet `cle_inconnue` |
| 13 | E-09-1 | 2026-03-09 · 'APP' · P06 · qté 0 · prix 32.500 · remise '' | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées, dans 5 commandes** (`E-01` a deux lignes).

## 2. CA brut et remises

Une virgule ou un point sépare les décimales : `18,5` = `18.500` = 18 500 millimes. `40.500` est un prix promotionnel : on garde le prix payé. La remise est un montant en TND pour **toute la ligne** ; vide ou `0` = pas de remise.

| ligne_id | Commande | Date ISO | Canal | Calcul du brut | Brut | Remise |
|---|---|---|---|---|---|---|
| E-01-1 | E-01 | 2026-03-02 | WEB | 2 × 45,000 | 90,000 TND | 0,000 TND |
| E-01-2 | E-01 | 2026-03-02 | WEB | 1 × 18,500 | 18,500 TND | 0,000 TND |
| E-02-1 | E-02 | 2026-03-03 | BZL | 1 × 89,900 | 89,900 TND | 9,000 TND |
| E-03-1 | E-03 | 2026-03-05 | VSO | 3 × 15,900 | 47,700 TND | 0,000 TND |
| E-04-1 | E-04 | 2026-03-06 | APP | 2 × 32,500 | 65,000 TND | 6,500 TND |
| E-05-1 | E-05 | 2026-03-07 | SHM | 1 × 40,500 | 40,500 TND | 4,050 TND |

- **CA brut** = 90,000 + 18,500 + 89,900 + 47,700 + 65,000 + 40,500 = **351,600 TND** (351600 millimes).
- **Remises** = 9,000 + 6,500 + 4,050 = **19,550 TND**.

## 3. Remboursements (`operations.sqlite`, table `remboursement`)

- `RB-0001` : 1 coque (ligne `E-03-1`, canal VSO), statut `REMBOURSE` → **15,900 TND gardés**.
- `RB-0002` : statut `REFUSE` → ignoré (ce n'est pas un rejet).
- `RB-0003` : la ligne `E-99-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).
- `RB-0004` : statut `EN_COURS` (pas encore payé) → ignoré.

**Remboursements = 15,900 TND.**

## 4. CA net et panier moyen net

- CA net = CA brut − remises − remboursements = 351,600 TND − 19,550 TND − 15,900 TND = **316,150 TND**.
- Commandes distinctes : E-01, E-02, E-03, E-04, E-05 = **5**.
- Panier moyen net = 316,150 TND / 5 = **63,230 TND**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_commande` : 6 lignes · `fact_remboursement` : 1 ligne · `dim_produit` : 15 · `dim_canal` : 6 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
