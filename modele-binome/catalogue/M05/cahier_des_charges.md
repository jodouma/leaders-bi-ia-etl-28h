# Cahier des charges — Mission 05 : Centre de formation

Client fictif : **Académie Nour**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une présence : un participant inscrit × une séance d'une session (présent 0 ou 1).** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `presences.csv` | csv | Feuilles d'émargement exportées (UTF-8, séparateur `;`) : chaque inscrit figure à chaque séance tenue, avec `present` = 1 ou 0. | formats de dates mélangés ; doublons ; identifiants vides ou en conflit ; session inconnue ou participant non inscrit ; valeurs de `present` invalides ; lot2 : recopie la séance du 30 juin de SES-2619 |
| `catalogue.xlsx` | excel | Feuille `Formations` (en-têtes à la ligne 3) : tarif, capacité et nombre de séances. | titre au-dessus du tableau ; nombres stockés comme texte |
| `sessions.json` | json | Planning des sessions avec l'historique du centre de rattachement. | lot2 : une deuxième version pour SES-2619 (Sfax au 2026-07-15) ; une date au format JJ/MM/AAAA ; un code en minuscules |
| `operations.sqlite` | sqlite | Base de gestion : tables `participant`, `inscription`, `paiement`, `remboursement`, `parametre`. | paiements annulés ; paiement vers une inscription inconnue ; montants stockés en texte avec virgule ; lot2 : recopie des mouvements depuis le 1er juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne d'émargement deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `PRS-80037` deux fois avec `present` différent | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `presence_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | session `SES-2699`, participant `PA-9001` non inscrit, paiement vers `INS-26-9001` | rejet `cle_inconnue` |
| Présence invalide | `present` = `2`, `-1`, `oui`, `1,5` | rejet `quantite_invalide` |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` ses-2604 `, `Ses-2604`, ` pa-0137`, ` f03` | supprimer les espaces autour + majuscules |
| Format décimal | `450,000` (Excel), `225,000` (texte dans SQLite), `225.0` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Encodage | `Comptabilité`, `espèces` | lire les fichiers en UTF-8 |
| Paiement ou remboursement annulé | `statut = 'ANNULE'` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie la séance du 30 juin et les mouvements depuis le 1er juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel : session absente de `sessions.json`, participant sans inscription confirmée à cette session, ou paiement / remboursement vers une inscription inconnue |
| `quantite_invalide` | valeur de `present` autre que `0` ou `1` (ex. `2`, `-1`, `oui`, `1,5`) |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `presence_id` vide → `id_manquant` ;
3. `presence_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. session absente de `sessions.json`, ou participant sans inscription `CONFIRMEE` à cette session dans `operations.sqlite` → `cle_inconnue` ;
5. `present` différent de `0` ou `1` → `quantite_invalide` ;
6. `presence_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Paiements puis remboursements : `ANNULE` ignoré → `numero_inscription` absent de la table `inscription` = `cle_inconnue` (source `operations.sqlite`, numero_ligne = `id` de la ligne) → numéro déjà chargé = ignoré.

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `presences.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Une ligne de présence prend la version de la session valable à la **date de la séance**.
- Un paiement ou un remboursement prend la session de son inscription et la version valable à la **date du mouvement** (heure ignorée). `fact_paiement.signe` = `1` pour un paiement, `-1` pour un remboursement ; `montant_millimes` est toujours positif.
- Les paiements et remboursements d'une inscription `ANNULEE` sont chargés (l'argent est entré puis sorti) ; une inscription annulée n'est pas sur la feuille d'émargement, donc elle ne compte pas dans les inscrits.
- Inscrits d'une session = participants distincts de la feuille d'émargement de cette session. Ils sont comptés une fois, avec la capacité et l'encaissement attendu, dans le **mois et le centre de la date de début** de la session (vue d'analyse).
- Une session terminée a exactement inscrits × nombre de séances (catalogue) lignes de présence : c'est le dénominateur du taux d'assiduité.
- `dim_formation.prix_millimes` = prix par participant du catalogue ; `capacite` et `nb_seances` en entiers.
- `dim_session.valid_from` de la première version = `valide_depuis` (ouverture des inscriptions) ; `date_debut` = date ISO de la première séance.
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

### `dim_formation` — dimension

Catalogue : une formation par ligne (feuille Formations).

| Colonne | Type | Règle |
|---|---|---|
| `formation_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `formation_id` | TEXT | Code formation normalisé (strip + majuscules), ex. `F03`. |
| `intitule` | TEXT | Intitulé de la formation. |
| `domaine` | TEXT | Domaine, ex. `Données`. |
| `prix_millimes` | INTEGER | Prix par participant en millimes. |
| `capacite` | INTEGER | Places par session. |
| `nb_seances` | INTEGER | Nombre de séances d'une session. |

### `dim_session` — dimension scd2

Sessions avec historique du centre de rattachement (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `session_key` | INTEGER (clé) | Clé technique d'une VERSION de session. |
| `session_id` | TEXT | Code session, ex. `SES-2619` (plusieurs versions possibles). |
| `formation_id` | TEXT | Code de la formation donnée dans la session. |
| `formateur` | TEXT | Formateur. |
| `date_debut` | TEXT | Date de la première séance, AAAA-MM-JJ. |
| `centre` | TEXT | Centre de rattachement de cette version : `Tunis`, `Sousse` ou `Sfax`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_presence` — fait

Une ligne d'émargement acceptée : un inscrit × une séance.

| Colonne | Type | Règle |
|---|---|---|
| `presence_id` | TEXT (clé) | Identifiant de la ligne d'émargement (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la séance. |
| `session_key` | INTEGER → `dim_session.session_key` | Version de la session valable à la date de la séance. |
| `formation_key` | INTEGER → `dim_formation.formation_key` | Formation de la session. |
| `participant_id` | TEXT | Code participant normalisé, ex. `PA-0137`. |
| `present` | INTEGER | 1 = présent, 0 = absent. |

### `fact_paiement` — fait

Un paiement ou un remboursement VALIDE de la base de gestion.

| Colonne | Type | Règle |
|---|---|---|
| `mouvement_id` | TEXT (clé) | `numero_paiement` ou `numero_remboursement` (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour du mouvement (heure ignorée). |
| `session_key` | INTEGER → `dim_session.session_key` | Version de la session de l'inscription valable à la date du MOUVEMENT. |
| `formation_key` | INTEGER → `dim_formation.formation_key` | Formation de la session. |
| `inscription_id` | TEXT | `numero_inscription` concerné. |
| `type_mouvement` | TEXT | `paiement` ou `remboursement`. |
| `signe` | INTEGER | 1 pour un paiement, -1 pour un remboursement. |
| `montant_millimes` | INTEGER | Montant en millimes, toujours positif. |


## 7. Historique (SCD2) sur `dim_session`

La session SES-2619 (anglais professionnel, mardi soir, à distance) passe du centre « Sousse » au centre « Sfax » le 2026-07-15 (inclus). Cette information arrive avec `lot2/sessions.json`.

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
| Inscrits | nombre | nombre d'inscriptions distinctes de la session (participants de la feuille d'émargement), compté une fois par session, à la date de début de la session |
| Taux d'assiduité | ratio | présences / (inscrits × séances), soit la somme de `present` divisée par le nombre de lignes de présence (chaque inscrit figure à chaque séance tenue) |
| Taux de remplissage | ratio | inscrits / capacité (capacité du catalogue, une fois par session) |
| Paiements | TND (stocké en millimes) | somme des paiements VALIDE acceptés |
| Remboursements | TND (stocké en millimes) | somme des remboursements VALIDE acceptés |
| Encaissements nets | TND (stocké en millimes) | paiements − remboursements |
| Encaissement attendu | TND (stocké en millimes) | inscrits × prix par participant du catalogue |
| Taux d'encaissement | ratio | encaissements nets / encaissement attendu |
| Présences | nombre | somme de `present` (séances suivies) |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (présences, sessions, paiements et remboursements réunis ; une session est rangée à sa date de début). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_presence` : present; `fact_paiement` : montant_millimes, signe; `dim_formation` : prix_millimes, capacite, nb_seances.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par session », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M05 --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission M05 --etape initial     # après le lot 1
python -m controles.verifier --mission M05 --etape increment   # après le lot 2
python -m controles.verifier --mission M05 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M05 --etape export
python -m controles.verifier --mission M05 --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** (1) Un participant a payé mais n'est jamais venu (présent = 0 à toutes les séances) : compte-t-il dans les inscrits ? (2) Un participant de SES-2619 est remboursé le 20 juillet, après le changement de centre : le remboursement compte-t-il à Sousse (centre de son inscription) ou à Sfax (centre le jour du remboursement) ?

**Options étudiées :**

- (1) A : oui, il occupe une place et il a payé ; ses absences font baisser l'assiduité.
- (1) B : non, on ne compte que les participants venus au moins une fois (le remplissage baisse, l'assiduité monte).
- (2) A : version de la session à la date de l'inscription (Sousse).
- (2) B : version valable à la date du remboursement (Sfax), comme chaque mouvement.

**Décision de la direction :** (1) A : il compte dans les inscrits et dans le dénominateur de l'assiduité ; son paiement compte dans les encaissements. (2) B : chaque présence, paiement ou remboursement est rattaché à la version de la session valable à SA date et compté dans SON mois ; le remboursement du 20 juillet compte donc à Sfax.

Conséquence dans l'entrepôt : le participant jamais venu garde ses lignes `present = 0` dans `fact_presence` ; le remboursement du 2026-07-20 de SES-2619 pointe vers la version « Sfax » de `dim_session`.

## 13. Objectifs de la direction (décision)

Une session **atteint ses objectifs** si : taux de remplissage ≥ 70 %, taux d'assiduité ≥ 80 % et encaissements nets ≥ 95 % de l'encaissement attendu (inscrits × prix). Les valeurs par session sont dans l'agrégat `par_session` de `reference/attendu_lot2.json`. La recommandation à la direction nomme les sessions qui n'atteignent pas un objectif, dit lequel, et propose une action.

## 14. Ce que le lot 2 ajoute au passé (paiements de juin, sessions d'été)

Le `operations.sqlite` du lot 1 est un export **par session** : il ne contient que les inscriptions et les mouvements des 20 sessions de janvier à juin. Les 5 sessions d'été (début en juillet-août) ouvrent leurs inscriptions en juin et leurs participants **paient en juin**, mais ces paiements ne sont exportés qu'avec le lot 2, qui contient toutes les inscriptions et tout mouvement du 2026-06-01 au 2026-08-31. C'est un fait **arrivé en retard** : il est rangé dans le mois de SA date (juin), pas dans le mois du chargement. Le mois de juin change donc après l'incrément : encaissements nets de juin 950,000 TND après le lot 1, 11 740,000 TND après le lot 2. Ce n'est pas une erreur : vérifiez-le dans `par_mois` des deux fichiers `attendu_*.json`.

`dim_session` gagne 6 versions au lot 2 : 5 sessions d'été nouvelles (une première version chacune) + **une seule** nouvelle version historique, SES-2619 qui passe de Sousse à Sfax le 2026-07-15 (le seul changement SCD2 de la mission).

## 15. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux d'abandon = inscrits absents aux deux dernières séances de leur session / inscrits.
2. Nouvelle règle : une présence datée d'un jour qui n'est pas une séance de la session (hors rythme du planning) est rejetée avec un nouveau motif `seance_inconnue`.
3. Changement historique : la session SES-2622 est rattachée à Tunis à partir du 2026-07-20 (deuxième session historisée dans `dim_session`).

## 16. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — inscrits, assiduité, remplissage, encaissements nets et taux d'encaissement, puis les encaissements nets par mois et par centre (barres empilées).
2. **Détail par session** — chaque session avec ses versions : SES-2619 à Sousse jusqu'au 2026-07-14, puis à Sfax.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot.

Pendant la démonstration : choisir une période et un centre dans les filtres, lire un indicateur et son unité, puis montrer sur l'écran 2 que les présences et paiements de SES-2619 avant le 2026-07-15 restent à « Sousse » et que le remboursement du 2026-07-20 est à « Sfax ».
