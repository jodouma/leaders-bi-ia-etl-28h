# Échantillon Maison Zitouna — le calcul à la main

12 lignes de `ventes.csv`, le catalogue complet, 3 boutiques, 3 retours dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`ventes.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | ligne_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | E-001-1 | 2026-03-02 · 'TUN' · P01 · qté 2 · prix 18.500 | gardée |
| 3 | E-001-2 | 02/03/2026 · 'TUN' · P05 · qté 3 · prix 3,900 | gardée |
| 4 | E-002-1 | 3 mars 2026 · ' nbe ' · P04 · qté 1 · prix 14.5 | gardée |
| 5 | E-003-1 | 2026-03-05 · 'SFX' · P01 · qté 1 · prix 18,5 | gardée |
| 6 | E-003-1 | 2026-03-05 · 'SFX' · P01 · qté 1 · prix 18,5 | ignorée : doublon exact de la ligne 5 |
| 7 | E-004-1 | 2026-03-06 · 'Sfx' · P04 · qté 2 · prix 14,500 | gardée |
| 8 | E-005-1 | 2026-03-06 · 'TUN' · P01 · qté 1 · prix 16.650 | gardée |
| 9 | E-006-1 | 2026-03-07 · 'TUN' · P05 · qté 2 · prix 3.900 | rejet `id_conflit` |
| 10 | E-006-1 | 2026-03-07 · 'TUN' · P05 · qté 4 · prix 3.900 | rejet `id_conflit` |
| 11 | (vide) | 2026-03-08 · 'NBE' · P01 · qté 1 · prix 18.500 | rejet `id_manquant` |
| 12 | E-008-1 | 2026-03-09 · 'TUN' · P99 · qté 1 · prix 9.000 | rejet `cle_inconnue` |
| 13 | E-009-1 | 2026-03-09 · 'NBE' · P05 · qté -1 · prix 3.900 | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Ventes brutes

Une virgule ou un point sépare les décimales : `18,5` = `18.500` = 18 500 millimes. `16.650` est un prix promotionnel : on garde le prix du ticket.

| ligne_id | Date ISO | Boutique | Produit | Calcul | Montant brut |
|---|---|---|---|---|---|
| E-001-1 | 2026-03-02 | TUN | P01 | 2 × 18,500 | 37,000 TND |
| E-001-2 | 2026-03-02 | TUN | P05 | 3 × 3,900 | 11,700 TND |
| E-002-1 | 2026-03-03 | NBE | P04 | 1 × 14,500 | 14,500 TND |
| E-003-1 | 2026-03-05 | SFX | P01 | 1 × 18,500 | 18,500 TND |
| E-004-1 | 2026-03-06 | SFX | P04 | 2 × 14,500 | 29,000 TND |
| E-005-1 | 2026-03-06 | TUN | P01 | 1 × 16,650 | 16,650 TND |

**Ventes brutes = 127,350 TND** (127350 millimes).

## 3. Retours (`operations.sqlite`, table `retour`)

- `R-0001` : 1 × Dattes (ligne `E-004-1`, SFX), statut `VALIDE` → **14,500 TND gardés**.
- `R-0002` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `R-0003` : la ligne `E-099-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

**Retours = 14,500 TND.**

## 4. Ventes nettes, coût d'achat, marge, taux de retour

- Ventes nettes = brutes − retours = 127,350 TND − 14,500 TND = **112,850 TND**.
- Coût d'achat des unités vendues = 2 × 11,200 + 3 × 1,650 + 1 × 8,750 + 1 × 11,200 + 2 × 8,750 + 1 × 11,200 = 76,000 TND.
- Unités retournées : 1 × 8,750 (coût des dattes) = 8,750 TND. Coût d'achat des unités nettes = 76,000 TND − 8,750 TND = **67,250 TND**.
- Marge sur coût d'achat = ventes nettes − coût des unités nettes = **45,600 TND**.
- Taux de retour = retours / brutes = 14500 / 127350 = **11,39 %**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_vente` : 6 lignes · `fact_retour` : 1 ligne · `dim_produit` : 8 · `dim_boutique` : 3 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
