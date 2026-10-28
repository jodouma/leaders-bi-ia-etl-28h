# Échantillon Colis Rapide — le calcul à la main

12 lignes de `colis.csv`, la grille tarifaire complète, 7 agences, 8 factures et 4 pénalités dans `facturation.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`colis.csv`)

La ligne 1 du fichier est l'en-tête. Colonnes montrées : date de livraison · agence · zone de destination · poids · service.

| Ligne du fichier | colis_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | CR-E01 | 2026-03-05 · 'TUN' · GT · 0.800 kg · STD | gardée |
| 3 | CR-E02 | 03/03/2026 · 'ARI' · NO · 2,5 kg · EXP | gardée |
| 4 | CR-E03 | 8 mars 2026 · ' sfx ' · SU · 5.000 kg · STD | gardée |
| 5 | CR-E04 | 2026-03-08 · 'NAB' · sa · 12,75 kg · ECO | gardée |
| 6 | CR-E05 | 2026-03-09 · 'SOU' · GT · 1 kg · EXP | gardée |
| 7 | CR-E05 | 2026-03-09 · 'SOU' · GT · 1 kg · EXP | ignorée : doublon exact de la ligne 6 |
| 8 | CR-E06 | 2026-03-09 · 'TUN' · NO · 3.2 kg · STD | rejet `id_conflit` |
| 9 | CR-E06 | 2026-03-10 · 'TUN' · NO · 3.2 kg · STD | rejet `id_conflit` |
| 10 | (vide) | 2026-03-10 · 'BIZ' · NO · 1.1 kg · STD | rejet `id_manquant` |
| 11 | CR-E07 | 2026-03-11 · 'KAI' · SA · 2.0 kg · STD | rejet `cle_inconnue` |
| 12 | CR-E08 | 2026-03-11 · 'GAB' · SU · -1,200 kg · STD | rejet `quantite_invalide` |
| 13 | CR-E09 | 2026-03-13 · 'GAB' · SU · 7.4 kg · STD | gardée |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue` pour l'agence `KAI`, 1 `quantite_invalide` pour le poids `-1,200`) → **6 colis gardés**.

## 2. Retard, tranche, coût et facture de chaque colis

- Écart = date livrée − date promise. `retard_jours` = l'écart s'il est positif, sinon 0. **Livré le jour promis = à l'heure** (`CR-E01`, `CR-E02`) ; livré en avance aussi (`CR-E04`).
- Tranche : borne basse exclue, borne haute incluse. `1` kg → T1 (`CR-E05`) ; `5.000` kg → T2 (`CR-E03`).
- Le coût transporteur vient de la grille (feuille `Grille`, zone de destination × tranche). Le montant facturé vient de la **facture non annulée** de la base ; la pénalité, des pénalités `APPLIQUEE`.

| colis_id | Promis | Livré | Écart → retard_jours | À l'heure | Poids → tranche | Tarif | Coût transporteur | Facturé | Pénalité |
|---|---|---|---|---|---|---|---|---|---|
| CR-E01 | 2026-03-05 | 2026-03-05 | +0 → 0 | oui | 800 g → T1 | GT-T1 | 4,200 TND | 7,000 TND | 0,000 TND |
| CR-E02 | 2026-03-03 | 2026-03-03 | +0 → 0 | oui | 2500 g → T2 | NO-T2 | 7,400 TND | 17,250 TND | 0,000 TND |
| CR-E03 | 2026-03-06 | 2026-03-08 | +2 → 2 | non | 5000 g → T2 | SU-T2 | 10,200 TND | 14,000 TND | 2,800 TND |
| CR-E04 | 2026-03-09 | 2026-03-08 | -1 → 0 | oui | 12750 g → T4 | SA-T4 | 17,200 TND | 20,400 TND | 0,000 TND |
| CR-E05 | 2026-03-06 | 2026-03-09 | +3 → 3 | non | 1000 g → T1 | GT-T1 | 4,200 TND | 10,500 TND | 3,150 TND |
| CR-E09 | 2026-03-12 | 2026-03-13 | +1 → 1 | non | 7400 g → T3 | SU-T3 | 15,300 TND | 19,500 TND | 1,950 TND |

Base `facturation.sqlite` : la facture `FA-E03` de `CR-E03` est `ANNULEE` (elle a été refaite : `FA-E04`, 14,000 TND) ; la pénalité `PE-E02` est `ANNULEE` → ignorées, ce ne sont pas des rejets. La facture `FA-E08` vise le colis `CR-E99`, qui n'existe pas → rejet `cle_inconnue` (source `facturation.sqlite`, numero_ligne 8).

## 3. Les indicateurs

- Colis livrés = **6** ; à l'heure = 3 (CR-E01, CR-E02, CR-E04) ; en retard = 3.
- Ponctualité = 3 / 6 = **50,00 %**.
- Retard moyen = jours de retard des colis en retard / nombre de colis en retard = (2 + 3 + 1) / 3 = **2,00 jours**. Les colis à l'heure ne comptent pas.
- Montant facturé = 88,650 TND ; pénalités (10 % du montant facturé par jour de retard, service ECO exempté) = 20 % × 14,000 + 30 % × 10,500 + 10 % × 19,500 = 2,800 + 3,150 + 1,950 = 7,900 TND.
- Revenu facturé net de pénalités = **80,750 TND**.
- Coût transporteur = **58,500 TND**.
- Marge de livraison = revenu net − coût transporteur = **22,250 TND** (marge partielle, pas un bénéfice).

## 4. Ce que doit contenir l'entrepôt de l'échantillon

`fact_colis` : 6 lignes · `dim_agence` : 7 · `dim_service` : 3 · `dim_tarif` : 16 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
