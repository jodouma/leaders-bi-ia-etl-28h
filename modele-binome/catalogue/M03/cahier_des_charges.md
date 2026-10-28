# Cahier des charges — Mission 03 : Distribution B2B

Client fictif : **Medina Distribution**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une ligne de facture.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `factures.csv` | csv | Lignes de facture exportées du logiciel de facturation (UTF-8, séparateur `;`). | formats de prix et de dates mélangés ; doublons ; identifiants vides ou en conflit ; codes inconnus ; quantités invalides ; lot2 : recopie des dernières factures du 30 juin |
| `couts.xlsx` | excel | Feuille `Articles` (en-têtes à la ligne 3) + feuille `Familles`. | titre au-dessus du tableau ; nombres stockés comme texte |
| `clients.json` | json | Fichier clients avec l'historique des segments. | segments écrits avec des majuscules ou des espaces ; lot2 : une deuxième version pour CL04 (« grande surface » au 2026-07-15) |
| `avoirs.sqlite` | sqlite | Base de la gestion commerciale : tables `avoir`, `motif_avoir`, `parametre`. | avoirs annulés ou en brouillon ; avoirs vers une ligne inconnue ; lot2 : recopie des avoirs depuis le 20 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `F26-90003-9` deux fois avec des quantités différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `ligne_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | produit `PR99`, client `CL99`, avoir vers `F26-00777-9` | rejet `cle_inconnue` |
| Format décimal | `18.280`, `18,280`, `18.28`, `18,28`, `1 240,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces (codes) | ` cl05 `, `Pr03`, ` pr07` | supprimer les espaces autour + majuscules |
| Casse / espaces (segment) | `Grande Surface`, `Épicerie ` | supprimer les espaces autour + minuscules |
| Quantité invalide | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `Sélima`, `Hédi`, `Supérette` | lire les fichiers en UTF-8 |
| Avoir non émis | `statut` = `ANNULE` ou `BROUILLON` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les dernières factures du 30 juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel ou ligne d'origine inconnue |
| `quantite_invalide` | quantité nulle, négative ou non entière |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `ligne_id` vide → `id_manquant` ;
3. `ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. client ou produit absent des référentiels → `cle_inconnue` ;
5. quantité non entière ou ≤ 0 → `quantite_invalide` ;
6. `ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Avoirs : statut ≠ `EMIS` ignoré → `numero_avoir` déjà chargé = ignoré → `ref_ligne_facture` absente de `fact_facture` = `cle_inconnue` (numero_ligne = `avoir.id`).

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `factures.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Montant facturé d'une ligne = quantité × prix **négocié** de la ligne (souvent inférieur au prix tarif).
- Coût d'achat = `Coût d'achat (TND)` du fichier des coûts (fixe sur 2026), pour chaque carton facturé.
- Un avoir prend le produit **et la version du client** de sa ligne de facture d'origine : `client_key` et `date_facture_key` sont recopiés de `fact_facture`. Son `date_key` est la **date de l'avoir**.
- Avoir `RETOUR` : `quantite` = cartons repris (> 0) ; leur coût d'achat est retiré du coût des unités nettes.
- Avoir `REMISE` : `quantite` = 0 ; il baisse les ventes nettes sans changer le coût d'achat.
- Montant d'un avoir = `montant_ht` converti en millimes (arrondi au millime).
- `famille` de `dim_produit` = libellé de la feuille Familles (ex. `LAI` → `Produits laitiers`).
- `segment` de `dim_client` = segment du JSON, sans espaces autour et en minuscules (`Grande Surface` → `grande surface`).
- `dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).

## 6. Entrepôt `outputs/entrepot.sqlite` (modèle en étoile)

Charger les dimensions **avant** les faits. Clés techniques `*_key` entières ; clés métier `*_id` en texte. Montants en **millimes entiers** (type INTEGER). Les clés étrangères sont déclarées (`FOREIGN KEY`).

### `dim_date` — dimension

Calendrier : une ligne par jour de la période chargée.

| Colonne | Type | Règle |
|---|---|---|
| `date_key` | INTEGER (clé) | Clé du jour au format AAAAMMJJ (ex. 20260304). |
| `date_complete` | TEXT | Date ISO AAAA-MM-JJ. |
| `annee` | INTEGER | Année. |
| `mois` | INTEGER | Mois de 1 à 12. |
| `jour` | INTEGER | Jour du mois. |

### `dim_produit` — dimension

Articles : un produit par ligne (feuilles Articles + Familles).

| Colonne | Type | Règle |
|---|---|---|
| `produit_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code article normalisé (strip + majuscules), ex. `PR03`. |
| `nom` | TEXT | Désignation et conditionnement. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Produits laitiers`. |
| `cout_achat_millimes` | INTEGER | Coût d'achat d'un carton en millimes. |
| `prix_tarif_millimes` | INTEGER | Prix tarif d'un carton (avant négociation) en millimes. |

### `dim_client` — dimension scd2

Clients avec historique du segment (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `client_key` | INTEGER (clé) | Clé technique d'une VERSION de client. |
| `client_id` | TEXT | Code client, ex. `CL04` (plusieurs versions possibles). |
| `nom` | TEXT | Raison sociale. |
| `segment` | TEXT | Segment de cette version : `épicerie`, `restaurant`, `grande surface` ou `hôtel`. |
| `region` | TEXT | Région de livraison. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_facture` — fait

Une ligne de facture acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `ligne_id` | TEXT (clé) | Identifiant de la ligne de facture (clé métier unique). |
| `facture_id` | TEXT | Numéro de la facture. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la facture. |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit facturé. |
| `client_key` | INTEGER → `dim_client.client_key` | Version du client valable à la date de la facture. |
| `quantite` | INTEGER | Cartons facturés (entier > 0). |
| `prix_negocie_millimes` | INTEGER | Prix négocié d'un carton en millimes. |
| `montant_facture_millimes` | INTEGER | quantite × prix_negocie_millimes. |

### `fact_avoir` — fait

Un avoir EMIS de la gestion commerciale, rattaché à une ligne de facture.

| Colonne | Type | Règle |
|---|---|---|
| `avoir_id` | TEXT (clé) | Numéro de l'avoir (`numero_avoir`), clé métier unique. |
| `ligne_id` | TEXT → `fact_facture.ligne_id` | Ligne de facture corrigée. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de l'avoir (mois de comptage). |
| `date_facture_key` | INTEGER → `dim_date.date_key` | Jour de la facture d'origine (choisit la version du client). |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit de la ligne de facture. |
| `client_key` | INTEGER → `dim_client.client_key` | Version du client de la ligne de facture (règle A). |
| `type_avoir` | TEXT | `RETOUR` (cartons repris) ou `REMISE` (geste sur le prix). |
| `quantite` | INTEGER | Cartons repris (0 pour une REMISE). |
| `montant_millimes` | INTEGER | Montant de l'avoir en millimes. |


## 7. Historique (SCD2) sur `dim_client`

Le client CL04 (Supérette El Amel) passe du segment « épicerie » au segment « grande surface » le 2026-07-15 (inclus). Cette information arrive avec `lot2/clients.json`.

- Une ligne par version : `valid_from` **inclus**, `valid_to` **exclu**, `valid_to` vide (NULL) = version courante.
- La première version commence à la date `valide_depuis` donnée par la source.
- Une nouvelle version **ferme** la précédente : `valid_to` de l'ancienne = `valid_from` de la nouvelle.
- Un fait est rattaché à la version valable **à la date du fait** : un fait ancien garde l'ancienne version.
- **Pour un avoir, la date qui choisit la version est la date de sa facture d'origine** (`fact_avoir.date_facture_key`), pas la date de l'avoir (voir § 12).

## 8. Chargement incrémental et rejeu

- `initial` : entrepôt neuf + `lot1`.
- `increment` : ajoute `lot2` sans effacer `lot1` (nouvelles lignes, nouvelle version SCD2, calendrier prolongé).
- `rejeu` : relancer `lot2` ne change **rien** (aucune ligne ajoutée, mêmes rejets). Un fait dont la clé métier est déjà dans l'entrepôt est ignoré.
- `lot2` contient volontairement des lignes de `lot1` (chevauchement d'export) : elles ne créent pas de doublon.

## 9. Indicateurs (définitions exactes)

| Indicateur | Unité | Formule exacte |
|---|---|---|
| Montant facturé | TND (stocké en millimes) | somme de quantite × prix_unitaire_negocie des lignes de facture acceptées |
| Avoirs | TND (stocké en millimes) | somme des montants des avoirs EMIS acceptés (RETOUR et REMISE) |
| Ventes nettes | TND (stocké en millimes) | montant facturé − avoirs |
| Coût d'achat des unités nettes | TND (stocké en millimes) | (cartons facturés − cartons repris par avoir RETOUR) × coût d'achat unitaire, produit par produit |
| Marge commerciale | TND (stocké en millimes) | ventes nettes − coût d'achat des unités nettes |
| Taux d'avoir | ratio | avoirs / montant facturé (en montant) |
| Cartons nets | nombre | cartons facturés − cartons repris |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (faits et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_facture` : quantite, montant_facture_millimes; `fact_avoir` : quantite, montant_millimes; `dim_produit` : cout_achat_millimes, prix_tarif_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par client », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M03 --etape initial     # après le lot 1
python -m controles.verifier --mission M03 --etape increment   # après le lot 2
python -m controles.verifier --mission M03 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M03 --etape export
python -m controles.verifier --mission M03 --etape tout
```

## 12. Règle à clarifier

Le 20 juillet, Medina Distribution émet un avoir pour une ligne facturée le 30 juin à la Supérette El Amel (CL04). Depuis le 15 juillet, CL04 est passé du segment « épicerie » au segment « grande surface ». L'avoir compte-t-il dans le segment de la facture (épicerie) ou dans le segment valable le jour de l'avoir (grande surface) ? — **Décision :** A. Un avoir corrige une ligne de facture : il est rattaché à la version du client valable à la date de la **facture d'origine** (`fact_avoir.date_facture_key`), pour que la rentabilité d'un segment compte ses propres corrections. Il reste compté dans le mois de **sa** date (`fact_avoir.date_key`). Attention : la mission 00 a fait le choix inverse (B) pour les retours.

Options étudiées :

- A : segment de la facture d'origine (l'avoir corrige une vente : il suit la version du client valable à la date de la facture).
- B : segment valable à la date de l'avoir (chaque mouvement suit sa propre date).

Conséquence dans l'entrepôt : `fact_avoir.client_key` = `client_key` de la ligne de facture ; `fact_avoir.date_key` = date de l'avoir (mois de l'avoir) ; `fact_avoir.date_facture_key` = date de la facture (contrôle SCD2).

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux de remise négociée = 1 − montant facturé / (quantité × prix tarif), par client et par produit.
2. Nouvelle règle : un avoir émis plus de 30 jours après la date de la facture est refusé → nouveau motif `avoir_hors_delai` dans `rejets.csv`.
3. Changement historique : le coût d'achat de l'huile végétale (PR03) augmente de 8 % au 2026-08-01 ; le coût doit dépendre de la date (dimension produit historisée ou coût stocké dans le fait).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — les six indicateurs et les ventes nettes par mois et par segment (barres empilées) ; les filtres client, segment, famille et produit montrent qui fait baisser la marge.
2. **Détail par client** — chaque client avec ses versions : CL04 en « épicerie » jusqu'au 2026-07-14, puis « grande surface » ; les avoirs restent dans le segment de leur facture.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; avoirs ignorés.

Démonstration conseillée :

1. **Vue direction** — Montrer les six indicateurs sur toute la période, puis lire le graphique ventes nettes par mois et par segment. Choisir le filtre Produit = `PR03` (huile végétale), puis Client = `CL05` : la marge commerciale devient négative. Dire en une phrase ce que cela veut dire.
2. **Détail par client** — Ouvrir CL04 : deux versions (« épicerie » valable jusqu'au 2026-07-15 exclu, puis « grande surface » courante). Montrer que l'avoir du 20 juillet sur la facture du 30 juin est compté dans « épicerie » (règle A) et dans le mois de juillet.
3. **Qualité des données** — Montrer les lignes lues, les doublons ignorés, les lignes déjà chargées au lot 2 et les rejets par motif ; relier un rejet `cle_inconnue` à sa ligne dans `rejets.csv`.

## 15. La décision attendue

Quels **clients** et quels **produits** réduisent la rentabilité commerciale de Medina Distribution ? Classez les clients et les produits par marge commerciale et par taux de marge (marge / ventes nettes), repérez ceux dont le taux d'avoir est le plus haut, et proposez à la direction **une** action chiffrée (par exemple : revoir le prix négocié d'un produit pour un client, ou traiter la cause des avoirs d'une famille).
