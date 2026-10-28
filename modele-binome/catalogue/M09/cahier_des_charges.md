# Cahier des charges — Mission 09 : Événementiel — Scène Libre

Client fictif : **Scène Libre**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = un billet vendu.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `billets.csv` | csv | Billets exportés de la billetterie (UTF-8, séparateur `;`), une ligne = un billet. | formats de prix et de dates mélangés ; doublons ; identifiants vides ou en conflit ; événements ou canaux inconnus ; nb_places invalide ; lot2 : recopie des 16 derniers billets de juin |
| `evenements.xlsx` | excel | Feuille `Programme` (en-têtes à la ligne 3) + feuille `Tarifs`. | titre au-dessus du tableau ; dates et capacités stockées comme texte ; lot2 : le programme complet (anciens et nouveaux événements) |
| `canaux.json` | json | Référentiel des canaux de vente avec l'historique des frais de distribution. | frais écrits de plusieurs façons (`9`, `"9 %"`, `"4,5 %"`) ; lot2 : une deuxième version pour REV (11 % au 2026-07-15) |
| `remboursements.sqlite` | sqlite | Base opérationnelle du service client : tables `remboursement`, `motif`, `parametre`. | demandes refusées ou billets conservés (report) ; remboursements vers un billet inconnu ; lot2 : recopie des remboursements depuis le 1er juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | le même billet deux fois, caractère pour caractère | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `B800037` deux fois avec des `nb_places` différents | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `billet_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | événement `EV99`, canal `TEL`, remboursement vers `B990001` | rejet `cle_inconnue` |
| Format décimal | `35.000`, `35,000`, `35`, `35,5`, `1 240,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` ev04 `, `Rev`, `cat2`, ` ev07` | supprimer les espaces autour + majuscules |
| Nombre de places invalide | `0`, `-2`, `1.5`, `2,5` | rejet `quantite_invalide` (une ligne = un billet : `nb_places` vaut 1) |
| Frais écrits en texte | `9`, `"9 %"`, `"4,5 %"` | convertir en pour mille entier : 9 % → 90, 4,5 % → 45 |
| Demande non remboursée | `statut` = `CONSERVE` ou `REFUSE` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les 16 derniers billets de juin et les remboursements depuis le 1er juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel (événement, canal) ou billet inconnu |
| `quantite_invalide` | quantité nulle, négative ou non entière |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `billet_id` vide → `id_manquant` ;
3. `billet_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. événement ou canal absent des référentiels → `cle_inconnue` ;
5. `nb_places` différent de l'entier 1 → `quantite_invalide` ;
6. `billet_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Remboursements : seules les lignes `REMBOURSE` comptent (`CONSERVE` et `REFUSE` ignorées) → `billet_id` absent de `fact_billet` = `cle_inconnue` (numero_ligne = `remboursement.id`) → `numero` déjà chargé = ignoré.

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `billets.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Prix d'un billet = le prix **payé** (`prix` du CSV) : un tarif réduit peut être inférieur au tarif de la feuille Tarifs.
- Frais de distribution d'un billet = prix × `frais_pour_mille` / 1 000, arrondi au millime le plus proche, avec le taux du canal valable à la **date de vente** (les prix étant en TND entiers, le calcul tombe juste).
- Les frais sont calculés **une fois**, dans `fact_billet`. Un remboursement ne les annule pas et ne les recalcule pas.
- Un remboursement prend l'événement de son billet, la **date de l'opération** (heure ignorée) et la version du canal du billet valable à cette date.
- Montant d'un remboursement = `montant_rembourse` converti en millimes. Un billet a au plus un remboursement `REMBOURSE`.
- Taux de remplissage = billets nets / capacité. Il se lit **par événement** (ou par type, lieu, mois de l'événement). Par canal il n'a pas de sens : la capacité est rangée sous le canal `(capacité)` dans la vue d'analyse.
- `mois` (axe d'analyse) = mois de la **date de l'événement**, pas de la vente.
- `dim_evenement` : un événement par ligne ; `date_evenement` = date actuelle du spectacle (après report). Le lot 2 apporte le programme complet : les événements déjà connus ne changent pas, les nouveaux sont ajoutés.
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

### `dim_evenement` — dimension

Programme : un événement par ligne (feuille Programme).

| Colonne | Type | Règle |
|---|---|---|
| `evenement_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `evenement_id` | TEXT | Code événement normalisé (strip + majuscules), ex. `EV07`. |
| `nom` | TEXT | Nom du spectacle. |
| `type_evenement` | TEXT | `Concert`, `Théâtre` ou `Festival`. |
| `lieu` | TEXT | Nom de la salle. |
| `ville` | TEXT | Ville de la salle. |
| `date_evenement` | TEXT | Date actuelle du spectacle (après un éventuel report), AAAA-MM-JJ. |
| `capacite` | INTEGER | Nombre de places mises en vente (entier). |

### `dim_canal` — dimension scd2

Canaux de vente avec l'historique des frais de distribution (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `canal_key` | INTEGER (clé) | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `REV` (plusieurs versions possibles). |
| `libelle` | TEXT | Nom du canal, ex. `revendeur`. |
| `frais_pour_mille` | INTEGER | Frais de distribution de cette version en pour mille (9 % → 90). |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_billet` — fait

Un billet vendu accepté.

| Colonne | Type | Règle |
|---|---|---|
| `billet_id` | TEXT (clé) | Identifiant du billet (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la vente. |
| `evenement_key` | INTEGER → `dim_evenement.evenement_key` | Événement du billet. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Version du canal valable à la date de vente. |
| `categorie` | TEXT | Catégorie de place normalisée : `VIP`, `CAT1`, `CAT2`. |
| `prix_millimes` | INTEGER | Prix payé en millimes (tarif réduit possible). |
| `frais_millimes` | INTEGER | prix_millimes × frais_pour_mille de la version / 1 000 (arrondi au millime). |

### `fact_remboursement` — fait

Un remboursement `REMBOURSE` de la base du service client.

| Colonne | Type | Règle |
|---|---|---|
| `remboursement_id` | TEXT (clé) | Numéro de la demande (`numero`), clé métier unique. |
| `billet_id` | TEXT → `fact_billet.billet_id` | Billet remboursé. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de l'opération (heure ignorée). |
| `evenement_key` | INTEGER → `dim_evenement.evenement_key` | Événement du billet. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Version du canal du billet valable à la date du REMBOURSEMENT. |
| `motif` | TEXT | `ANNULATION` ou `REPORT`. |
| `montant_millimes` | INTEGER | Montant rendu en millimes. |


## 7. Historique (SCD2) sur `dim_canal`

Le canal REV (revendeur) passe de 9 % (90 ‰) à 11 % (110 ‰) de frais de distribution le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.

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
| Billets vendus | nombre | nombre de billets acceptés |
| Billets remboursés | nombre | nombre de remboursements acceptés (statut REMBOURSE, un par billet) |
| Billets nets | nombre | billets vendus − billets remboursés |
| Taux de remplissage | ratio | billets nets / capacité des événements (somme des capacités des événements concernés) |
| Recettes des billets | TND (stocké en millimes) | somme des prix payés des billets acceptés |
| Remboursements | TND (stocké en millimes) | somme des montants rendus des remboursements acceptés |
| Frais de distribution | TND (stocké en millimes) | somme des frais des billets acceptés (taux du canal valable à la date de vente) |
| Recettes nettes | TND (stocké en millimes) | recettes des billets − remboursements − frais de distribution |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (billets, remboursements et une ligne « capacité » par événement). L'axe `mois` est le mois de la **date de l'événement** ; `par_canal` contient une clé `(capacité)` (les capacités ne dépendent d'aucun canal), et le taux de remplissage d'un canal est vide.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_billet` : prix_millimes, frais_millimes; `fact_remboursement` : montant_millimes; `dim_evenement` : capacite.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par canal », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M09 --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission M09 --etape initial     # après le lot 1
python -m controles.verifier --mission M09 --etape increment   # après le lot 2
python -m controles.verifier --mission M09 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M09 --etape export
python -m controles.verifier --mission M09 --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** 1) Un billet REV vendu le 10 juillet (frais 9 %) est remboursé le 20 juillet, après le passage à 11 %. Quels frais garde-t-on ? 2) Un spectacle reporté : une demande « report » compte-t-elle comme un remboursement ?

**Options étudiées :**

- 1A : frais de la version valable à la date de **vente** (9 %), jamais recalculés.
- 1B : frais recalculés à la date du remboursement (11 %).
- 1C : frais annulés quand le billet est remboursé.
- 2A : toute demande de motif `REPORT` est un remboursement.
- 2B : seul le statut `REMBOURSE` compte ; `CONSERVE` (billet gardé pour la nouvelle date) n'est pas un remboursement.

**Décision de la direction :** 1A et 2B. Les frais sont dus au canal le jour de la vente : ils restent au taux de la version valable à la date de vente et ne sont ni remboursés ni recalculés. Un report n'est pas un remboursement : seules les lignes `REMBOURSE` (argent rendu) réduisent les billets nets et les recettes, quel que soit le motif (`ANNULATION` ou `REPORT`).

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : recette nette moyenne par billet net = recettes nettes / billets nets, par événement.
2. Nouvelle règle : en cas d'annulation, le canal rend ses frais → frais nets = frais des billets non remboursés ; nouvelle colonne `frais_rendus_millimes` dans `fact_remboursement`.
3. Changement historique : le canal PAR (partenaire) passe de 6 % à 5 % le 2026-08-01 (deuxième version de PAR dans `dim_canal`).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — billets nets, taux de remplissage, recettes nettes ; recettes nettes par mois de l'événement et par type (barres empilées) ; filtre par événement et par type.
2. **Détail par canal** — chaque canal avec ses versions de frais : REV à 90 ‰ jusqu'au 2026-07-14, puis 110 ‰ ; recettes et frais par version.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; demandes non remboursées ignorées.

Démonstration conseillée (après le lot 2) :

1. **Vue direction** — sans filtre : billets nets 2489, taux de remplissage 32,12 %, recettes nettes 109 866,930 TND. Filtrer l'événement `EV05` (annulé) : 0 billet net, recettes nettes -463,290 TND (les frais restent dus). Les trois meilleurs remplissages : `EV01` 95,00 %, `EV07` 92,22 %, `EV10` 90,00 %.
2. **Détail par canal** — `REV` montre deux versions : 90 ‰ du 2025-09-01 au 2026-07-15 (exclu), puis 110 ‰ (courante) ; frais REV au total 2 394,900 TND. Expliquer le cas de la règle à clarifier : un billet `EV12` vendu par REV avant le 15 juillet et remboursé après garde 90 ‰.
3. **Qualité des données** — rejets lot1 = 25, lot2 = 10 (par motif et par source) ; billets déjà chargés au rejeu ; demandes `CONSERVE` / `REFUSE` ignorées (ce ne sont pas des rejets).
