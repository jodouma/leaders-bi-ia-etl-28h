# Cahier des charges — Mission 07 : Abonnements FibreNet

Client fictif : **FibreNet**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une facture mensuelle d'abonnement (un abonnement × un mois facturé).** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `facturation.csv` | csv | Factures mensuelles exportées de la facturation (UTF-8, séparateur `;`). | formats de montants et de dates mélangés ; doublons ; identifiants vides ou en conflit ; comptes, offres ou abonnements inconnus ; nb_mois invalide ; lot2 : recopie des factures depuis le 10 juin |
| `comptes.xlsx` | excel | Feuille `Comptes` (titre au-dessus, en-têtes à la ligne 3). | titre au-dessus du tableau ; type de compte en casse variable ; lot2 : nouveaux comptes |
| `offres.json` | json | Catalogue des offres avec l'historique de gamme et de prix. | prix tantôt nombre, tantôt texte à virgule ; lot2 : une deuxième version pour FN-F300 au 2026-07-15 |
| `abonnements.sqlite` | sqlite | Base opérationnelle : tables `abonnement`, `motif_resiliation`, `parametre`. | abonnements annulés avant installation ; abonnements vers un compte inconnu ; abonnements résiliés en 2025 (aucun mois en 2026) ; lot2 : la base complète, résiliations de l'été comprises |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même facture deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `F26-900002` deux fois avec des `nb_mois` différents | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `facture_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | offre `FN-TV`, compte `C0999`, abonnement `AB09999` ; abonnement SQLite vers un compte inconnu | rejet `cle_inconnue` |
| Format décimal | `69.900`, `69,900`, `69.9`, `69,9`, `149,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-01`, `01/03/2026`, `1 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` c0042`, `fn-f100`, ` Entreprise ` | codes : espaces autour supprimés + majuscules ; type de compte et gamme : + minuscules |
| nb_mois invalide | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `Déco`, `Hôtel`, `Médina` dans les noms | lire les fichiers en UTF-8 |
| Abonnement annulé | `statut = 'ANNULE'` | ignorer (jamais installé : ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les factures émises depuis le 10 juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | compte, offre ou abonnement absent du référentiel |
| `quantite_invalide` | nb_mois nul, négatif ou non entier |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `facture_id` vide → `id_manquant` ;
3. `facture_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. compte absent de `comptes.xlsx`, offre absente de `offres.json` ou abonnement absent des abonnements acceptés → `cle_inconnue` ;
5. `nb_mois` non entier ou ≤ 0 → `quantite_invalide` ;
6. `facture_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Abonnements (lus **avant** les factures) : `ANNULE` ignoré → `num_compte` absent de `dim_compte` = `cle_inconnue` (numero_ligne = `abonnement.id`) → ligne-mois déjà chargée = ignorée.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `facturation.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Une facture est émise pour **chaque mois entamé** : le 1er du mois, ou le jour de début pour le premier mois. Montant = `nb_mois` × prix de la version de l'offre valable à la date de facture.
- `fact_facture` : version de l'offre valable à la **date de la facture** (la facture de juillet de Fibre 300, émise le 1er juillet, reste en confort à 89,900 TND).
- `fact_abonnement_mois` est **dérivée** de la base des abonnements (dates de début et de fin), pas du CSV : une ligne par abonnement et par mois où il est actif au moins un jour, rattachée au **dernier jour du mois** (`date_key`) et à la version de l'offre valable ce jour-là. Voir § 13.
- `date_fin` = dernier jour de service (inclus). Un abonnement résilié le dernier jour du mois est un départ de ce mois et n'est **pas** actif en fin de mois (voir la règle à clarifier).
- `type_compte` ∈ {`particulier`, `entreprise`} et `gamme` ∈ {`essentiel`, `confort`, `pro`} : en minuscules.
- Abonnés et MRR sont des stocks de fin de mois : on les lit **mois par mois** (agrégat `par_mois`). La somme sur plusieurs mois (total de la référence) compte des abonnés-mois, pas des abonnés.
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

### `dim_compte` — dimension

Comptes clients (feuille Comptes de `comptes.xlsx`).

| Colonne | Type | Règle |
|---|---|---|
| `compte_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `compte_id` | TEXT | Numéro de compte normalisé (strip + majuscules), ex. `C0042`. |
| `nom` | TEXT | Nom ou raison sociale (inventé). |
| `type_compte` | TEXT | `particulier` ou `entreprise` (strip + minuscules). |
| `ville` | TEXT | Ville du compte. |

### `dim_offre` — dimension scd2

Offres avec l'historique de la gamme et du prix mensuel (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `offre_key` | INTEGER (clé) | Clé technique d'une VERSION d'offre. |
| `offre_id` | TEXT | Code de l'offre, ex. `FN-F300` (plusieurs versions possibles). |
| `nom` | TEXT | Nom commercial. |
| `gamme` | TEXT | `essentiel`, `confort` ou `pro` pour cette version (minuscules). |
| `prix_mensuel_millimes` | INTEGER | Prix mensuel de cette version en millimes. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_facture` — fait

Une facture mensuelle acceptée de `facturation.csv`.

| Colonne | Type | Règle |
|---|---|---|
| `facture_id` | TEXT (clé) | Numéro de facture (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la facture. |
| `compte_key` | INTEGER → `dim_compte.compte_key` | Compte facturé. |
| `offre_key` | INTEGER → `dim_offre.offre_key` | Version de l'offre valable à la date de la facture. |
| `abonnement_id` | TEXT | Abonnement facturé (clé métier de la base opérationnelle). |
| `mois_facture` | TEXT | Mois facturé, AAAA-MM. |
| `nb_mois` | INTEGER | Mensualités facturées (entier > 0). |
| `montant_millimes` | INTEGER | Montant facturé en millimes. |

### `fact_abonnement_mois` — fait

Un abonnement × un mois où il est actif au moins un jour (fait DÉRIVÉ des dates de début et de fin, voir § 13).

| Colonne | Type | Règle |
|---|---|---|
| `abonnement_mois_id` | TEXT (clé) | `<abonnement_id>-<AAAA-MM>` (clé métier unique). |
| `abonnement_id` | TEXT | Abonnement (clé métier de la base opérationnelle). |
| `date_key` | INTEGER → `dim_date.date_key` | DERNIER jour du mois (ex. 20260331). |
| `compte_key` | INTEGER → `dim_compte.compte_key` | Compte titulaire. |
| `offre_key` | INTEGER → `dim_offre.offre_key` | Version de l'offre valable le dernier jour du mois. |
| `actif_debut` | INTEGER | 1 si actif le dernier jour du mois précédent, sinon 0. |
| `nouveau` | INTEGER | 1 si `date_debut` tombe dans le mois, sinon 0. |
| `depart` | INTEGER | 1 si `date_fin` tombe dans le mois, sinon 0. |
| `actif_fin` | INTEGER | 1 si actif le dernier jour du mois (`date_fin` vide ou après), sinon 0. |
| `mensualite_millimes` | INTEGER | Prix mensuel de la version `offre_key`, en millimes. |


## 7. Historique (SCD2) sur `dim_offre`

L'offre FN-F300 (Fibre 300) passe de la gamme « confort » à 89,900 TND à la gamme « pro » à 99,900 TND le 2026-07-15 (inclus). Cette information arrive avec `lot2/offres.json`.

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
| Abonnés actifs fin de mois | nombre | nombre d'abonnements actifs le dernier jour du mois (`actif_fin` = 1) — valeur d'**un** mois : lisez l'agrégat `par_mois` ; sur plusieurs mois, le total de la référence additionne les fins de mois (abonnés-mois) |
| MRR (revenu mensuel récurrent) | TND (stocké en millimes) | somme des mensualités des abonnements actifs en fin de mois, au prix de la version de l'offre valable le dernier jour du mois |
| Départs du mois | nombre | nombre d'abonnements dont la `date_fin` tombe dans le mois |
| Taux de départ | ratio | départs du mois / abonnés actifs en début de mois (sur plusieurs mois : somme des départs / somme des actifs de début de mois) |
| Abonnés actifs début de mois | nombre | abonnements actifs le dernier jour du mois précédent (`actif_debut` = 1) |
| Nouveaux abonnements | nombre | abonnements dont la `date_debut` tombe dans le mois |
| Montant facturé | TND (stocké en millimes) | somme des montants des factures acceptées, rangées dans le mois de leur date de facture |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (faits et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_facture` : nb_mois, montant_millimes; `fact_abonnement_mois` : actif_debut, actif_fin, nouveau, depart, mensualite_millimes; `dim_offre` : prix_mensuel_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par offre », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M07 --etape initial     # après le lot 1
python -m controles.verifier --mission M07 --etape increment   # après le lot 2
python -m controles.verifier --mission M07 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M07 --etape export
python -m controles.verifier --mission M07 --etape tout
```

## 12. Règle à clarifier

Un abonnement résilié le 31 mars (dernier jour du mois) est-il encore actif « fin mars » ? Et le MRR de juillet d'un abonné Fibre 300 se calcule-t-il à 89,900 TND (prix à la souscription ou à la facture du 1er juillet) ou à 99,900 TND (prix valable le 31 juillet) ? — **Décision :** B. `date_fin` = dernier jour de service ; actif fin de mois ⇔ `date_fin` vide ou **après** le dernier jour du mois. Le MRR d'un mois utilise la version de l'offre valable le dernier jour de ce mois : Fibre 300 compte 99,900 TND dans le MRR de juillet alors que sa facture de juillet (émise le 1er) vaut 89,900 TND.

Options étudiées :

- A : actif fin mars (il est servi le 31) ; MRR au prix de la souscription.
- B : départ de mars, plus actif fin mars ; MRR au prix de la version valable le dernier jour du mois.
- C : actif fin mars, départ compté en avril ; MRR au prix de la dernière facture.

## 13. Dérivation de `fact_abonnement_mois` (le cœur de la mission)

Ce fait ne vient pas du CSV : il est **calculé** depuis les dates de `abonnements.sqlite` (abonnements acceptés). Une ligne = un abonnement × un mois où il est actif **au moins un jour** (`date_debut` ≤ dernier jour du mois ET (`date_fin` vide OU `date_fin` ≥ 1er jour du mois)), de janvier 2026 au dernier mois du lot chargé. `abonnement_mois_id` = `<abonnement_id>-<AAAA-MM>` (ex. `AB00137-2026-03`) ; `date_key` = dernier jour du mois (ex. `20260331`) ; `offre_key` = version de l'offre valable ce dernier jour.

| Colonne | Règle de calcul (mois M) |
|---|---|
| `actif_debut` | 1 si l'abonnement était actif le dernier jour du mois **précédent** : `date_debut` < 1er jour du mois ET (`date_fin` vide OU `date_fin` ≥ 1er jour du mois) |
| `nouveau` | 1 si `date_debut` tombe dans le mois |
| `depart` | 1 si `date_fin` tombe dans le mois (même le dernier jour du mois) |
| `actif_fin` | 1 si l'abonnement est actif le dernier jour du mois : `date_debut` ≤ dernier jour ET (`date_fin` vide OU `date_fin` > dernier jour) |
| `mensualite_millimes` | prix mensuel de la version de l'offre valable le **dernier jour du mois** |
| contrôle | pour chaque mois : actifs fin = actifs début + nouveaux − départs |

Un abonnement résilié avant 2026 n'a aucune ligne. Relancer un lot recalcule les mêmes lignes : celles dont la clé existe sont ignorées, le passé ne change pas.

## 14. Trois variantes (évolutions possibles)

1. Nouvel indicateur : revenu moyen par abonné (ARPU) = MRR / abonnés actifs fin de mois, par gamme.
2. Nouvelle règle : un abonnement résilié moins de 60 jours après son début est un « départ précoce » → colonne `depart_precoce` dans `fact_abonnement_mois` et indicateur dédié.
3. Changement historique : l'offre FN-F20 baisse à 34,900 TND le 2026-08-01 (deuxième version dans `dim_offre`, MRR d'août recalculé, factures de juillet inchangées).

## 15. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — abonnés actifs et MRR à la fin de la période choisie, départs et taux de départ, MRR par mois et par gamme (barres empilées) et le tableau mois par mois actifs début + nouveaux − départs = actifs fin.
2. **Détail par offre** — chaque offre avec ses versions : FN-F300 en confort à 89,900 TND jusqu'au 2026-07-14, puis pro à 99,900 TND ; actifs, départs et MRR mois par mois.
3. **Qualité des données** — factures lues, gardées, déjà chargées, rejetées par motif ; abonnements annulés et rejetés, par lot.

Démonstration conseillée : (1) Vue direction sur toute la période (abonnés et MRR lus au dernier mois choisi), puis filtre « type de compte = entreprise » ; (2) Détail par offre sur FN-F300 : juin en confort, août en pro, MRR d'août au nouveau prix ; (3) Qualité des données : rejets du lot 1 et du lot 2, factures déjà chargées au rejeu (une ligne « lot2 (rejeu) » à 0 ajout).
