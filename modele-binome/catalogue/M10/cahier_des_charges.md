# Cahier des charges — Mission 10 : Agence numérique

Client fictif : **Pixel Studio**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une ligne de temps (un collaborateur, un projet, un jour, une tâche, des heures).** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `temps.csv` | csv | Feuilles de temps exportées de l'outil de saisie (UTF-8, séparateur `;`). | heures `7,5` / `7.5` / `7.50` ; dates en trois formats ; doublons ; identifiants vides ou en conflit ; codes inconnus ; heures nulles ou négatives ; lot2 : recopie de lignes de fin juin |
| `couts.xlsx` | excel | Feuille `Profils` (en-têtes à la ligne 3) + feuille `Collaborateurs`. | titre au-dessus du tableau ; nombres stockés comme texte ; profils en casse variable |
| `projets.json` | json | Référentiel des projets avec l'historique des chefs de projet. | lot2 : une deuxième version pour PX07 (Nour Jebali au 2026-07-15) ; un projet interne non facturable |
| `facturation.sqlite` | sqlite | Base de facturation : tables `facture`, `avoir`, `parametre`. | factures annulées ; facture vers un projet inconnu ; avoir vers une facture inconnue ; lot2 : recopie des documents depuis le 15 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne de temps deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `T26-90001` deux fois avec des heures différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `temps_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | collaborateur `C99`, projet `PX99`, avoir vers `F26-0999` | rejet `cle_inconnue` |
| Format des heures | `7.5`, `7,5`, `7.50`, `8,0` | point ou virgule = décimales ; convertir en centièmes d'heure entiers (7,5 h → 750) |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` c05 `, `Px07`, `DÉVELOPPEUR`, `Régie` | codes : espaces autour supprimés + majuscules ; profils et types : espaces supprimés + minuscules |
| Heures invalides | `-2`, `0`, `-7,5`, `0,0` | rejet `quantite_invalide` |
| Montants Excel | `41,000`, `32.5` | point ou virgule = décimales ; millimes entiers |
| Encodage | `réunion client`, `développeur` | lire les fichiers en UTF-8 |
| Facture annulée | `statut = 'ANNULEE'` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie des lignes de temps de fin juin et les documents depuis le 15 juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel (collaborateur, projet, facture d'origine d'un avoir) |
| `quantite_invalide` | heures nulles, négatives ou illisibles |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `temps_id` vide → `id_manquant` ;
3. `temps_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. collaborateur ou projet absent des référentiels → `cle_inconnue` ;
5. heures illisibles, nulles ou négatives → `quantite_invalide` ;
6. `temps_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Factures : `ANNULEE` ignorée → `facture_id` déjà chargé = ignoré → `code_projet` inconnu = `cle_inconnue` (numero_ligne = `facture.id`). Avoirs (après les factures) : `avoir_id` déjà chargé = ignoré → `facture_id` absent de `fact_facture` = `cle_inconnue` (numero_ligne = `avoir.id`).

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `temps.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Heures : stockées en **centièmes d'heure entiers** dans `heures_centiemes` (7,5 h → 750 ; 1,25 h → 125). Au plus deux décimales dans la source.
- Taux horaire coût = taux du **profil** du collaborateur (`couts.xlsx`, feuille Collaborateurs puis Profils), fixe sur 2026. La colonne `profil` du CSV n'est qu'une information : le référentiel gagne.
- `cout_charge_millimes` = `heures_centiemes` × `taux_horaire_millimes` / 100. Le résultat est un entier exact (tous les taux sont des multiples de 0,100 TND).
- Une facture `EMISE` → une ligne de `fact_facture` : `type_document` = `facture`, `signe` = +1. Un avoir → `type_document` = `avoir`, `signe` = −1, projet de sa facture d'origine, **date de l'avoir**.
- `montant_ht_millimes` est toujours positif : c'est `signe` qui dit s'il ajoute ou retire.
- Chaque fait (heure, facture, avoir) est rattaché à la version du projet valable à **sa propre date**.
- Le projet `INT01` (type `interne` : formation, avant-vente) n'est jamais facturé : ses heures **comptent** dans le coût de charge et sa marge de contribution est négative.
- Marge de contribution = facturé net − coût de charge. Ce n'est **pas** un bénéfice : loyers, logiciels, heures non saisies et frais généraux n'y sont pas.
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

### `dim_collaborateur` — dimension

Collaborateurs avec leur profil et le taux horaire coût du profil (feuilles Collaborateurs + Profils).

| Colonne | Type | Règle |
|---|---|---|
| `collaborateur_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `collaborateur_id` | TEXT | Code normalisé (strip + majuscules), ex. `C05`. |
| `nom` | TEXT | Nom et prénom (fictifs). |
| `profil` | TEXT | Profil normalisé en minuscules : `développeur`, `designer`, `chef de projet`, `consultant`. |
| `taux_horaire_millimes` | INTEGER | Taux horaire coût du profil, en millimes par heure (32,500 TND → 32500). |

### `dim_projet` — dimension scd2

Projets avec historique du chef de projet (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `projet_key` | INTEGER (clé) | Clé technique d'une VERSION de projet. |
| `projet_id` | TEXT | Code projet, ex. `PX07` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du projet. |
| `client` | TEXT | Client (fictif) ; `Pixel Studio` pour le projet interne. |
| `type_projet` | TEXT | `forfait`, `régie` ou `interne` (minuscules). |
| `chef_projet` | TEXT | Chef de projet de cette version (nom). |
| `date_debut` | TEXT | Date de début du projet, AAAA-MM-JJ. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_temps` — fait

Une ligne de temps acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `temps_id` | TEXT (clé) | Identifiant de la ligne de temps (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour travaillé. |
| `collaborateur_key` | INTEGER → `dim_collaborateur.collaborateur_key` | Collaborateur. |
| `projet_key` | INTEGER → `dim_projet.projet_key` | Version du projet valable le jour travaillé. |
| `tache` | TEXT | Tâche (texte de la source, espaces supprimés). |
| `heures_centiemes` | INTEGER | Heures en CENTIÈMES d'heure entiers (7,5 h → 750), > 0. |
| `taux_horaire_millimes` | INTEGER | Taux horaire coût du profil du collaborateur (millimes par heure). |
| `cout_charge_millimes` | INTEGER | heures_centiemes × taux_horaire_millimes / 100 (entier exact). |

### `fact_facture` — fait

Une facture EMISE ou un avoir de la base de facturation.

| Colonne | Type | Règle |
|---|---|---|
| `document_id` | TEXT (clé) | `facture_id` (F26-…) ou `avoir_id` (AV26-…), clé métier unique. |
| `type_document` | TEXT | `facture` ou `avoir`. |
| `facture_origine_id` | TEXT | Pour un avoir : la facture corrigée ; vide pour une facture. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la facture ou de l'avoir. |
| `projet_key` | INTEGER → `dim_projet.projet_key` | Version du projet valable à la date du DOCUMENT. |
| `signe` | INTEGER | +1 pour une facture, −1 pour un avoir. |
| `montant_ht_millimes` | INTEGER | Montant hors taxes en millimes, toujours positif. |


## 7. Historique (SCD2) sur `dim_projet`

Le projet PX07 (Portail patients) passe de la cheffe de projet « Hela Mansour » à « Nour Jebali » le 2026-07-15 (inclus). Cette information arrive avec `lot2/projets.json`.

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
| Heures | centièmes d'heure, 750 = 7,5 h | somme des heures des lignes de temps acceptées, en centièmes d'heure (750 = 7,5 h) |
| Coût de charge | TND (stocké en millimes) | somme de heures × taux horaire coût du profil du collaborateur |
| Factures | TND (stocké en millimes) | somme des montants HT des factures EMISE acceptées |
| Avoirs | TND (stocké en millimes) | somme des montants HT des avoirs acceptés |
| Facturé net | TND (stocké en millimes) | factures − avoirs (montants HT) |
| Marge de contribution | TND (stocké en millimes) | facturé net − coût de charge (ce n'est PAS un bénéfice : aucun frais général) |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (faits et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_temps` : heures_centiemes, cout_charge_millimes; `fact_facture` : signe, montant_ht_millimes; `dim_collaborateur` : taux_horaire_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par projet », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M10 --etape initial     # après le lot 1
python -m controles.verifier --mission M10 --etape increment   # après le lot 2
python -m controles.verifier --mission M10 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M10 --etape export
python -m controles.verifier --mission M10 --etape tout
```

## 12. Règle à clarifier

(1) Les heures saisies sur PX07 avant le 15 juillet, et la facture de régie de juillet datée du 31 juillet : quel chef de projet ? (2) Les heures passées sur le projet interne INT01 (non facturable) comptent-elles dans le coût de charge ? — **Décision :** (1) B : chaque heure, facture ou avoir prend la version de PX07 valable à SA date : les heures jusqu'au 14 juillet restent à Hela Mansour, la facture du 31 juillet (qui couvre tout juillet) va à Nour Jebali. (2) A : les heures de INT01 comptent dans le coût de charge global ; INT01 apparaît comme un projet de type `interne` avec un facturé net nul.

Options étudiées :

- (1) A : le chef courant pour tout le projet (on réécrit l'historique).
- (1) B : le chef valable le jour de la ligne de temps (ou de la facture).
- (2) A : oui, toute heure saisie coûte, facturable ou non.
- (2) B : non, on n'analyse que les projets clients.

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux de facturabilité = heures des projets forfait ou régie / heures totales.
2. Nouvelle règle : une ligne de plus de 12 heures est refusée → nouveau motif `heures_hors_bornes`.
3. Changement historique : le taux horaire coût des développeurs passe de 32,500 à 34,000 TND le 2026-08-01 (le coût d'une heure dépend de sa date : historiser les taux).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — factures, avoirs, facturé net, coût de charge et marge de contribution ; coût de charge par mois et par type de projet (barres empilées).
2. **Détail par projet** — chaque projet avec ses versions : PX07 chez Hela Mansour jusqu'au 2026-07-14, puis Nour Jebali ; les projets à marge négative se repèrent ici.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot.
