# Cahier des charges — Mission 00 : Solen Commerce 360

Client fictif : **Maison Zitouna**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une ligne de ticket de caisse.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `ventes.csv` | csv | Lignes de tickets exportées des caisses (UTF-8, séparateur `;`). | formats de prix et de dates mélangés ; doublons ; identifiants vides ou en conflit ; codes inconnus ; quantités invalides ; lot2 : recopie des 29 et 30 juin |
| `catalogue.xlsx` | excel | Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`. | titre au-dessus du tableau ; nombres stockés comme texte |
| `boutiques.json` | json | Référentiel des boutiques avec l'historique des zones. | lot2 : une deuxième version pour NBE (Nord-Est au 2026-07-15) |
| `operations.sqlite` | sqlite | Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`. | retours annulés ; retours vers une ligne inconnue ; lot2 : recopie des retours depuis le 20 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `TK10037-9` deux fois avec des quantités différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `ligne_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | produit `P99`, boutique `BZT`, retour vers `TK1999-1` | rejet `cle_inconnue` |
| Format décimal | `18.500`, `18,500`, `18.5`, `18,5`, `1 240,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` tun `, `Sfx`, ` p06` | supprimer les espaces autour + majuscules |
| Quantité invalide | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `espèces`, `chèque` | lire les fichiers en UTF-8 |
| Retour annulé | `statut = 'ANNULE'` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les ventes des 29-30 juin | ignorer : la clé métier existe déjà |

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
4. boutique ou produit absent des référentiels → `cle_inconnue` ;
5. quantité non entière ou ≤ 0 → `quantite_invalide` ;
6. `ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Retours : `ANNULE` ignoré → `ref_ligne_ticket` absente de `fact_vente` = `cle_inconnue` (numero_ligne = `retour.id`) → `numero_retour` déjà chargé = ignoré.

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `ventes.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Montant brut d'une ligne = quantité × prix du **ticket** (une promotion peut donner un prix inférieur au catalogue).
- Coût d'achat = `cout_achat` du catalogue (fixe sur 2026).
- Un retour prend le produit de sa ligne de vente d'origine, la boutique `code_boutique` et la **date du retour** (heure ignorée).
- Montant d'un retour = `montant_rembourse` converti en millimes (arrondi au millime).
- `famille` de `dim_produit` = libellé de la feuille Familles (ex. `DAT` → `Dattes`).
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

Catalogue : un produit par ligne (feuilles Catalogue + Familles).

| Colonne | Type | Règle |
|---|---|---|
| `produit_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code produit normalisé (strip + majuscules), ex. `P01`. |
| `nom` | TEXT | Désignation. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Huiles`. |
| `prix_millimes` | INTEGER | Prix de vente du catalogue en millimes. |
| `cout_achat_millimes` | INTEGER | Coût d'achat unitaire en millimes. |

### `dim_boutique` — dimension scd2

Boutiques avec historique de la zone commerciale (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `boutique_key` | INTEGER (clé) | Clé technique d'une VERSION de boutique. |
| `boutique_id` | TEXT | Code boutique, ex. `NBE` (plusieurs versions possibles). |
| `nom` | TEXT | Nom de la boutique. |
| `zone` | TEXT | Zone commerciale de cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_vente` — fait

Une ligne de ticket acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `ligne_id` | TEXT (clé) | Identifiant de la ligne de ticket (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la vente. |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit vendu. |
| `boutique_key` | INTEGER → `dim_boutique.boutique_key` | Version de la boutique valable à la date de la vente. |
| `quantite` | INTEGER | Unités vendues (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix du ticket en millimes (promotion possible). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes. |

### `fact_retour` — fait

Un retour VALIDE de la base opérationnelle.

| Colonne | Type | Règle |
|---|---|---|
| `retour_id` | TEXT (clé) | Numéro du retour (`numero_retour`), clé métier unique. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour du retour (heure ignorée). |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit de la ligne de vente d'origine. |
| `boutique_key` | INTEGER → `dim_boutique.boutique_key` | Version de la boutique valable à la date du RETOUR. |
| `quantite` | INTEGER | Unités retournées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes. |


## 7. Historique (SCD2) sur `dim_boutique`

La boutique NBE (Nabeul) passe de la zone « Cap Bon » à la zone « Nord-Est » le 2026-07-15 (inclus). Cette information arrive avec `lot2/boutiques.json`.

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
| Ventes brutes | TND (stocké en millimes) | somme de quantite × prix_unitaire des lignes de ticket acceptées |
| Retours | TND (stocké en millimes) | somme des montants remboursés des retours VALIDE acceptés |
| Ventes nettes | TND (stocké en millimes) | ventes brutes − retours |
| Coût d'achat des unités nettes | TND (stocké en millimes) | (unités vendues − unités retournées) × coût d'achat unitaire, produit par produit |
| Marge sur coût d'achat | TND (stocké en millimes) | ventes nettes − coût d'achat des unités nettes |
| Taux de retour | ratio | retours / ventes brutes (en montant) |
| Unités nettes | nombre | unités vendues − unités retournées |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (faits et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_vente` : quantite, montant_brut_millimes; `fact_retour` : quantite, montant_millimes; `dim_produit` : prix_millimes, cout_achat_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par boutique », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission tronc-commun --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission tronc-commun --etape initial     # après le lot 1
python -m controles.verifier --mission tronc-commun --etape increment   # après le lot 2
python -m controles.verifier --mission tronc-commun --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission tronc-commun --etape export
python -m controles.verifier --mission tronc-commun --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** Un client rapporte le 20 juillet un produit acheté le 30 juin à Nabeul. Le retour compte-t-il dans la zone Cap Bon (zone de la vente) ou Nord-Est (zone le jour du retour) ?

**Options étudiées :**

- A : zone de la vente d'origine (il faut relier le retour à la version de la vente).
- B : zone valable à la date du retour (chaque mouvement suit sa propre date).

**Décision de la direction :** B. Chaque mouvement (vente ou retour) est rattaché à la version de la boutique valable à SA date et compté dans SON mois. C'est la même règle que pour les ventes.

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : panier moyen net = ventes nettes / nombre de tickets distincts.
2. Nouvelle règle : un retour plus de 30 jours après la vente est refusé → nouveau motif `retour_hors_delai`.
3. Changement historique : SFX passe en zone « Centre-Est » le 2026-08-01 (troisième version dans `dim_boutique`).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — les cinq indicateurs et les ventes nettes par mois et par zone (barres empilées).
2. **Détail par boutique** — chaque boutique avec ses versions : NBE en Cap Bon jusqu'au 2026-07-14, puis Nord-Est.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; une ligne par chargement (lot 1, lot 2, puis le rejeu du lot 2 à 0 ajout).
