# Cahier des charges — Mission 04 : Livraison

Client fictif : **Colis Rapide**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = un colis livré.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `colis.csv` | csv | Suivi des colis livrés exporté du logiciel des agences (UTF-8, séparateur `;`). | formats de poids et de dates mélangés ; doublons ; identifiants vides ou en conflit ; agences ou services inconnus ; poids invalides ; lot2 : recopie de colis livrés fin juin |
| `tarifs.xlsx` | excel | Feuilles `Grille` (en-têtes à la ligne 3), `Tranches`, `Zones`, `Services`. | titre au-dessus de la grille ; nombres stockés comme texte |
| `agences.json` | json | Référentiel des agences avec l'historique de leur zone de rattachement. | une date au format JJ/MM/AAAA ; lot2 : une deuxième version pour NAB (Centre-Sahel au 2026-07-15) |
| `facturation.sqlite` | sqlite | Base opérationnelle de facturation : tables `facture`, `penalite`, `parametre`. | factures annulées puis refaites ; pénalités annulées ; factures et pénalités vers un colis inconnu ; lot2 : recopie des factures des colis de fin juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `CR900001` deux fois avec des poids différents | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `colis_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | agence `KAI`, service `PRM`, facture vers `CR777001` | rejet `cle_inconnue` |
| Format décimal du poids | `2.350`, `2,350`, `2.35`, `2,35`, `1` | point ou virgule = décimales ; convertir en **grammes entiers** (2,35 kg = 2 350 g) |
| Poids invalide | `-1,200`, `0`, `45.000` (plus de 30 kg) | rejet `quantite_invalide` |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` nab `, `Exp`, ` su` | supprimer les espaces autour + majuscules |
| Encodage | `Médenine`, `Béja`, `Gabès` | lire les fichiers en UTF-8 |
| Facture annulée | `statut = 'ANNULEE'` | ignorer (ce n'est pas un rejet) ; la facture refaite compte |
| Pénalité annulée | `statut = 'ANNULEE'` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie des colis livrés fin juin et leurs factures | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel (agence, service, zone) ou facture / pénalité vers un colis inconnu |
| `quantite_invalide` | poids nul, négatif, illisible ou supérieur à 30 kg (le poids joue ici le rôle de la quantité) |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `colis_id` vide → `id_manquant` ;
3. `colis_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. agence, service ou zone de destination absent des référentiels → `cle_inconnue` ;
5. poids illisible, ≤ 0 ou > 30 kg → `quantite_invalide` ;
6. `colis_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Facturation : factures `ANNULEE` et pénalités `ANNULEE` ignorées → `colis_id` ni dans `fact_colis` ni parmi les colis acceptés du lot = `cle_inconnue` (numero_ligne = `id` de la table `facture` ou `penalite`) → facture ou pénalité d'un colis déjà chargé = ignorée (lot 2 : voir `nettoyage.facturation.sqlite` de la référence).

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `colis.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Date du fait = **date de livraison** (`date_key` de `fact_colis`) : un colis compte dans le mois où il est livré.
- `retard_jours` = date_livraison − date_promise en jours calendaires, **0 si le colis arrive avant ou le jour promis** (jamais négatif).
- `a_l_heure` = 1 si date_livraison ≤ date_promise, sinon 0. Un colis livré **le jour promis** est à l'heure.
- Tranche de poids : la borne basse est exclue, la borne haute incluse (1,000 kg → T1 ; 1,010 kg → T2 ; 5,000 kg → T2).
- `tarif_id` = code zone de destination + `-` + code tranche (ex. `SU-T3`) ; `zone_destination` = libellé de la feuille Zones (ex. `Sud`).
- `cout_transporteur_millimes` du colis = coût de la grille pour sa zone de destination et sa tranche.
- `montant_facture_millimes` = montant de l'unique facture `EMISE` ou `PAYEE` du colis (la base garantit qu'il y en a exactement une par colis accepté). La remise éventuelle est déjà dedans : ne pas recalculer depuis la grille.
- `penalite_millimes` = somme des pénalités `APPLIQUEE` du colis, 0 s'il n'y en a pas.
- Poids stocké en **grammes entiers** (`poids_grammes`).
- `dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2). Les dates d'expédition et promises restent du texte ISO dans `fact_colis`.

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

### `dim_agence` — dimension scd2

Agences avec l'historique de leur zone de rattachement (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `agence_key` | INTEGER (clé) | Clé technique d'une VERSION d'agence. |
| `agence_id` | TEXT | Code agence normalisé, ex. `NAB` (plusieurs versions possibles). |
| `nom` | TEXT | Nom de l'agence. |
| `ville` | TEXT | Ville de l'agence. |
| `zone` | TEXT | Zone de rattachement de cette version, ex. `Nord`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `dim_service` — dimension

Les trois services (feuille Services).

| Colonne | Type | Règle |
|---|---|---|
| `service_key` | INTEGER (clé) | Clé technique (1, 2, 3). |
| `service_id` | TEXT | Code service normalisé : `STD`, `EXP`, `ECO`. |
| `libelle` | TEXT | Libellé, ex. `Express`. |
| `delai_promis_jours` | INTEGER | Délai promis au client en jours. |
| `coefficient_prix_pct` | INTEGER | Coefficient appliqué au prix de la grille, en % (Express = 150). |

### `dim_tarif` — dimension

Grille tarifaire : une ligne par zone de destination × tranche de poids (16 lignes).

| Colonne | Type | Règle |
|---|---|---|
| `tarif_key` | INTEGER (clé) | Clé technique. |
| `tarif_id` | TEXT | Code zone + `-` + code tranche, ex. `SU-T3`. |
| `zone_destination` | TEXT | Libellé de la zone de destination (feuille Zones), ex. `Sud`. |
| `tranche` | TEXT | Code tranche de poids : `T1` … `T4`. |
| `tranche_libelle` | TEXT | Libellé de la tranche (feuille Tranches). |
| `poids_min_grammes` | INTEGER | Borne basse de la tranche en grammes (exclue). |
| `poids_max_grammes` | INTEGER | Borne haute de la tranche en grammes (incluse). |
| `prix_millimes` | INTEGER | Prix de la grille (service Standard) en millimes. |
| `cout_transporteur_millimes` | INTEGER | Coût transporteur en millimes. |

### `fact_colis` — fait

Un colis livré accepté, complété par sa facture et ses pénalités.

| Colonne | Type | Règle |
|---|---|---|
| `colis_id` | TEXT (clé) | Numéro du colis (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de LIVRAISON (date du fait). |
| `agence_key` | INTEGER → `dim_agence.agence_key` | Version de l'agence valable à la date de livraison. |
| `service_key` | INTEGER → `dim_service.service_key` | Service du colis. |
| `tarif_key` | INTEGER → `dim_tarif.tarif_key` | Ligne de grille : zone de destination × tranche du poids. |
| `date_expedition` | TEXT | Date d'expédition ISO AAAA-MM-JJ. |
| `date_promise` | TEXT | Date de livraison promise ISO AAAA-MM-JJ. |
| `poids_grammes` | INTEGER | Poids en grammes entiers (0 < poids ≤ 30 000). |
| `retard_jours` | INTEGER | max(0, date_livraison − date_promise) en jours calendaires. |
| `a_l_heure` | INTEGER | 1 si date_livraison ≤ date_promise, sinon 0. |
| `montant_facture_millimes` | INTEGER | Montant de la facture EMISE ou PAYEE du colis, en millimes. |
| `penalite_millimes` | INTEGER | Somme des pénalités APPLIQUEE du colis, en millimes (0 si aucune). |
| `cout_transporteur_millimes` | INTEGER | Coût de la grille pour ce tarif, en millimes. |


## 7. Historique (SCD2) sur `dim_agence`

L'agence NAB (Nabeul) passe de la zone « Nord » à la zone « Centre-Sahel » le 2026-07-15 (inclus). Cette information arrive avec `lot2/agences.json`.

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
| Colis livrés | nombre | nombre de colis acceptés dans `fact_colis` |
| Colis à l'heure | nombre | colis avec date_livraison ≤ date_promise (livré le jour promis = à l'heure) |
| Ponctualité | ratio | colis à l'heure / colis livrés |
| Retard moyen | jours, nombre décimal | somme des jours de retard / nombre de colis EN RETARD (les colis à l'heure ne comptent pas) ; jours de retard = date_livraison − date_promise, en jours calendaires |
| Montant facturé | TND (stocké en millimes) | somme des montants des factures EMISE ou PAYEE des colis acceptés |
| Pénalités de retard | TND (stocké en millimes) | somme des pénalités APPLIQUEE des colis acceptés |
| Revenu facturé net de pénalités | TND (stocké en millimes) | montant facturé − pénalités de retard |
| Coût transporteur | TND (stocké en millimes) | somme du coût transporteur de la grille (zone de destination × tranche de poids) des colis acceptés |
| Marge de livraison | TND (stocké en millimes) | revenu facturé net de pénalités − coût transporteur (marge partielle : ni salaires, ni loyers, ni carburant des agences ; ce n'est pas un bénéfice) |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (une ligne par colis livré). Un colis est rangé dans le mois **de sa date de livraison**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_colis` : poids_grammes, retard_jours, a_l_heure, montant_facture_millimes, penalite_millimes, cout_transporteur_millimes; `dim_tarif` : prix_millimes, cout_transporteur_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par agence », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M04 --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission M04 --etape initial     # après le lot 1
python -m controles.verifier --mission M04 --etape increment   # après le lot 2
python -m controles.verifier --mission M04 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M04 --etape export
python -m controles.verifier --mission M04 --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** Deux cas posent problème. (1) Un colis livré **le jour même** de la date promise est-il à l'heure ? (2) Un colis de l'agence de Nabeul expédié le 13 juillet (zone Nord) et livré le 16 juillet (zone Centre-Sahel) : dans quelle zone le compter ?

**Options étudiées :**

- (1) A : à l'heure (date_livraison ≤ date_promise). B : en retard (il fallait livrer avant).
- (2) A : version de l'agence valable à la date d'**expédition** (Nord). B : version valable à la date de **livraison** (Centre-Sahel).

**Décision de la direction :** deux décisions distinctes.

- Question (1) → **option A** : un colis livré le jour promis est **à l'heure** ; son retard vaut 0 jour.
- Question (2) → **option B** : le colis est rattaché à la version de l'agence valable à sa **date de livraison**, qui est la date du fait (dim_date) ; il compte donc dans Centre-Sahel et dans le mois de juillet.

Exemple : le colis de Nabeul expédié le 2026-07-13 et livré le 2026-07-16 (date promise 2026-07-16) est **à l'heure** et compte dans la zone **Centre-Sahel**, mois 2026-07.

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : taux de pénalité = pénalités / montant facturé, par agence et par service.
2. Nouvelle règle : le retard se compte en jours ouvrés (samedi et dimanche exclus) ; recalculer `retard_jours`, `a_l_heure` et la ponctualité.
3. Changement historique : l'agence BIZ (Bizerte) rejoint la zone « Grand Tunis » le 2026-08-16 (deuxième version pour BIZ dans `dim_agence`).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — ponctualité, revenu facturé net, pénalités, coût transporteur et marge de livraison ; revenu net par mois et par zone d'agence (barres empilées) ; filtres période, agence, zone, service.
2. **Détail par agence** — chaque agence avec ses versions : NAB en zone Nord jusqu'au 2026-07-14, puis Centre-Sahel ; indicateurs par version et par mois.
3. **Qualité des données** — lignes rejetées par motif, par source et par lot.

Démonstration conseillée (5 minutes) : écran 1 sans filtre (ponctualité, retard moyen en jours et montants) → filtre zone « Sud » (où se concentrent retards et coûts) → écran 2, agence NAB (deux versions, chiffres de juillet répartis entre Nord et Centre-Sahel) → écran 3 (rejets par motif et par lot, puis une ligne par chargement : lot 1, lot 2 et le rejeu à 0 ajout).
