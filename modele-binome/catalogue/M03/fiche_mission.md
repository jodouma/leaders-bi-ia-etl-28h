# Mission 03 — Distribution B2B

**Client fictif :** Medina Distribution (grossiste en produits alimentaires et d'entretien qui livre des épiceries, des restaurants, des grandes surfaces et des hôtels). **Grain du fait :** une ligne de facture.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Medina Distribution achète des cartons de semoule, de pâtes, d'huile, de conserves, de boissons, de produits laitiers et d'entretien, puis les revend à une dizaine de clients professionnels. Chaque client a un prix négocié, souvent plus bas que le prix tarif. Quand un produit arrive abîmé, trop près de sa date limite ou avec une erreur de prix, le service commercial émet un **avoir** (une facture négative). Les lignes de facture sortent du logiciel de facturation dans un CSV, les coûts d'achat et les prix tarif sont dans un classeur Excel, le fichier clients (segment, région) est un JSON et les avoirs sont dans la base SQLite de la gestion commerciale. Le chiffre d'affaires monte, mais personne ne sait quels clients et quels produits rapportent vraiment. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Notre chiffre d'affaires progresse, mais la marge ne suit pas. Je veux savoir **quels clients et quels produits font baisser notre rentabilité commerciale**. Par client, par segment, par produit et par mois : le montant facturé, les avoirs, les ventes nettes, le coût d'achat des unités nettes, la marge commerciale et le taux d'avoir. Dites-moi aussi quelles lignes vous avez écartées, et pourquoi.
> 
> Pour information : à partir du 15 juillet, la Supérette El Amel (CL04) passe du segment « épicerie » au segment « grande surface ». Ses factures du premier semestre doivent rester dans « épicerie ».
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Medina Distribution)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_produit, dim_client, fact_facture, fact_avoir).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. Le client CL04 (Supérette El Amel) passe du segment « épicerie » au segment « grande surface » le 2026-07-15 (inclus). Cette information arrive avec `lot2/clients.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## La décision attendue

Quels **clients** et quels **produits** réduisent la rentabilité commerciale de Medina Distribution ? Classez les clients et les produits par marge commerciale et par taux de marge (marge / ventes nettes), repérez ceux dont le taux d'avoir est le plus haut, et proposez à la direction **une** action chiffrée (par exemple : revoir le prix négocié d'un produit pour un client, ou traiter la cause des avoirs d'une famille).

## Les indicateurs (définitions exactes)

- **Montant facturé** (TND) : somme de quantite × prix_unitaire_negocie des lignes de facture acceptées
- **Avoirs** (TND) : somme des montants des avoirs EMIS acceptés (RETOUR et REMISE)
- **Ventes nettes** (TND) : montant facturé − avoirs
- **Coût d'achat des unités nettes** (TND) : (cartons facturés − cartons repris par avoir RETOUR) × coût d'achat unitaire, produit par produit
- **Marge commerciale** (TND) : ventes nettes − coût d'achat des unités nettes
- **Taux d'avoir** (ratio) : avoirs / montant facturé (en montant)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les dernières factures du 30 juin ; CL04 change de segment le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Le 20 juillet, Medina Distribution émet un avoir pour une ligne facturée le 30 juin à la Supérette El Amel (CL04). Depuis le 15 juillet, CL04 est passé du segment « épicerie » au segment « grande surface ». L'avoir compte-t-il dans le segment de la facture (épicerie) ou dans le segment valable le jour de l'avoir (grande surface) ?

- A : segment de la facture d'origine (l'avoir corrige une vente : il suit la version du client valable à la date de la facture).
- B : segment valable à la date de l'avoir (chaque mouvement suit sa propre date).

**Décision de la direction pour cette mission :** A. Un avoir corrige une ligne de facture : il est rattaché à la version du client valable à la date de la **facture d'origine** (`fact_avoir.date_facture_key`), pour que la rentabilité d'un segment compte ses propres corrections. Il reste compté dans le mois de **sa** date (`fact_avoir.date_key`). Attention : la mission 00 a fait le choix inverse (B) pour les retours.

## Les trois écrans de l'application

1. **Vue direction** — les six indicateurs et les ventes nettes par mois et par segment (barres empilées) ; les filtres client, segment, famille et produit montrent qui fait baisser la marge.
2. **Détail par client** — chaque client avec ses versions : CL04 en « épicerie » jusqu'au 2026-07-14, puis « grande surface » ; les avoirs restent dans le segment de leur facture.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; avoirs ignorés.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux de remise négociée = 1 − montant facturé / (quantité × prix tarif), par client et par produit.
2. Nouvelle règle : un avoir émis plus de 30 jours après la date de la facture est refusé → nouveau motif `avoir_hors_delai` dans `rejets.csv`.
3. Changement historique : le coût d'achat de l'huile végétale (PR03) augmente de 8 % au 2026-08-01 ; le coût doit dépendre de la date (dimension produit historisée ou coût stocké dans le fait).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M03 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
