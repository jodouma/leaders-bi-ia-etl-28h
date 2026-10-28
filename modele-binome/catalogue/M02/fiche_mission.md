# Mission 02 — E-commerce · Souk Express

**Client fictif :** Souk Express (boutique en ligne tunisienne : mode, high-tech, beauté, maison, épicerie fine). **Grain du fait :** une ligne de commande en ligne.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Souk Express vend en ligne par six canaux : son site, son application mobile, deux places de marché partenaires (Bazar Lina, Sahel Market) et deux canaux sur les réseaux sociaux (la vitrine sociale et le groupe communauté). Le système de commande exporte les lignes de commande dans un CSV, les produits vivent dans un classeur Excel, la liste des canaux dans un fichier JSON et les remboursements clients dans une petite base SQLite. Chaque canal se dit « rentable », mais personne ne compte les remises et les remboursements. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nos places de marché font beaucoup de chiffre d'affaires, mais avec beaucoup de codes promo et de remboursements. Je veux savoir quels canaux nous font vraiment vendre une fois les remises et les remboursements enlevés. Par canal, par famille de canal et par mois : CA brut, remises, remboursements, CA net et panier moyen net. Dites-moi aussi ce que vous avez dû écarter, et pourquoi.
> 
> Pour information : à partir du 15 juillet, notre vitrine sociale (canal VSO) accueille des vendeurs partenaires. Elle passe de la famille « réseaux sociaux » à la famille « marketplace ». Les chiffres du premier semestre doivent rester dans « réseaux sociaux ».
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Souk Express)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_produit, dim_canal, fact_commande, fact_remboursement).
3. Le lot 2 chargé, l'historique gardé (Le canal VSO (vitrine sociale) passe de la famille « réseaux sociaux » à la famille « marketplace » le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.), un rejeu sans doublon.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **CA brut** (TND) : somme de quantite × prix_unitaire des lignes de commande acceptées
- **Remises** (TND) : somme des remises (TND) des lignes de commande acceptées
- **Remboursements** (TND) : somme des montants des remboursements au statut REMBOURSE acceptés
- **CA net** (TND) : CA brut − remises − remboursements
- **Panier moyen net** (TND) : CA net / nombre de commandes distinctes, arrondi au millime

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 (fichier en cp1252) ; recopie les 29-30 juin ; VSO change de famille le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Une cliente a commandé le 30 juin sur la vitrine sociale (VSO, alors « réseaux sociaux ») et a été remboursée le 20 juillet (VSO est alors « marketplace »). Dans quelle famille compte ce remboursement ?

- A : famille valable à la date de la **commande** (« réseaux sociaux ») : il faut relier le remboursement à la version de la commande.
- B : famille valable à la date du **remboursement** (« marketplace ») : chaque mouvement suit sa propre date.

**Décision de la direction pour cette mission :** B. Chaque mouvement (ligne de commande ou remboursement) est rattaché à la version du canal valable à SA date et compté dans SON mois. Le remboursement du 20 juillet compte donc en « marketplace », en juillet. C'est la même règle que pour les commandes, et c'est ce que vérifie `controles/verifier.py`.

## Les trois écrans de l'application

1. **Vue direction** — les cinq indicateurs (CA brut, remises, remboursements, CA net, panier moyen net) et le CA net par mois et par famille de canal (barres empilées) ; filtres période, canal, famille.
2. **Détail par canal** — chaque canal avec ses versions : VSO en « réseaux sociaux » jusqu'au 2026-07-14, puis « marketplace » ; indicateurs par famille et par mois.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; remboursements ignorés.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux de remise = remises / CA brut, par canal et par famille.
2. Nouvelle règle : un remboursement plus de 30 jours après la commande est refusé → nouveau motif `remboursement_hors_delai`.
3. Changement historique : l'application (APP) passe en famille « site » le 2026-08-01 (fusion des deux équipes) : troisième version dans `dim_canal`.

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M02 --etape tout
python -m pytest
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
