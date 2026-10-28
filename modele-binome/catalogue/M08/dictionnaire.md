# Dictionnaire des données — Mission 08 (TechniServ)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `interventions.csv` (csv)

Interventions saisies par les techniciens (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `intervention_id` | texte | Identifiant de l'intervention. | `INT-26-00412` |
| `equipement` | texte | Code de l'équipement (casse et espaces variables). | ` eq-017 ` |
| `date_demande` | texte | Jour de la demande du client (panne) ou de la planification (préventif), trois formats possibles. | `14/07/2026` |
| `heure_demande` | texte | Heure de la demande, heure pleine. | `19:00` |
| `date_intervention` | texte | Jour où le technicien intervient, trois formats. | `15 juillet 2026` |
| `heure_intervention` | texte | Heure d'arrivée du technicien, heure pleine. | `09:00` |
| `technicien` | texte | Code du technicien. | `T08` |
| `heures` | texte | Heures facturées (heure entamée = heure due), entier. | `3` |
| `type_intervention` | texte | `préventif` (visite planifiée) ou `correctif` (panne). | `Correctif` |

### `pieces.xlsx` (excel)

Feuille `Pièces` (en-têtes à la ligne 3) + feuille `Taux horaires`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code pièce` | texte | Code de la pièce (une cellule mal saisie). | ` pc-204` |
| `Désignation` | texte | Nom de la pièce. | `Contacteur de porte` |
| `Catégorie` | texte | Code catégorie d'équipement. | `ASC` |
| `Prix unitaire (TND)` | nombre ou texte | Prix d'achat unitaire de la pièce. | `1 450,000` |
| `Code catégorie / Catégorie / Taux horaire (TND)` | texte / nombre | Feuille Taux horaires : coût d'une heure de technicien par catégorie. | `ASC / Ascenseur / 62,5` |

### `equipements.json` (json)

Parc d'équipements avec l'historique du contrat de chaque équipement.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `equipements[].id` | texte | Code équipement. | `EQ-017` |
| `equipements[].designation` | texte | Description. | `Groupe électrogène 250 kVA` |
| `equipements[].categorie` | texte | Code catégorie (CLIM, ASC, GE). | `GE` |
| `equipements[].site` | texte | Site du client. | `Résidences Nakhla — Les Berges` |
| `equipements[].historique[].contrat` | texte | Contrat qui couvre l'équipement. | `CT-03` |
| `equipements[].historique[].valide_depuis` | date | Début (inclus), ISO ou JJ/MM/AAAA. | `2024-09-01` |

### `operations.sqlite` (sqlite)

Base de l'atelier : tables `contrat`, `consommation`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `contrat.contrat_id` | texte | Code du contrat. | `CT-03` |
| `contrat.client` | texte | Client. | `Groupe Nakhla` |
| `contrat.revenu_mensuel` | texte | Forfait mensuel en TND, formats variés. | `11 750,000` |
| `contrat.date_debut / date_fin` | texte | Période du contrat (ISO ; fin vide = en cours). | `2026-03-01` |
| `consommation.id` | entier | Numéro interne de la ligne. | `812` |
| `consommation.intervention_id` | texte | Intervention qui a consommé la pièce. | `INT-26-00412` |
| `consommation.code_piece` | texte | Code pièce du catalogue. | `PC-301` |
| `consommation.quantite` | entier | Quantité consommée. | `6` |
| `consommation.saisi_le` | texte | Date et heure de saisie. | `2026-03-04 15:00` |

## Entrepôt

### `dim_date`

Calendrier : une ligne par jour de la période chargée.

| Colonne | Type | Description |
|---|---|---|
| `date_key` | INTEGER | Clé du jour au format AAAAMMJJ (ex. 20260304). |
| `date_complete` | TEXT | Date ISO AAAA-MM-JJ. |
| `annee` | INTEGER | Année. |
| `mois` | INTEGER | Mois de 1 à 12. |
| `jour` | INTEGER | Jour du mois. |

### `dim_contrat`

Contrats de maintenance (table `contrat` de la base de l'atelier).

| Colonne | Type | Description |
|---|---|---|
| `contrat_key` | INTEGER | Clé technique (1, 2, 3…). |
| `contrat_id` | TEXT | Code contrat normalisé (strip + majuscules), ex. `CT-03`. |
| `client` | TEXT | Nom du client. |
| `revenu_mensuel_millimes` | INTEGER | Forfait mensuel du contrat en millimes. |
| `date_debut` | TEXT | Début du contrat, AAAA-MM-JJ. |
| `date_fin` | TEXT | Fin du contrat, AAAA-MM-JJ ; vide = sans fin prévue. |

### `dim_equipement`

Équipements avec l'historique de leur contrat (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `equipement_key` | INTEGER | Clé technique d'une VERSION d'équipement. |
| `equipement_id` | TEXT | Code équipement, ex. `EQ-017` (plusieurs versions possibles). |
| `designation` | TEXT | Description de l'équipement. |
| `categorie` | TEXT | Libellé de la catégorie (feuille Taux horaires), ex. `Ascenseur`. |
| `site` | TEXT | Site du client où se trouve l'équipement. |
| `contrat_id` | TEXT | Contrat qui couvre l'équipement pendant cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_intervention`

Une intervention acceptée.

| Colonne | Type | Description |
|---|---|---|
| `intervention_id` | TEXT | Identifiant de l'intervention (clé métier unique). |
| `date_key` | INTEGER | Jour de l'intervention. |
| `equipement_key` | INTEGER | Version de l'équipement valable à la date d'intervention. |
| `contrat_key` | INTEGER | Contrat de cette version de l'équipement. |
| `technicien` | TEXT | Code technicien normalisé, ex. `T04`. |
| `type_intervention` | TEXT | `préventif` ou `correctif` (minuscules). |
| `demande_le` | TEXT | Date et heure de la demande, `AAAA-MM-JJ HH:MM`. |
| `intervention_le` | TEXT | Date et heure de l'intervention, `AAAA-MM-JJ HH:MM`. |
| `heures` | INTEGER | Heures facturées (entier > 0). |
| `delai_heures` | INTEGER | intervention_le − demande_le, en heures. |
| `cout_main_oeuvre_millimes` | INTEGER | heures × taux horaire de la catégorie, en millimes. |
| `cout_pieces_millimes` | INTEGER | Somme quantité × prix des pièces consommées acceptées (0 si aucune). |

### `fact_revenu_contrat`

Le forfait d'un contrat pour un mois où il est actif.

| Colonne | Type | Description |
|---|---|---|
| `revenu_id` | TEXT | `<contrat_id>-<AAAA-MM>`, ex. `CT-03-2026-07` (clé métier unique). |
| `date_key` | INTEGER | 1er jour du mois. |
| `contrat_key` | INTEGER | Contrat. |
| `revenu_millimes` | INTEGER | Forfait mensuel en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `interventions` | Interventions | nombre | nombre d'interventions acceptées (préventives + correctives) |
| `interventions_correctives` | Interventions correctives | nombre | nombre d'interventions de type correctif |
| `delai_total_correctif_heures` | Délai total des correctifs | nombre | somme de delai_heures des interventions correctives |
| `delai_moyen_heures` | Délai moyen d'intervention | heures, nombre décimal | somme des délais des interventions correctives / nombre d'interventions correctives ; délai = (date + heure d'intervention) − (date + heure de demande), en heures ; le préventif est exclu ; résultat en heures décimales (ex. 20,18 h) |
| `heures_facturees` | Heures facturées | nombre | somme des heures des interventions |
| `cout_main_oeuvre_millimes` | Coût de main-d'œuvre | millimes | heures × taux horaire de la catégorie de l'équipement |
| `cout_pieces_millimes` | Coût des pièces | millimes | somme de quantité × prix unitaire des pièces consommées acceptées |
| `cout_intervention_millimes` | Coût d'intervention | millimes | coût des pièces + coût de main-d'œuvre |
| `revenu_contrat_millimes` | Revenu de contrat | millimes | somme des forfaits mensuels dus (un par contrat et par mois actif) |
| `marge_service_millimes` | Marge de service | millimes | revenu de contrat − coût d'intervention ; marge PARTIELLE (ni déplacements, ni frais de structure) ; à lire par contrat, par mois ou au total |
