# Mission 01 — Réseau de magasins

**Client fictif :** Carthage Market (réseau de sept supérettes de quartier, trois magasins propres et quatre magasins franchisés). **Grain du fait :** une ligne de ticket de caisse.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Carthage Market est une enseigne fictive de supérettes : épicerie, boissons, produits laitiers, hygiène et entretien. Le réseau compte sept magasins. Trois sont des magasins **propres** (gérés par l'enseigne) et quatre sont **franchisés** (gérés par un commerçant partenaire qui utilise la marque). Les caisses exportent les lignes de ticket dans un CSV, avec les codes promotion et les remises. Le catalogue (prix, coût d'achat, famille) vit dans un classeur Excel, la liste des magasins dans un fichier JSON et les retours clients dans une petite base SQLite. La direction veut savoir quels magasins et quels produits font vraiment les ventes et la marge. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nous ouvrons de plus en plus de magasins en franchise. Avant d'aller plus loin, je veux savoir quels magasins et quels produits apportent les ventes et la marge. Par magasin, par région, par famille et par mois : les ventes nettes, la marge sur coût d'achat, la part des franchisés dans les ventes nettes et le taux de retour. Dites-moi aussi quelles lignes vous avez dû écarter, et pourquoi.
> 
> Pour information : le 15 juillet, le magasin de Hammamet quitte la région Cap Bon et rejoint la région Sahel. Les chiffres du premier semestre doivent rester dans Cap Bon.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Carthage Market)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_produit, dim_magasin, fact_vente, fact_retour).
3. Le lot 2 chargé, l'historique gardé (Le magasin HAM (Hammamet, franchisé) passe de la région « Cap Bon » à la région « Sahel » le 2026-07-15 (inclus). Cette information arrive avec `lot2/magasins.json`.), un rejeu sans doublon.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Ventes nettes** (TND) : ventes brutes − retours
- **Marge sur coût d'achat** (TND) : ventes nettes − coût d'achat des unités nettes
- **Part des franchisés** (ratio) : ventes nettes des magasins franchisés / ventes nettes totales
- **Taux de retour** (ratio) : retours / ventes brutes (en montant)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les 29-30 juin ; HAM change de région le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Une ligne vendue en promotion (code `RAMADAN26`, remise de 10 %) : la marge se calcule-t-elle sur le prix payé (après remise) ou sur le prix du catalogue, la remise étant suivie à part comme une dépense de promotion ?

- A : remise déduite **avant** la marge. Ventes brutes = quantité × prix − remise ; la remise baisse les ventes et la marge.
- B : remise déduite **après** la marge. Ventes brutes au prix catalogue ; la marge ignore la remise ; un indicateur « remises » est suivi à part.

**Décision de la direction pour cette mission :** A. Les ventes brutes sont le montant réellement payé (remise déduite), donc la marge sur coût d'achat tient compte de la remise. L'indicateur « Remises » reste calculé à part pour montrer combien les promotions ont coûté. Un retour rembourse le prix payé, remise comprise.

## Les trois écrans de l'application

1. **Vue direction** — les quatre indicateurs (ventes nettes, marge sur coût d'achat, part des franchisés, taux de retour) et les ventes nettes par mois et par région ; filtres période, magasin, région, type.
2. **Détail par magasin** — chaque magasin avec ses versions : HAM en Cap Bon jusqu'au 2026-07-14, puis en Sahel ; ventes nettes et marge par version et par mois.
3. **Qualité des données** — lignes lues, gardées, déjà chargées, rejetées par motif et par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : marge par famille et taux de marge = marge sur coût d'achat / ventes nettes, par famille de produits.
2. Changement historique : le magasin SOU (Sousse, propre) devient franchisé le 2026-08-01 → le type devient lui aussi historisé (nouvelle version de `dim_magasin`) et la part des franchisés change à partir d'août.
3. Nouvelle région : un huitième magasin, KAI (Kairouan, franchisé), ouvre le 2026-09-01 dans une nouvelle région « Centre » (lot 3 : nouveau magasin, nouvelle région, aucune ligne avant son ouverture).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M01 --etape tout
python -m pytest
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
