# Générateurs de données — édition « Solen BI 22 h » (V7)

Ces scripts fabriquent les données **100 % synthétiques** de chaque mission et calculent les valeurs de référence **depuis la vérité terrain**, jamais depuis un ETL. Le vérificateur des étudiants (`modele-binome/controles/verifier.py`) compare leurs sorties à ces références.

## Régénérer

Depuis `github/` :

```bash
.venv/bin/python authoring/generateurs/mission00_commerce360.py
```

Le script réécrit uniquement `modele-binome/tronc-commun/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/, sources/, reference/}`, met à jour `v7-data.json` et, si le dossier formateur existe, écrit la vérité brute privée dans `formateur/fable-v7-solen-22h/solutions/verite_terrain/<mission>/` (jamais dans le dépôt public).

Reproductible : deux exécutions donnent les mêmes octets (graine fixe, classeur Excel zippé avec des dates figées, SVG avec `svg.hashsalt` fixe, PNG sans métadonnées variables).

| Mission | Script | Graine | Taille générée |
|---|---|---|---|
| 00 tronc commun — Maison Zitouna | `mission00_commerce360.py` (+ `textes_mission00.py`) | 260001 | ≈ 640 Ko |

Versions utilisées pour la génération de référence : Python 3.13.17 · pandas 3.1.0 · openpyxl 3.1.5 · matplotlib 3.11.2 · pytest 9.2.0. Le code n'utilise que la bibliothèque standard + openpyxl + matplotlib.

## Ce que produit une mission

```
<mission>/fiche_mission.md  cahier_des_charges.md  dictionnaire.md
<mission>/echantillon/      ventes.csv (≤ 12 lignes) catalogue.xlsx boutiques.json operations.sqlite attendu.md attendu.json
<mission>/sources/lot1/     4 sources (CSV, Excel, JSON, SQLite)
<mission>/sources/lot2/     4 sources : nouvelles lignes + lignes déjà chargées (rejeu) + 1 changement SCD2
<mission>/reference/        attendu_lot1.json attendu_lot2.json contrat_entrepot.json README.md visuels/*.png|svg
```

- `attendu_<lot>.json` : comptes par source, nettoyage (formats normalisés, doublons, lignes déjà chargées), rejets par motif et par source, lignes par table, indicateurs globaux, agrégats par axe (zone, boutique, mois, famille…) en millimes entiers, versions SCD2 avec `valid_from`/`valid_to`, contrôles de date frontière. `attendu_lot2.json` vaut aussi pour le rejeu (bloc `rejeu`).
- `contrat_entrepot.json` : ce qui rend le vérificateur générique pour les 11 missions — tables, colonnes, colonnes entières, clés étrangères, dimension SCD2 et faits qui y pointent, vue d'analyse SQL « mouvements », indicateurs (code, formule française, agrégat SQL, tolérance), axes, colonnes obligatoires de `rejets.csv`, sommes de l'export, textes obligatoires de l'application, lots et étapes.

## Comment la référence est calculée (indépendance)

1. Le script de mission crée des **événements vrais** (ventes, retours…) avec une graine.
2. `construire_csv()` les rend en texte « sale » et **ajoute** des lignes piégées comptées (doublons exacts, conflits d'identifiant, identifiants vides, clés inconnues, quantités invalides) ; les formats de montants, dates et codes sont mélangés sur une part des lignes vraies.
3. Les tables de l'étoile sont construites **directement depuis les événements vrais** (`tables_verite`), puis `entrepot_verite()` les charge en mémoire et exécute la vue d'analyse du contrat : ce sont les valeurs attendues. Aucune source n'est relue.
4. Un double contrôle Python pur (sans SQL) vérifie ventes nettes et marge dans le script ; le formateur dispose en plus de `solutions/controle_croise_mission00.py` (pandas sur la vérité brute).

## Ajouter une mission (M01…M10)

Un script `missionNN_<nom>.py` de 150 à 250 lignes, plus ses textes :

1. Définir `TABLES` (`table_dim_date()` + dimensions + faits ; une dimension `dimension_scd2` avec `valid_from`/`valid_to` nullable) et un `MissionSpec` : textes, `Source`s, `Indicateur`s (formule française + agrégat SQL sur la vue), `vue_analyse` (une ligne par mouvement : colonnes d'axes + colonnes additives), `axes`, `SCD2` (faits concernés + dates frontières), `visuels`.
2. Générer la vérité (`rng_mission(graine)`), puis pour chaque lot : `construire_csv(evenements, ChampsCSV(...), Doses(...), rng, nouvel_id, rejouees)` ; écrire les sources avec `ecrire_csv` (option `encodage="cp1252"`), `ecrire_excel([Feuille…])`, `ecrire_json`, `ecrire_sqlite(ddl, données)`.
3. Remplir un `LotResultat` par lot (comptes, nettoyage, rejets par source, **état cumulé** des tables de vérité, bloc incrément) et appeler `produire_reference(spec, lots)`, puis l'échantillon (`calculer_attendu_echantillon`), `exporter_v7_data` et `ecrire_verite_privee`.
4. Vérifier : taille < 2 Mo, deux exécutions identiques, puis la solution de référence (`solutions/solen_ref`, un adaptateur de plus) passe `python -m controles.verifier --mission MNN --etape tout`.

Les 9 anomalies standard (contrat § 5) : doublon exact, `id_conflit`, `id_manquant`, `cle_inconnue`, format décimal, format date, casse/espaces, `quantite_invalide`, encodage (`ecrire_csv(..., encodage="cp1252")` pour M02 et M06).

## v7-data.json

Exporte, par mission, les vérités de l'échantillon et les nombres clés (indicateurs, tables, rejets, versions SCD2, agrégats par axe) pour le générateur de schémas. Montants en millimes. Ne pas éditer à la main.

## Décisions de format fixées ici

- Montants source : point **ou** virgule = séparateur décimal ; espace = séparateur de milliers (`1 240,000` = 1 240 TND). L'exemple `12 500` du contrat est donc lu « douze mille cinq cents ».
- Dates source : `AAAA-MM-JJ`, `JJ/MM/AAAA` (jour d'abord), `4 mars 2026`.
- CSV des sources : séparateur `;` (la virgule sert de décimale) ; exports de l'entrepôt : séparateur `,`.
