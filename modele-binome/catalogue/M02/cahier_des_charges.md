# Cahier des charges — Mission 02 : E-commerce · Souk Express

Client fictif : **Souk Express**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une ligne de commande en ligne.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `commandes.csv` | csv | Lignes de commande exportées du site (séparateur `;`). Lot 1 en UTF-8, **lot 2 en Windows-1252 (`cp1252`)**. | formats de montants et de dates mélangés ; remise vide, `0` ou montant ; doublons ; identifiants vides ou en conflit ; codes inconnus ; quantités invalides ; lot2 : fichier en cp1252 (lu en UTF-8, il plante sur les accents : `août`, `Gabès`) ; lot2 : recopie des commandes des 29 et 30 juin |
| `produits.xlsx` | excel | Feuille `Produits` (titre au-dessus, en-têtes à la ligne 3). | titre au-dessus du tableau ; nombres stockés comme texte |
| `canaux.json` | json | Référentiel des canaux de vente avec l'historique de leur famille. | lot2 : une deuxième version pour VSO (marketplace au 2026-07-15) |
| `operations.sqlite` | sqlite | Base opérationnelle du service client : tables `remboursement`, `motif_remboursement`, `parametre`. | statuts EN_COURS et REFUSE (à ignorer) ; remboursements vers une ligne inconnue ; pas de canal dans la table : il vient de la commande ; lot2 : recopie des remboursements depuis le 20 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `C150037-9` deux fois avec des quantités différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `ligne_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | produit `X15`, canal `TIK`, remboursement vers `C109999-1` | rejet `cle_inconnue` |
| Format décimal | `32.500`, `32,500`, `32.5`, `32,5`, `1 240,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Remise vide | `remise` vide, `0`, `0.000` | remise = 0 millime (ce n'est pas un rejet) |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` app `, `Web`, ` p12` | supprimer les espaces autour + majuscules |
| Quantité invalide | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | lot2 : `Gabès` écrit en Windows-1252 | lire `lot1/commandes.csv` en UTF-8 et `lot2/commandes.csv` en `cp1252` (sinon erreur `UnicodeDecodeError`) |
| Remboursement non payé | `statut` = `EN_COURS` ou `REFUSE` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les commandes du 30 juin | ignorer : la clé métier existe déjà |

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
4. canal ou produit absent des référentiels → `cle_inconnue` ;
5. quantité non entière ou ≤ 0 → `quantite_invalide` ;
6. `ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Remboursements : statut autre que `REMBOURSE` ignoré → `ref_ligne_commande` absente de `fact_commande` = `cle_inconnue` (numero_ligne = `remboursement.id`) → `numero_remboursement` déjà chargé = ignoré.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `commandes.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Montant brut d'une ligne = quantité × prix unitaire **payé** (une promotion peut donner un prix inférieur au catalogue).
- `remise` = montant en **TND** de la remise accordée sur **la ligne entière** (pas par unité, pas un pourcentage). Vide = 0. Elle est stockée telle quelle en millimes dans `fact_commande.remise_millimes`.
- Un remboursement prend le produit et le **canal** de sa ligne de commande d'origine (la table `remboursement` n'a pas de canal), et la **date du remboursement** (heure ignorée).
- Montant d'un remboursement = `montant` converti en millimes (arrondi au millime). Il est déjà net de la remise : on ne retire rien d'autre.
- Nombre de commandes = nombre de `commande_id` distincts parmi les lignes de commande acceptées. Par catégorie, une commande qui contient deux catégories compte dans chacune.
- Panier moyen net = CA net / nombre de commandes, arrondi au millime (pour un groupe sans commande : vide).
- `categorie` de `dim_produit` = colonne Catégorie du classeur, espaces supprimés (ex. `Beauté`).
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

Catalogue : un produit par ligne (feuille Produits).

| Colonne | Type | Règle |
|---|---|---|
| `produit_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code produit normalisé (strip + majuscules), ex. `P12`. |
| `nom` | TEXT | Libellé du produit. |
| `categorie` | TEXT | Catégorie (espaces supprimés), ex. `Beauté`. |
| `prix_millimes` | INTEGER | Prix public du catalogue en millimes. |
| `cout_millimes` | INTEGER | Coût de revient unitaire en millimes. |

### `dim_canal` — dimension scd2

Canaux de vente avec historique de la famille de canal (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `canal_key` | INTEGER (clé) | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `VSO` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du canal. |
| `famille` | TEXT | Famille de cette version : `site`, `application`, `marketplace` ou `réseaux sociaux`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_commande` — fait

Une ligne de commande acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `ligne_id` | TEXT (clé) | Identifiant de la ligne de commande (clé métier unique). |
| `commande_id` | TEXT | Identifiant de la commande (sert à compter les commandes distinctes). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la commande. |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit commandé. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Version du canal valable à la date de la commande. |
| `quantite` | INTEGER | Unités commandées (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix unitaire payé en millimes (promotion possible). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes. |
| `remise_millimes` | INTEGER | Remise de la ligne entière en millimes (0 si vide). |

### `fact_remboursement` — fait

Un remboursement au statut REMBOURSE de la base opérationnelle.

| Colonne | Type | Règle |
|---|---|---|
| `remboursement_id` | TEXT (clé) | Numéro du remboursement (`numero_remboursement`), clé métier unique. |
| `ligne_id` | TEXT → `fact_commande.ligne_id` | Ligne de commande remboursée. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour du remboursement (heure ignorée). |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit de la ligne de commande d'origine. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Version du canal DE LA COMMANDE valable à la date du REMBOURSEMENT. |
| `quantite` | INTEGER | Unités remboursées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes. |


## 7. Historique (SCD2) sur `dim_canal`

Le canal VSO (vitrine sociale) passe de la famille « réseaux sociaux » à la famille « marketplace » le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.

- Une ligne par version : `valid_from` **inclus**, `valid_to` **exclu**, `valid_to` vide (NULL) = version courante.
- La première version commence à la date `valide_depuis` donnée par la source.
- Une nouvelle version **ferme** la précédente : `valid_to` de l'ancienne = `valid_from` de la nouvelle.
- Un fait est rattaché à la version valable **à la date du fait** : un fait ancien garde l'ancienne version.

## 8. Chargement incrémental et rejeu

- `initial` : entrepôt neuf + `lot1`.
- `increment` : ajoute `lot2` sans effacer `lot1` (nouvelles lignes, nouvelle version SCD2, calendrier prolongé).
- `rejeu` : relancer `lot2` ne change **rien** (aucune ligne ajoutée, mêmes rejets). Un fait dont la clé métier est déjà dans l'entrepôt est ignoré.
- `lot2` contient volontairement des lignes de `lot1` (chevauchement d'export) : elles ne créent pas de doublon.

## 9. Indicateurs (définitions exactes)

| Indicateur | Unité | Formule exacte |
|---|---|---|
| CA brut | TND (stocké en millimes) | somme de quantite × prix_unitaire des lignes de commande acceptées |
| Remises | TND (stocké en millimes) | somme des remises (TND) des lignes de commande acceptées |
| Remboursements | TND (stocké en millimes) | somme des montants des remboursements au statut REMBOURSE acceptés |
| CA net | TND (stocké en millimes) | CA brut − remises − remboursements |
| Nombre de commandes | nombre | nombre de `commande_id` distincts parmi les lignes de commande acceptées |
| Panier moyen net | TND (stocké en millimes) | CA net / nombre de commandes distinctes, arrondi au millime |
| Unités nettes | nombre | unités commandées − unités remboursées |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (faits et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_commande` : quantite, montant_brut_millimes, remise_millimes; `fact_remboursement` : quantite, montant_millimes; `dim_produit` : prix_millimes, cout_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par canal », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M02 --etape initial     # après le lot 1
python -m controles.verifier --mission M02 --etape increment   # après le lot 2
python -m controles.verifier --mission M02 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M02 --etape export
python -m controles.verifier --mission M02 --etape tout
```

## 12. Règle à clarifier

Une cliente a commandé le 30 juin sur la vitrine sociale (VSO, alors « réseaux sociaux ») et a été remboursée le 20 juillet (VSO est alors « marketplace »). Dans quelle famille compte ce remboursement ? — **Décision :** B. Chaque mouvement (ligne de commande ou remboursement) est rattaché à la version du canal valable à SA date et compté dans SON mois. Le remboursement du 20 juillet compte donc en « marketplace », en juillet. C'est la même règle que pour les commandes, et c'est ce que vérifie `controles/verifier.py`.

Options étudiées :

- A : famille valable à la date de la **commande** (« réseaux sociaux ») : il faut relier le remboursement à la version de la commande.
- B : famille valable à la date du **remboursement** (« marketplace ») : chaque mouvement suit sa propre date.

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux de remise = remises / CA brut, par canal et par famille.
2. Nouvelle règle : un remboursement plus de 30 jours après la commande est refusé → nouveau motif `remboursement_hors_delai`.
3. Changement historique : l'application (APP) passe en famille « site » le 2026-08-01 (fusion des deux équipes) : troisième version dans `dim_canal`.

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — les cinq indicateurs (CA brut, remises, remboursements, CA net, panier moyen net) et le CA net par mois et par famille de canal (barres empilées) ; filtres période, canal, famille.
2. **Détail par canal** — chaque canal avec ses versions : VSO en « réseaux sociaux » jusqu'au 2026-07-14, puis « marketplace » ; indicateurs par famille et par mois.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; remboursements ignorés.

Démonstration conseillée : (1) Vue direction, toute la période, puis filtre famille « marketplace » : le CA brut est élevé, le CA net beaucoup moins ; (2) Détail par canal, VSO : deux versions, et le remboursement du 20 juillet compté en « marketplace » ; (3) Qualité des données : rejets par motif et par lot, remboursements `EN_COURS`/`REFUSE` ignorés.
