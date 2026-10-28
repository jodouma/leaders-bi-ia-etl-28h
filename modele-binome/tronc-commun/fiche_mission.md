# Mission 00 — Solen Commerce 360

**Client fictif :** Maison Zitouna (réseau de trois boutiques de produits du terroir : huile d'olive, olives, dattes, coffrets). **Grain du fait :** une ligne de ticket de caisse.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Maison Zitouna vend de l'huile d'olive, des olives, des dattes et des coffrets cadeaux dans trois boutiques : Tunis Centre (zone Grand Tunis), Nabeul (zone Cap Bon) et Sfax (zone Sud). Les caisses exportent les tickets dans un CSV, le catalogue vit dans un classeur Excel, la liste des boutiques dans un fichier JSON et les retours clients dans une petite base SQLite. Personne ne sait dire combien l'entreprise gagne vraiment après les retours. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Les ventes montent, mais où passe la marge ? Je veux, par boutique, par zone et par mois : les ventes brutes, les retours, les ventes nettes, la marge sur coût d'achat et le taux de retour. Et je veux pouvoir faire confiance aux chiffres : dites-moi aussi ce que vous avez dû écarter, et pourquoi.
> 
> Pour information : à partir du 15 juillet, la boutique de Nabeul passe de la zone Cap Bon à la zone Nord-Est. Les chiffres du premier semestre doivent rester dans Cap Bon.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Maison Zitouna)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_produit, dim_boutique, fact_vente, fact_retour).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. La boutique NBE (Nabeul) passe de la zone « Cap Bon » à la zone « Nord-Est » le 2026-07-15 (inclus). Cette information arrive avec `lot2/boutiques.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Ventes brutes** (TND) : somme de quantite × prix_unitaire des lignes de ticket acceptées
- **Retours** (TND) : somme des montants remboursés des retours VALIDE acceptés
- **Ventes nettes** (TND) : ventes brutes − retours
- **Marge sur coût d'achat** (TND) : ventes nettes − coût d'achat des unités nettes
- **Taux de retour** (ratio) : retours / ventes brutes (en montant)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les 29-30 juin ; NBE change de zone le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Un client rapporte le 20 juillet un produit acheté le 30 juin à Nabeul. Le retour compte-t-il dans la zone Cap Bon (zone de la vente) ou Nord-Est (zone le jour du retour) ?

- A : zone de la vente d'origine (il faut relier le retour à la version de la vente).
- B : zone valable à la date du retour (chaque mouvement suit sa propre date).

**Décision de la direction pour cette mission :** B. Chaque mouvement (vente ou retour) est rattaché à la version de la boutique valable à SA date et compté dans SON mois. C'est la même règle que pour les ventes.

## Les trois écrans de l'application

1. **Vue direction** — les cinq indicateurs et les ventes nettes par mois et par zone (barres empilées).
2. **Détail par boutique** — chaque boutique avec ses versions : NBE en Cap Bon jusqu'au 2026-07-14, puis Nord-Est.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; une ligne par chargement (lot 1, lot 2, puis le rejeu du lot 2 à 0 ajout).

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : panier moyen net = ventes nettes / nombre de tickets distincts.
2. Nouvelle règle : un retour plus de 30 jours après la vente est refusé → nouveau motif `retour_hors_delai`.
3. Changement historique : SFX passe en zone « Centre-Est » le 2026-08-01 (troisième version dans `dim_boutique`).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission tronc-commun --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
