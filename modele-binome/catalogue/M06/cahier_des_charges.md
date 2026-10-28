# Cahier des charges — Mission 06 : Hôtellerie — Dar Azur

Client fictif : **Dar Azur**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = un séjour (une réservation de chambre, de la date d'arrivée à la date de départ).** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `sejours.csv` | csv | Séjours exportés du logiciel de réception (séparateur `;`). `lot1` en UTF-8, **`lot2` en Windows-1252 (cp1252)**. | formats de prix et de dates mélangés ; doublons ; identifiants vides ou en conflit ; codes inconnus ; nuitées invalides ; lot2 : encodage cp1252 ; lot2 : recopie les séjours arrivés le 30 juin |
| `chambres.xlsx` | excel | Feuille `Chambres` (en-têtes à la ligne 3) + feuille `Types`. | titre au-dessus du tableau ; nombres stockés comme texte ; capacité d'un établissement = somme de ses lignes |
| `canaux.json` | json | Contrats des canaux de vente avec l'historique du taux de commission. | un taux écrit `10.0` ; lot2 : une deuxième version pour OTA (15 % au 2026-07-15) |
| `operations.sqlite` | sqlite | Base opérationnelle : tables `annulation`, `motif_annulation`, `paiement`, `parametre`. | annulations retirées ; annulations vers un séjour inconnu ; lot2 : recopie des annulations depuis le 20 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `DA-90003` deux fois avec des nuitées différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `sejour_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | établissement `DMH`, canal `AGC`, type `VIL`, annulation vers `DA-09990` | rejet `cle_inconnue` |
| Format décimal | `520.500`, `520,500`, `520.5`, `520,5`, `1 007,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` dah `, `Ota`, ` dsb` | supprimer les espaces autour + majuscules |
| Nuitées invalides | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `lot2/sejours.csv` en cp1252 (`Algérie`, `Côte d'Ivoire`) | lot1 en UTF-8 ; lot2 en `cp1252` (essayer UTF-8, sinon cp1252) |
| Annulation retirée | `statut = 'RETIREE'` | ignorer (ce n'est pas un rejet) : le séjour reste vendu |
| Ligne déjà chargée | lot2 recopie les séjours arrivés le 30 juin (certains partent en juillet) | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent des référentiels (établissement, type de chambre de cet établissement, canal) ou annulation vers un séjour inconnu |
| `quantite_invalide` | nuitées nulles, négatives ou non entières |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `sejour_id` vide → `id_manquant` ;
3. `sejour_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. établissement, canal ou couple (établissement, type de chambre) absent des référentiels → `cle_inconnue` ;
5. nuitées non entières ou ≤ 0 → `quantite_invalide` ;
6. `sejour_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Annulations : `RETIREE` ignorée → `ref_sejour` absente de `fact_sejour` = `cle_inconnue` (numero_ligne = `annulation.id`) → `numero_annulation` déjà chargé = ignorée.

Règle commune à toutes les missions (c'est ce que compte le vérificateur) : les rejets sont comptés **par lot et par motif** ; une ligne dont la clé métier est déjà dans l'entrepôt est ignorée et **n'est jamais un rejet**. Le test « déjà chargé » vient donc **après** les contrôles de validité, pour le CSV comme pour la base SQLite (statut ignoré → référence inconnue = `cle_inconnue` → déjà chargé = ignoré). L'ordre ne change aucun compte : une ligne déjà chargée a forcément passé ces contrôles au lot précédent.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `sejours.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Grain : un séjour = une ligne de `fact_sejour`. Nuitées = date de départ − date d'arrivée (toujours vrai pour les lignes acceptées).
- **Date du fait = date d'arrivée** : toutes les nuitées et tout le montant d'un séjour sont rangés dans le mois de son arrivée, même si le client part le mois suivant (règle à clarifier, décision de la direction).
- Montant d'un séjour = `prix_total` converti en millimes (taxe de séjour comprise).
- Commission = montant × taux de commission du canal / 100, avec le taux de la **version valable à la date d'arrivée** (pas à la date de réservation). Les montants sont des multiples de 0,500 TND : le calcul tombe juste au millime.
- Une annulation `CONFIRMEE` reprend l'établissement, le canal (même version), les nuitées et la **date d'arrivée** de son séjour (`ref_sejour` → `fact_sejour`) ; la date d'annulation est gardée en texte.
- Remboursement = `montant_rembourse` converti en millimes (0 possible : séjour non remboursable).
- Capacité : `nombre_chambres` d'un établissement = somme de ses lignes de la feuille `Chambres`. Chambres disponibles d'une période = nombre_chambres × nombre de jours de la période présents dans `dim_date` (un mois entier : 31, 28 ou 30 nuits). Total : 64 × 181 = 11 584 après le lot 1, 64 × 243 = 15 552 après le lot 2.
- Taux d'occupation et RevPAR ne se somment pas : on les recalcule à partir des sommes (nuitées, revenu net, chambres disponibles).
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

### `dim_etablissement` — dimension

Établissements : un par ligne, capacité = somme des chambres (feuille Chambres).

| Colonne | Type | Règle |
|---|---|---|
| `etablissement_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `etablissement_id` | TEXT | Code établissement normalisé (strip + majuscules), ex. `DAH`. |
| `nom` | TEXT | Nom de l'établissement. |
| `ville` | TEXT | Ville. |
| `nombre_chambres` | INTEGER | Capacité : somme des chambres de tous les types de l'établissement. |

### `dim_canal` — dimension scd2

Canaux de vente avec historique du taux de commission (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `canal_key` | INTEGER (clé) | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `OTA` (plusieurs versions possibles). |
| `libelle` | TEXT | `direct`, `agence en ligne`, `tour-opérateur` ou `entreprise`. |
| `taux_commission_pct` | INTEGER | Commission de cette version, en % entier du prix total (ex. 18). |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_sejour` — fait

Un séjour accepté (date du fait = date d'arrivée).

| Colonne | Type | Règle |
|---|---|---|
| `sejour_id` | TEXT (clé) | Identifiant du séjour (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour d'ARRIVÉE du séjour. |
| `etablissement_key` | INTEGER → `dim_etablissement.etablissement_key` | Établissement du séjour. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Version du canal valable à la date d'arrivée. |
| `type_chambre` | TEXT | Code du type de chambre normalisé, ex. `DBL`. |
| `date_reservation` | TEXT | Jour de la réservation, AAAA-MM-JJ (peut être en 2025). |
| `date_depart` | TEXT | Jour de départ, AAAA-MM-JJ (pas de nuit ce jour-là). |
| `nuitees` | INTEGER | Nombre de nuits (entier > 0) = départ − arrivée. |
| `montant_millimes` | INTEGER | Prix total du séjour en millimes. |
| `commission_millimes` | INTEGER | montant_millimes × taux_commission_pct (version à l'arrivée) / 100. |

### `fact_annulation` — fait

Une annulation CONFIRMEE de la base opérationnelle.

| Colonne | Type | Règle |
|---|---|---|
| `annulation_id` | TEXT (clé) | Numéro de l'annulation (`numero_annulation`), clé métier unique. |
| `sejour_id` | TEXT → `fact_sejour.sejour_id` | Séjour annulé. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour d'ARRIVÉE du séjour annulé (pas la date d'annulation). |
| `etablissement_key` | INTEGER → `dim_etablissement.etablissement_key` | Établissement du séjour annulé. |
| `canal_key` | INTEGER → `dim_canal.canal_key` | Même version de canal que le séjour annulé. |
| `date_annulation` | TEXT | Jour de l'annulation, AAAA-MM-JJ (heure ignorée). |
| `nuitees` | INTEGER | Nuitées du séjour annulé (elles ne sont plus vendues). |
| `remboursement_millimes` | INTEGER | Montant remboursé en millimes (0 possible). |


## 7. Historique (SCD2) sur `dim_canal`

Le canal OTA (agence en ligne) passe d'une commission de 18 % à 15 % le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.

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
| Nuitées vendues | nombre | nuitées des séjours acceptés − nuitées des séjours annulés (annulations CONFIRMEE acceptées) |
| Chambres disponibles (chambres × nuits) | nombre | nombre de chambres de l'établissement × nombre de nuits de la période (jours de dim_date) |
| Taux d'occupation | ratio | nuitées vendues / (chambres × nuits de la période) |
| Montant des séjours | TND (stocké en millimes) | somme des prix totaux des séjours acceptés |
| Remboursements | TND (stocké en millimes) | somme des montants remboursés des annulations CONFIRMEE acceptées |
| Revenu net d'annulations | TND (stocké en millimes) | montant des séjours − remboursements |
| RevPAR | TND (stocké en millimes) | revenu net / (chambres × nuits de la période), en TND par chambre disponible, arrondi au millime |
| Commissions des canaux | TND (stocké en millimes) | somme de montant × taux de commission (version valable à la date d'arrivée) / 100 |
| Séjours acceptés | nombre | nombre de lignes de fact_sejour |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (séjours, annulations et une ligne de capacité par établissement et par jour). Un séjour **et son annulation** sont rangés dans le mois de la **date d'arrivée** du séjour (§ 5), jamais dans le mois du départ ni de l'annulation ; la capacité est rangée dans le mois de chaque nuit.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_sejour` : nuitees, montant_millimes, commission_millimes; `fact_annulation` : nuitees, remboursement_millimes; `dim_etablissement` : nombre_chambres.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par canal », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M06 --etape rejets      # après le nettoyage du lot 1 (rejets.csv seul)
python -m controles.verifier --mission M06 --etape initial     # après le lot 1
python -m controles.verifier --mission M06 --etape increment   # après le lot 2
python -m controles.verifier --mission M06 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M06 --etape export
python -m controles.verifier --mission M06 --etape tout
pytest controles
```

## 12. Règle à clarifier

**Question :** Un client arrive le 30 juin et repart le 3 juillet (3 nuitées) : le séjour compte-t-il en juin, en juillet, ou nuit par nuit ? Et une réservation faite le 10 juillet sur l'agence en ligne pour une arrivée le 20 juillet : commission à 18 % (taux du jour de la réservation) ou 15 % (taux du jour d'arrivée) ?

**Options étudiées :**

- A : tout au mois d'arrivée ; commission au taux valable à la date d'arrivée.
- B : nuit par nuit (2 nuits en juin, 1 en juillet) ; il faut découper le montant.
- C : commission au taux valable à la date de réservation.

**Décision de la direction :** A. La date d'arrivée est la date du fait : nuitées, montant, commission (version du canal valable ce jour-là) et annulations éventuelles sont rangés dans le mois d'arrivée. Simple, stable et identique pour tous les établissements.

## 13. Trois variantes (évolutions possibles)

1. Nouvel indicateur : revenu net après commissions = revenu net d'annulations − commissions, par canal et par établissement.
2. Nouvelle règle : répartir les nuitées et le montant d'un séjour à cheval sur deux mois nuit par nuit (option B) — le fait passe au grain « nuitée » ; comparer le taux d'occupation de juin et juillet avec la règle actuelle.
3. Nouvelle source : charger la table `paiement` de `operations.sqlite` dans un `fact_paiement` et suivre le taux d'encaissement = paiements reçus / revenu net d'annulations.

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — nuitées vendues, taux d'occupation, revenu net d'annulations et RevPAR, puis le revenu net par mois et par établissement (barres empilées) ; filtres période et établissement.
2. **Détail par canal** — chaque canal avec ses versions : OTA à 18 % jusqu'au 2026-07-14, puis 15 % ; nuitées, revenu net et commissions par version.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; annulations retirées ; séjours déjà chargés ignorés au lot 2.

Démonstration conseillée : (1) Vue direction sur toute la période, puis filtre établissement « DTZ » (Tozeur, forte saison en hiver) contre « DAH » (Hammamet, forte saison en été) ; (2) Détail par canal, OTA : deux versions (18 % jusqu'au 2026-07-14, 15 % ensuite) et les séjours réservés le 10 juillet pour une arrivée après le 15 juillet comptés à 15 % (date d'arrivée) ; (3) Qualité des données : rejets par motif et par lot, séjours du 30 juin recopiés et ignorés au lot 2, ligne « lot2 (rejeu) » à 0 ajout.
