# Cahier des charges — Mission 08 : Maintenance · TechniServ

Client fictif : **TechniServ**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une intervention d'un technicien sur un équipement.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `interventions.csv` | csv | Interventions saisies par les techniciens (UTF-8, séparateur `;`). | formats de dates mélangés ; doublons ; identifiants vides ou en conflit ; équipements inconnus ; heures invalides ; lot2 : recopie des interventions du 30 juin |
| `pieces.xlsx` | excel | Feuille `Pièces` (en-têtes à la ligne 3) + feuille `Taux horaires`. | titre au-dessus du tableau ; nombres stockés comme texte |
| `equipements.json` | json | Parc d'équipements avec l'historique du contrat de chaque équipement. | une date au format JJ/MM/AAAA ; un code contrat en minuscules ; lot2 : une deuxième version pour EQ-017 (CT-09 au 2026-07-15) |
| `operations.sqlite` | sqlite | Base de l'atelier : tables `contrat`, `consommation`, `parametre`. | consommations vers une intervention inconnue ; pièces inconnues ; lot2 : recopie des consommations des interventions du 30 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `INT-26-90037` deux fois avec des heures différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `intervention_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | équipement `EQ-099`, pièce `PC-999`, consommation vers `INT-26-08812` | rejet `cle_inconnue` |
| Format décimal | `1 450,000`, `62,5`, `38.75` (Excel, SQLite) | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` eq-017 `, `Correctif`, ` t04`, ` pc-204`, ` ct-05` | supprimer les espaces autour ; codes en majuscules ; type en minuscules |
| Heures invalides | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `préventif`, `Résidences` | lire les fichiers en UTF-8 |
| Ligne déjà chargée | lot2 recopie les interventions du 30 juin et leurs consommations | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | équipement absent du parc (`equipements.json`), pièce absente du catalogue, ou consommation de pièce vers une intervention inconnue |
| `quantite_invalide` | heures facturées nulles, négatives ou non entières |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `intervention_id` vide → `id_manquant` ;
3. `intervention_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. équipement absent de `equipements.json` (ou sans version de contrat à la date d'intervention) → `cle_inconnue` ;
5. heures non entières ou ≤ 0 → `quantite_invalide` ;
6. `intervention_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Consommations (`consommation`, numero_ligne = `consommation.id`) : pièce absente du catalogue → `cle_inconnue` ; intervention ni acceptée dans ce lot ni déjà chargée → `cle_inconnue` ; consommation d'une intervention déjà chargée par un lot précédent → ignorée.

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `interventions.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- `delai_heures` = (date + heure d'intervention) − (date + heure de demande), en heures entières, pour TOUTES les interventions ; le délai moyen n'utilise que les correctives.
- `cout_main_oeuvre_millimes` = `heures` × taux horaire de la catégorie de l'équipement (feuille `Taux horaires`).
- `cout_pieces_millimes` = somme, sur les consommations acceptées de l'intervention, de `quantite` × prix unitaire du catalogue (0 si aucune pièce).
- Une intervention prend la version de l'équipement valable à sa **date d'intervention** : son `contrat_key` est le contrat de cette version.
- `fact_revenu_contrat` : une ligne par contrat et par mois du lot où le contrat est actif le 1er du mois (`date_debut` ≤ 1er du mois et `date_fin` vide ou ≥ 1er du mois). `revenu_id` = `<contrat_id>-<AAAA-MM>` (ex. `CT-03-2026-07`), `date_key` = 1er du mois, `revenu_millimes` = `revenu_mensuel` en millimes.
- `categorie` de `dim_equipement` = libellé de la feuille Taux horaires (ex. `GE` → `Groupe électrogène`).
- `type_intervention` stocké en minuscules : `préventif` ou `correctif`.
- `dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).
- La marge de service est partielle et n'a de sens que par contrat, par mois ou au total : les lignes de revenu n'ont ni équipement ni catégorie (valeur `(revenu contrat)` dans la vue d'analyse).

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

### `dim_contrat` — dimension

Contrats de maintenance (table `contrat` de la base de l'atelier).

| Colonne | Type | Règle |
|---|---|---|
| `contrat_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `contrat_id` | TEXT | Code contrat normalisé (strip + majuscules), ex. `CT-03`. |
| `client` | TEXT | Nom du client. |
| `revenu_mensuel_millimes` | INTEGER | Forfait mensuel du contrat en millimes. |
| `date_debut` | TEXT | Début du contrat, AAAA-MM-JJ. |
| `date_fin` | TEXT | Fin du contrat, AAAA-MM-JJ ; vide = sans fin prévue. |

### `dim_equipement` — dimension scd2

Équipements avec l'historique de leur contrat (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `equipement_key` | INTEGER (clé) | Clé technique d'une VERSION d'équipement. |
| `equipement_id` | TEXT | Code équipement, ex. `EQ-017` (plusieurs versions possibles). |
| `designation` | TEXT | Description de l'équipement. |
| `categorie` | TEXT | Libellé de la catégorie (feuille Taux horaires), ex. `Ascenseur`. |
| `site` | TEXT | Site du client où se trouve l'équipement. |
| `contrat_id` | TEXT | Contrat qui couvre l'équipement pendant cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_intervention` — fait

Une intervention acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `intervention_id` | TEXT (clé) | Identifiant de l'intervention (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de l'intervention. |
| `equipement_key` | INTEGER → `dim_equipement.equipement_key` | Version de l'équipement valable à la date d'intervention. |
| `contrat_key` | INTEGER → `dim_contrat.contrat_key` | Contrat de cette version de l'équipement. |
| `technicien` | TEXT | Code technicien normalisé, ex. `T04`. |
| `type_intervention` | TEXT | `préventif` ou `correctif` (minuscules). |
| `demande_le` | TEXT | Date et heure de la demande, `AAAA-MM-JJ HH:MM`. |
| `intervention_le` | TEXT | Date et heure de l'intervention, `AAAA-MM-JJ HH:MM`. |
| `heures` | INTEGER | Heures facturées (entier > 0). |
| `delai_heures` | INTEGER | intervention_le − demande_le, en heures. |
| `cout_main_oeuvre_millimes` | INTEGER | heures × taux horaire de la catégorie, en millimes. |
| `cout_pieces_millimes` | INTEGER | Somme quantité × prix des pièces consommées acceptées (0 si aucune). |

### `fact_revenu_contrat` — fait

Le forfait d'un contrat pour un mois où il est actif.

| Colonne | Type | Règle |
|---|---|---|
| `revenu_id` | TEXT (clé) | `<contrat_id>-<AAAA-MM>`, ex. `CT-03-2026-07` (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | 1er jour du mois. |
| `contrat_key` | INTEGER → `dim_contrat.contrat_key` | Contrat. |
| `revenu_millimes` | INTEGER | Forfait mensuel en millimes. |


## 7. Historique (SCD2) sur `dim_equipement`

L'équipement EQ-017 (groupe électrogène du Groupe Nakhla) passe du contrat « CT-03 » au contrat « CT-09 » le 2026-07-15 (inclus). Cette information arrive avec `lot2/equipements.json`.

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
| Interventions | nombre | nombre d'interventions acceptées (préventives + correctives) |
| Interventions correctives | nombre | nombre d'interventions de type correctif |
| Délai total des correctifs | nombre | somme de delai_heures des interventions correctives |
| Délai moyen d'intervention | heures, nombre décimal | somme des délais des interventions correctives / nombre d'interventions correctives ; délai = (date + heure d'intervention) − (date + heure de demande), en heures ; le préventif est exclu ; résultat en heures décimales (ex. 20,18 h) |
| Heures facturées | nombre | somme des heures des interventions |
| Coût de main-d'œuvre | TND (stocké en millimes) | heures × taux horaire de la catégorie de l'équipement |
| Coût des pièces | TND (stocké en millimes) | somme de quantité × prix unitaire des pièces consommées acceptées |
| Coût d'intervention | TND (stocké en millimes) | coût des pièces + coût de main-d'œuvre |
| Revenu de contrat | TND (stocké en millimes) | somme des forfaits mensuels dus (un par contrat et par mois actif) |
| Marge de service | TND (stocké en millimes) | revenu de contrat − coût d'intervention ; marge PARTIELLE (ni déplacements, ni frais de structure) ; à lire par contrat, par mois ou au total |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (interventions et revenus de contrat réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_intervention` : heures, delai_heures, cout_main_oeuvre_millimes, cout_pieces_millimes; `fact_revenu_contrat` : revenu_millimes; `dim_contrat` : revenu_mensuel_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par équipement », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M08 --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission M08 --etape initial     # après le lot 1
python -m controles.verifier --mission M08 --etape increment   # après le lot 2
python -m controles.verifier --mission M08 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M08 --etape export
python -m controles.verifier --mission M08 --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** (1) EQ-017 tombe en panne le 14 juillet à 19 h (contrat CT-03) ; le technicien intervient le 15 juillet à 9 h, jour où EQ-017 passe sur CT-09. Quel contrat paie cette intervention ? (2) Une visite préventive est planifiée trois semaines à l'avance : quel est son « délai » ?

**Options étudiées :**

- (1) A : contrat valable à la date de la demande (CT-03).
- (1) B : contrat valable à la date d'intervention (CT-09).
- (2) A : délai = intervention − planification, compté dans le délai moyen.
- (2) B : délai calculé et stocké, mais le préventif est exclu du délai moyen.

**Décision de la direction :** (1) B : chaque intervention est rattachée à la version de l'équipement valable à sa DATE D'INTERVENTION (la date du fait, `date_key`) ; c'est ce jour-là que le travail et les pièces sont consommés. (2) B : `delai_heures` est stocké pour toutes les interventions, mais le délai moyen ne compte que les correctives (la « demande » d'un préventif est une date de planification, pas une panne).

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux de respect du délai garanti = correctifs avec `delai_heures` ≤ délai garanti du contrat (nouvelle colonne `delai_garanti_heures` dans `contrat`) / correctifs.
2. Nouvelle règle : une intervention de plus de 8 heures facturées doit être validée par le chef d'atelier ; sans validation, elle est rejetée avec un nouveau motif `heures_hors_plafond`.
3. Changement historique : l'ascenseur EQ-014 passe au contrat CT-09 le 2026-08-01 (deuxième équipement historisé ; ses interventions de juillet restent sur CT-03).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — interventions, délai moyen (correctifs), coût d'intervention, revenu et marge de service ; coût d'intervention par mois et par catégorie (barres empilées) ; filtres période et contrat.
2. **Détail par équipement** — chaque équipement avec ses versions de contrat : EQ-017 sur CT-03 jusqu'au 2026-07-14, puis CT-09 ; ses interventions et son coût par contrat et par mois.
3. **Qualité des données** — lignes lues, gardées, déjà chargées, rejetées par motif, par source et par lot.

Démonstration conseillée :

1. **Vue direction** — sans filtre (janvier → août) : 2030 interventions, délai moyen 20,18 h, coût d'intervention 603 674,500 TND, marge de service 104 125,500 TND. Choisir le contrat `CT-03` : marge -8 015,200 TND, le contrat le moins rentable. Montrer le graphique « coût par mois et par catégorie » (la climatisation monte en été).
2. **Détail par équipement** — ouvrir `EQ-017` : deux versions (CT-03 jusqu'au 2026-07-14, CT-09 depuis le 2026-07-15) ; ses interventions de juillet sont réparties entre les deux contrats selon la date d'intervention. Citer l'équipement le plus coûteux : `EQ-029` (47 283,000 TND).
3. **Qualité des données** — rejets par motif et par lot (lot1 : 26, lot2 : 10), lignes déjà chargées du lot 2 (10 interventions recopiées du 30 juin), consommations rejetées ; la table « Chargements » montre le lot 2 puis son rejeu à 0 ajout.
