# Générateurs de données — édition « Solen BI 22 h » (V7)

Ces scripts fabriquent les données **100 % synthétiques** de chaque mission et calculent les valeurs de référence **depuis la vérité terrain**, jamais depuis un ETL. Le vérificateur des étudiants (`modele-binome/controles/verifier.py`) compare leurs sorties à ces références.

## Régénérer

Depuis `github/` :

```bash
.venv/bin/python authoring/generateurs/mission00_commerce360.py          # une mission
for g in authoring/generateurs/mission*.py; do .venv/bin/python "$g"; done   # les onze
.venv/bin/python authoring/generateurs/verifier_reproductibilite.py      # 11 OK attendus (restaure ensuite chaque mission et v7-data.json)
```

Un script réécrit uniquement le dossier de SA mission (`modele-binome/tronc-commun/` ou `modele-binome/catalogue/MNN/` : `fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/, sources/, reference/`) et fusionne SON bloc dans `v7-data.json`. La vérité terrain brute (CSV) n'est écrite que si la variable d'environnement `SOLEN_VERITE_PRIVEE=<dossier>` est définie (dossier privé du formateur, hors dépôt) : sans elle, rien n'est écrit ailleurs.

Reproductible : sur une même machine, deux exécutions donnent les mêmes octets (graine fixe, classeur Excel zippé avec des dates figées et `create_system` fixe, textes écrits en LF avec `newline="\n"`, SVG avec `svg.hashsalt` fixe, PNG sans métadonnées variables). Entre plateformes, on compare le **contenu** : chaque générateur écrit `reference/empreintes.json` (une empreinte par fichier de la mission) et `verifier_reproductibilite.py` la compare aux fichiers publiés puis aux fichiers régénérés :

| Fichier | Empreinte comparée |
|---|---|
| `.csv`, `.json`, `.md` | octets du texte, fins de ligne normalisées en LF (quel que soit l'encodage, cp1252 compris) |
| `.xlsx` | valeurs des cellules, feuille par feuille (openpyxl) ; pas les octets du ZIP (zlib) |
| `.sqlite` | schéma (`sqlite_master`) + `SELECT * ORDER BY` toutes les colonnes, table par table ; pas l'en-tête (il porte la version de SQLite) |
| `.png`, `.svg` (`reference/visuels/`) | présence seulement : le rendu dépend de matplotlib et de FreeType |

C'est ce qui rend le job `donnees` de `verify.yml` déterministe sous Ubuntu et Windows.

| Mission | Script (+ `textes_missionNN.py`) | Graine | Taille | CSV de faits lot1 / lot2 (lignes) | Faits après lot2 | Rejets lot1 / lot2 | Nombre clé (après lot2) |
|---|---|---|---|---|---|---|---|
| 00 tronc commun — Maison Zitouna | `mission00_commerce360.py` | 260001 | ≈ 627 Ko | `ventes.csv` 1998 / 413 | `fact_vente` 2345 · `fact_retour` 99 | 26 / 10 | Ventes nettes : 91 444,460 TND |
| M01 — Carthage Market | `mission01_carthage_market.py` | 260101 | ≈ 732 Ko | `ventes.csv` 2184 / 449 | `fact_vente` 2570 · `fact_retour` 80 | 24 / 10 | Ventes nettes : 21 880,226 TND |
| M02 — Souk Express | `mission02_souk_express.py` | 260202 | ≈ 651 Ko | `commandes.csv` 2085 / 488 | `fact_commande` 2510 · `fact_remboursement` 159 | 25 / 10 | CA net : 248 286,934 TND |
| M03 — Medina Distribution | `mission03_medina_distribution.py` | 260003 | ≈ 801 Ko | `factures.csv` 2087 / 428 | `fact_facture` 2458 · `fact_avoir` 126 | 24 / 10 | Marge commerciale : 39 074,380 TND |
| M04 — Colis Rapide | `mission04_colis_rapide.py` | 260004 | ≈ 1026 Ko | `colis.csv` 2116 / 444 | `fact_colis` 2497 | 29 / 11 | Ponctualité : 83,82 % |
| M05 — Académie Nour | `mission05_academie_nour.py` | 260005 | ≈ 791 Ko | `presences.csv` 1958 / 456 | `fact_presence` 2353 · `fact_paiement` 455 | 26 / 10 | Taux d'assiduité : 82,53 % |
| M06 — Dar Azur | `mission06_dar_azur.py` | 260006 | ≈ 913 Ko | `sejours.csv` 1938 / 494 | `fact_sejour` 2360 · `fact_annulation` 135 | 29 / 13 | Taux d'occupation : 44,48 % |
| M07 — FibreNet | `mission07_fibrenet.py` | 260007 | ≈ 794 Ko | `facturation.csv` 1722 / 600 | `fact_facture` 2270 · `fact_abonnement_mois` 2270 | 25 / 10 | MRR (revenu mensuel récurrent) : 23 158,100 TND (août) |
| M08 — TechniServ | `mission08_techniserv.py` | 260008 | ≈ 1052 Ko | `interventions.csv` 1593 / 491 | `fact_intervention` 2030 · `fact_revenu_contrat` 78 | 26 / 10 | Marge de service : 104 125,500 TND |
| M09 — Scène Libre | `mission09_scene_libre.py` | 260009 | ≈ 695 Ko | `billets.csv` 2380 / 441 | `fact_billet` 2757 · `fact_remboursement` 268 | 25 / 10 | Recettes nettes : 109 866,930 TND |
| M10 — Pixel Studio | `mission10_pixel_studio.py` | 261010 | ≈ 748 Ko | `temps.csv` 2015 / 426 | `fact_temps` 2384 · `fact_facture` 86 | 24 / 11 | Marge de contribution : 132 912,525 TND |

Versions de la construction publiée (données, visuels et PDF du 28/10/2026, macOS) : Python 3.13.17 · SQLite 3.54.1 · openpyxl 3.1.5 · matplotlib 3.11.2 · reportlab 5.1.0 · Pillow 13.0.0 · pypdf 6.21.3 · fonttools 4.68.0 ; côté dépôt binôme : pandas 3.1.0 · pytest 9.2.0. Les plages de `authoring/requirements.txt` et de `modele-binome/requirements.txt` incluent ces versions. Les générateurs n'utilisent que la bibliothèque standard + openpyxl + matplotlib (ni pandas, ni pytest).

## Ce que produit une mission

```
<mission>/fiche_mission.md  cahier_des_charges.md  dictionnaire.md
<mission>/echantillon/      ventes.csv (≤ 12 lignes) catalogue.xlsx boutiques.json operations.sqlite attendu.md attendu.json
<mission>/sources/lot1/     4 sources (CSV, Excel, JSON, SQLite)
<mission>/sources/lot2/     4 sources : nouvelles lignes + lignes déjà chargées (rejeu) + 1 changement SCD2
<mission>/reference/        attendu_lot1.json attendu_lot2.json contrat_entrepot.json empreintes.json README.md visuels/*.png|svg
```

- `attendu_<lot>.json` : comptes par source, nettoyage (formats normalisés, doublons, lignes déjà chargées), rejets par motif et par source, lignes par table, indicateurs globaux, agrégats par axe (zone, boutique, mois, famille…) en millimes entiers, versions SCD2 avec `valid_from`/`valid_to`, contrôles de date frontière. `attendu_lot2.json` vaut aussi pour le rejeu (bloc `rejeu`).
- `contrat_entrepot.json` : ce qui rend le vérificateur générique pour les 11 missions — tables, colonnes, colonnes entières, clés étrangères, dimension SCD2 et faits qui y pointent, vue d'analyse SQL « mouvements », indicateurs (code, formule française, agrégat SQL, tolérance), axes, colonnes obligatoires de `rejets.csv` et sources contrôlées par `--etape rejets` (`rejets.etape_rejets` : le CSV de faits seul ; la base SQLite est contrôlée à `--etape initial`), sommes de l'export, textes obligatoires de l'application, lots et étapes.

## Comment la référence est calculée (indépendance)

1. Le script de mission crée des **événements vrais** (ventes, retours…) avec une graine.
2. `construire_csv()` les rend en texte « sale » et **ajoute** des lignes piégées comptées (doublons exacts, conflits d'identifiant, identifiants vides, clés inconnues, quantités invalides) ; les formats de montants, dates et codes sont mélangés sur une part des lignes vraies.
3. Les tables de l'étoile sont construites **directement depuis les événements vrais** (`tables_verite`), puis `entrepot_verite()` les charge en mémoire et exécute la vue d'analyse du contrat : ce sont les valeurs attendues. Aucune source n'est relue.
4. Un double contrôle Python pur (sans SQL) vérifie ventes nettes et marge dans le script ; le formateur dispose en plus, dans son dossier privé, d'un contrôle croisé pandas sur la vérité brute.

## Ajouter une mission (M01…M10)

Un script `missionNN_<nom>.py` de 150 à 250 lignes, plus ses textes :

1. Définir `TABLES` (`table_dim_date()` + dimensions + faits ; une dimension `dimension_scd2` avec `valid_from`/`valid_to` nullable) et un `MissionSpec` : textes, `Source`s, `Indicateur`s (formule française + agrégat SQL sur la vue), `vue_analyse` (une ligne par mouvement : colonnes d'axes + colonnes additives), `axes`, `SCD2` (faits concernés + dates frontières), `visuels`.
2. Générer la vérité (`rng_mission(graine)`), puis pour chaque lot : `construire_csv(evenements, ChampsCSV(...), Doses(...), rng, nouvel_id, rejouees)` ; écrire les sources avec `ecrire_csv` (option `encodage="cp1252"`), `ecrire_excel([Feuille…])`, `ecrire_json`, `ecrire_sqlite(ddl, données)`.
3. Remplir un `LotResultat` par lot (comptes, nettoyage, rejets par source, **état cumulé** des tables de vérité, bloc incrément) et appeler `produire_reference(spec, lots)`, puis l'échantillon (`calculer_attendu_echantillon`), `exporter_v7_data` et `ecrire_verite_privee`.

Ce que le cadre écrit seul (ne pas le recoder dans un script de mission) :

- **Documents** : `MissionSpec.regle_a_clarifier` (`question`, `options`, `decision`, `consequence` facultatif), `variantes` (3), `ecrans_app` (3 écrans) + `parcours_app` (démonstration conseillée), `question_decision` (décision attendue, fiche et cahier), `sections_cahier` (sections propres à la mission, numérotées à partir du § 13), `regle_mois` (phrase du § 9), `scd2.precisions` (puces du § 7), `scd2.libelle_attribut`, `complement_reference` (texte ajouté à `reference/README.md`). `sommes_export_reference=True` écrit aussi les sommes attendues du manifest (`attendu_*.json` → `sommes_export`, contrôlées par le vérificateur ; utilisé par M08). Le cahier écrit une seule fois la règle commune de l'ordre des contrôles (« déjà chargé » testé après la validité ; rejets comptés par lot) et `pytest controles` partout. Un texte peut être une fonction `attendus → texte` quand il cite des valeurs de référence.
- **Unités d'indicateur** : `millimes`, `ratio`, `nombre`, `jours`, `heures`, `centiemes_heure` (documents : « 2,41 jours », « 20,18 h » ; le vérificateur compare `ratio`/`jours`/`heures` avec la tolérance du contrat).
- **Anomalies** : `Doses.quantites_invalides` remplace la liste par défaut quand « 1.5 » est une valeur valable (poids, heures). M04, M05 et M10 gardent leur passage local (même résultat octet pour octet, l'ordre d'affectation diffère).
- **Graphiques** : `empile` et `barres` (légende sous le graphique, axe sans « () » pour un comptage ; `barres` accepte `top`, `horizontal`, étiquettes inclinées au-delà de 8 valeurs), `rejets`, et `fonction` (`dessiner(spec, con, attendus, base)`) pour un graphique vraiment propre à la mission, listé dans `reference/README.md` comme les autres.
4. Vérifier : taille < 1,5 Mo (`TAILLE_MAX_MISSION`), deux exécutions identiques, puis la solution de référence du formateur (dossier privé, un adaptateur de plus) passe `python -m controles.verifier --mission MNN --etape tout --strict`.

Les 9 anomalies standard (contrat § 5) : doublon exact, `id_conflit`, `id_manquant`, `cle_inconnue`, format décimal, format date, casse/espaces, `quantite_invalide`, encodage (`ecrire_csv(..., encodage="cp1252")` pour M02 et M06).

## v7-data.json

Un bloc par mission (`missions.<code>`), écrit par `exporter_v7_data` à chaque génération : vérités de l'échantillon et nombres clés (indicateurs et unités, tables, rejets, nettoyage, versions SCD2, frontières, agrégats par axe) pour le générateur de schémas. Fusion par code de mission, écriture atomique : générer une mission ne touche jamais le bloc d'une autre. Montants en millimes. Ne pas éditer à la main.

## Décisions de format fixées ici

- Montants source : point **ou** virgule = séparateur décimal ; espace = séparateur de milliers (`1 240,000` = 1 240 TND). L'exemple `12 500` du contrat est donc lu « douze mille cinq cents ».
- Dates source : `AAAA-MM-JJ`, `JJ/MM/AAAA` (jour d'abord), `4 mars 2026`.
- CSV des sources : séparateur `;` (la virgule sert de décimale) ; exports de l'entrepôt : séparateur `,`.
