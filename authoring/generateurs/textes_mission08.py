"""Textes et règles de la mission M08 (TechniServ, maintenance). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

EQUIPEMENT_MOBILE = "EQ-017"          # groupe électrogène du Groupe Nakhla : CT-03 → CT-09 le 2026-07-15
CONTRAT_AVANT, CONTRAT_APRES = "CT-03", "CT-09"
DATE_CHANGEMENT = date(2026, 7, 15)
SANS_OBJET = "(revenu contrat)"       # valeur des axes équipement/catégorie/type sur les lignes de revenu

VUE = f"""
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, c.contrat_id, c.client, e.equipement_id, e.categorie,
       f.type_intervention,
       1 AS intervention,
       CASE WHEN f.type_intervention = 'correctif' THEN 1 ELSE 0 END AS correctif,
       CASE WHEN f.type_intervention = 'correctif' THEN f.delai_heures ELSE 0 END AS delai_correctif,
       f.heures, f.cout_main_oeuvre_millimes AS cout_mo, f.cout_pieces_millimes AS cout_pieces, 0 AS revenu
FROM fact_intervention f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_equipement e ON e.equipement_key = f.equipement_key
JOIN dim_contrat c ON c.contrat_key = f.contrat_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), c.contrat_id, c.client, '{SANS_OBJET}', '{SANS_OBJET}', '{SANS_OBJET}',
       0, 0, 0, 0, 0, 0, r.revenu_millimes
FROM fact_revenu_contrat r
JOIN dim_date d ON d.date_key = r.date_key
JOIN dim_contrat c ON c.contrat_key = r.contrat_key
"""

MOTIFS = dict(MOTIFS_STANDARD)
MOTIFS["cle_inconnue"] = ("équipement absent du parc (`equipements.json`), pièce absente du catalogue, "
                          "ou consommation de pièce vers une intervention inconnue")
MOTIFS["quantite_invalide"] = "heures facturées nulles, négatives ou non entières"

SPEC_TEXTES = dict(
    code="M08",
    numero="08",
    titre="Maintenance · TechniServ",
    entreprise="TechniServ",
    secteur="maintenance sous contrat de climatisations, ascenseurs et groupes électrogènes",
    contexte=("TechniServ entretient et dépanne 48 équipements (climatisations, ascenseurs, groupes électrogènes) "
              "chez 9 clients, avec 10 contrats de maintenance payés au mois. Les techniciens saisissent chaque "
              "intervention dans un export CSV ; le catalogue des pièces et les taux horaires sont dans un classeur "
              "Excel ; le parc d'équipements (site, catégorie, contrat) est dans un fichier JSON ; les contrats et "
              "les pièces consommées sont dans la base SQLite de l'atelier. Personne ne sait dire quels contrats "
              "rapportent vraiment, une fois payés les techniciens et les pièces. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNos contrats de maintenance sont-ils rentables ? Je veux, par contrat, par "
             "équipement, par catégorie et par mois : le nombre d'interventions, le délai moyen d'intervention sur "
             "les pannes, le coût d'intervention (pièces + main-d'œuvre) et la marge de service. Je veux savoir "
             "quels contrats et quels équipements mobilisent le plus nos équipes. Dites-moi aussi ce que vous avez "
             "dû écarter, et pourquoi.\n\nPour information : le 15 juillet, le groupe électrogène EQ-017 du Groupe "
             "Nakhla passe du contrat standard CT-03 au contrat premium CT-09. Ses interventions d'avant doivent "
             "rester sur CT-03.\n\nLamia Ben Salah, directrice (Solen Digital, pour le compte de TechniServ)"),
    grain="une intervention d'un technicien sur un équipement",
    sources=[
        Source("interventions.csv", "csv", "Interventions saisies par les techniciens (UTF-8, séparateur `;`).", [
            ColonneSource("intervention_id", "texte", "Identifiant de l'intervention.", "INT-26-00412"),
            ColonneSource("equipement", "texte", "Code de l'équipement (casse et espaces variables).", " eq-017 "),
            ColonneSource("date_demande", "texte", "Jour de la demande du client (panne) ou de la planification "
                                                    "(préventif), trois formats possibles.", "14/07/2026"),
            ColonneSource("heure_demande", "texte", "Heure de la demande, heure pleine.", "19:00"),
            ColonneSource("date_intervention", "texte", "Jour où le technicien intervient, trois formats.", "15 juillet 2026"),
            ColonneSource("heure_intervention", "texte", "Heure d'arrivée du technicien, heure pleine.", "09:00"),
            ColonneSource("technicien", "texte", "Code du technicien.", "T08"),
            ColonneSource("heures", "texte", "Heures facturées (heure entamée = heure due), entier.", "3"),
            ColonneSource("type_intervention", "texte", "`préventif` (visite planifiée) ou `correctif` (panne).", "Correctif"),
        ], ["formats de dates mélangés", "doublons", "identifiants vides ou en conflit", "équipements inconnus",
            "heures invalides", "lot2 : recopie des interventions du 30 juin"]),
        Source("pieces.xlsx", "excel", "Feuille `Pièces` (en-têtes à la ligne 3) + feuille `Taux horaires`.", [
            ColonneSource("Code pièce", "texte", "Code de la pièce (une cellule mal saisie).", " pc-204"),
            ColonneSource("Désignation", "texte", "Nom de la pièce.", "Contacteur de porte"),
            ColonneSource("Catégorie", "texte", "Code catégorie d'équipement.", "ASC"),
            ColonneSource("Prix unitaire (TND)", "nombre ou texte", "Prix d'achat unitaire de la pièce.", "1 450,000"),
            ColonneSource("Code catégorie / Catégorie / Taux horaire (TND)", "texte / nombre",
                          "Feuille Taux horaires : coût d'une heure de technicien par catégorie.", "ASC / Ascenseur / 62,5"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("equipements.json", "json", "Parc d'équipements avec l'historique du contrat de chaque équipement.", [
            ColonneSource("equipements[].id", "texte", "Code équipement.", "EQ-017"),
            ColonneSource("equipements[].designation", "texte", "Description.", "Groupe électrogène 250 kVA"),
            ColonneSource("equipements[].categorie", "texte", "Code catégorie (CLIM, ASC, GE).", "GE"),
            ColonneSource("equipements[].site", "texte", "Site du client.", "Résidences Nakhla — Les Berges"),
            ColonneSource("equipements[].historique[].contrat", "texte", "Contrat qui couvre l'équipement.", "CT-03"),
            ColonneSource("equipements[].historique[].valide_depuis", "date", "Début (inclus), ISO ou JJ/MM/AAAA.", "2024-09-01"),
        ], ["une date au format JJ/MM/AAAA", "un code contrat en minuscules",
            "lot2 : une deuxième version pour EQ-017 (CT-09 au 2026-07-15)"]),
        Source("operations.sqlite", "sqlite", "Base de l'atelier : tables `contrat`, `consommation`, `parametre`.", [
            ColonneSource("contrat.contrat_id", "texte", "Code du contrat.", "CT-03"),
            ColonneSource("contrat.client", "texte", "Client.", "Groupe Nakhla"),
            ColonneSource("contrat.revenu_mensuel", "texte", "Forfait mensuel en TND, formats variés.", "11 750,000"),
            ColonneSource("contrat.date_debut / date_fin", "texte", "Période du contrat (ISO ; fin vide = en cours).", "2026-03-01"),
            ColonneSource("consommation.id", "entier", "Numéro interne de la ligne.", "812"),
            ColonneSource("consommation.intervention_id", "texte", "Intervention qui a consommé la pièce.", "INT-26-00412"),
            ColonneSource("consommation.code_piece", "texte", "Code pièce du catalogue.", "PC-301"),
            ColonneSource("consommation.quantite", "entier", "Quantité consommée.", "6"),
            ColonneSource("consommation.saisi_le", "texte", "Date et heure de saisie.", "2026-03-04 15:00"),
        ], ["consommations vers une intervention inconnue", "pièces inconnues",
            "lot2 : recopie des consommations des interventions du 30 juin"]),
    ],
    indicateurs=[
        Indicateur("interventions", "Interventions", "nombre",
                   "nombre d'interventions acceptées (préventives + correctives)", "SUM(intervention)"),
        Indicateur("interventions_correctives", "Interventions correctives", "nombre",
                   "nombre d'interventions de type correctif", "SUM(correctif)", principal=False),
        Indicateur("delai_total_correctif_heures", "Délai total des correctifs", "nombre",
                   "somme de delai_heures des interventions correctives", "SUM(delai_correctif)", principal=False),
        Indicateur("delai_moyen_heures", "Délai moyen d'intervention", "heures",
                   "somme des délais des interventions correctives / nombre d'interventions correctives ; délai = "
                   "(date + heure d'intervention) − (date + heure de demande), en heures ; le préventif est exclu ; "
                   "résultat en heures décimales (ex. 20,18 h)",
                   "ROUND(1.0 * SUM(delai_correctif) / NULLIF(SUM(correctif), 0), 6)", tolerance=0.01),
        Indicateur("heures_facturees", "Heures facturées", "nombre", "somme des heures des interventions",
                   "SUM(heures)", principal=False),
        Indicateur("cout_main_oeuvre_millimes", "Coût de main-d'œuvre", "millimes",
                   "heures × taux horaire de la catégorie de l'équipement", "SUM(cout_mo)", principal=False),
        Indicateur("cout_pieces_millimes", "Coût des pièces", "millimes",
                   "somme de quantité × prix unitaire des pièces consommées acceptées", "SUM(cout_pieces)", principal=False),
        Indicateur("cout_intervention_millimes", "Coût d'intervention", "millimes",
                   "coût des pièces + coût de main-d'œuvre", "SUM(cout_mo) + SUM(cout_pieces)"),
        Indicateur("revenu_contrat_millimes", "Revenu de contrat", "millimes",
                   "somme des forfaits mensuels dus (un par contrat et par mois actif)", "SUM(revenu)", principal=False),
        Indicateur("marge_service_millimes", "Marge de service", "millimes",
                   "revenu de contrat − coût d'intervention ; marge PARTIELLE (ni déplacements, ni frais de "
                   "structure) ; à lire par contrat, par mois ou au total",
                   "SUM(revenu) - SUM(cout_mo) - SUM(cout_pieces)"),
    ],
    vue_analyse=VUE,
    axes={"par_mois": "mois", "par_contrat": "contrat_id", "par_categorie": "categorie",
          "par_equipement": "equipement_id", "par_type": "type_intervention"},
    scd2=SCD2("dim_equipement", "equipement_key", "equipement_id", "contrat_id",
              faits=[("fact_intervention", "equipement_key", "date_key")],
              frontieres=[(EQUIPEMENT_MOBILE, "2026-06-30"), (EQUIPEMENT_MOBILE, "2026-07-14"),
                          (EQUIPEMENT_MOBILE, "2026-07-15"), ("EQ-001", "2026-07-15")],
              changement=f"L'équipement {EQUIPEMENT_MOBILE} (groupe électrogène du Groupe Nakhla) passe du contrat "
                         f"« {CONTRAT_AVANT} » au contrat « {CONTRAT_APRES} » le {DATE_CHANGEMENT.isoformat()} "
                         "(inclus). Cette information arrive avec `lot2/equipements.json`."),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`INT-26-90037` deux fois avec des heures différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`intervention_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "équipement `EQ-099`, pièce `PC-999`, consommation vers `INT-26-08812`", "rejet `cle_inconnue`"),
        ("Format décimal", "`1 450,000`, `62,5`, `38.75` (Excel, SQLite)",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` eq-017 `, `Correctif`, ` t04`, ` pc-204`, ` ct-05`",
         "supprimer les espaces autour ; codes en majuscules ; type en minuscules"),
        ("Heures invalides", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`préventif`, `Résidences`", "lire les fichiers en UTF-8"),
        ("Ligne déjà chargée", "lot2 recopie les interventions du 30 juin et leurs consommations",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=MOTIFS,
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`intervention_id` vide → `id_manquant` ;",
        "`intervention_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "équipement absent de `equipements.json` (ou sans version de contrat à la date d'intervention) → `cle_inconnue` ;",
        "heures non entières ou ≤ 0 → `quantite_invalide` ;",
        "`intervention_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Consommations (`consommation`, numero_ligne = `consommation.id`) : intervention déjà chargée par un lot "
        "précédent → ignorée ; intervention ni acceptée dans ce lot ni déjà chargée → `cle_inconnue` ; pièce absente "
        "du catalogue → `cle_inconnue`.",
    ],
    regles_metier=[
        "`delai_heures` = (date + heure d'intervention) − (date + heure de demande), en heures entières, pour TOUTES les "
        "interventions ; le délai moyen n'utilise que les correctives.",
        "`cout_main_oeuvre_millimes` = `heures` × taux horaire de la catégorie de l'équipement (feuille `Taux horaires`).",
        "`cout_pieces_millimes` = somme, sur les consommations acceptées de l'intervention, de `quantite` × prix "
        "unitaire du catalogue (0 si aucune pièce).",
        "Une intervention prend la version de l'équipement valable à sa **date d'intervention** : son `contrat_key` "
        "est le contrat de cette version.",
        "`fact_revenu_contrat` : une ligne par contrat et par mois du lot où le contrat est actif le 1er du mois "
        "(`date_debut` ≤ 1er du mois et `date_fin` vide ou ≥ 1er du mois). `revenu_id` = `<contrat_id>-<AAAA-MM>` "
        "(ex. `CT-03-2026-07`), `date_key` = 1er du mois, `revenu_millimes` = `revenu_mensuel` en millimes.",
        "`categorie` de `dim_equipement` = libellé de la feuille Taux horaires (ex. `GE` → `Groupe électrogène`).",
        "`type_intervention` stocké en minuscules : `préventif` ou `correctif`.",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2).",
        "La marge de service est partielle et n'a de sens que par contrat, par mois ou au total : les lignes de revenu "
        f"n'ont ni équipement ni catégorie (valeur `{SANS_OBJET}` dans la vue d'analyse).",
    ],
    regle_a_clarifier={
        "question": ("(1) EQ-017 tombe en panne le 14 juillet à 19 h (contrat CT-03) ; le technicien intervient le "
                     "15 juillet à 9 h, jour où EQ-017 passe sur CT-09. Quel contrat paie cette intervention ? "
                     "(2) Une visite préventive est planifiée trois semaines à l'avance : quel est son « délai » ?"),
        "options": ("- (1) A : contrat valable à la date de la demande (CT-03).\n"
                    "- (1) B : contrat valable à la date d'intervention (CT-09).\n"
                    "- (2) A : délai = intervention − planification, compté dans le délai moyen.\n"
                    "- (2) B : délai calculé et stocké, mais le préventif est exclu du délai moyen."),
        "decision": ("(1) B : chaque intervention est rattachée à la version de l'équipement valable à sa DATE "
                     "D'INTERVENTION (la date du fait, `date_key`) ; c'est ce jour-là que le travail et les pièces "
                     "sont consommés. (2) B : `delai_heures` est stocké pour toutes les interventions, mais le délai "
                     "moyen ne compte que les correctives (la « demande » d'un préventif est une date de "
                     "planification, pas une panne)."),
    },
    variantes=[
        "Nouvel indicateur : taux de respect du délai garanti = correctifs avec `delai_heures` ≤ délai garanti du "
        "contrat (nouvelle colonne `delai_garanti_heures` dans `contrat`) / correctifs.",
        "Nouvelle règle : une intervention de plus de 8 heures facturées doit être validée par le chef d'atelier ; "
        "sans validation, elle est rejetée avec un nouveau motif `heures_hors_plafond`.",
        "Changement historique : l'ascenseur EQ-014 passe au contrat CT-09 le 2026-08-01 (deuxième équipement "
        "historisé ; ses interventions de juillet restent sur CT-03).",
    ],
    ecrans_app=[
        ("Vue direction", "interventions, délai moyen (correctifs), coût d'intervention, revenu et marge de service ; "
                          "coût d'intervention par mois et par catégorie (barres empilées) ; filtres période et contrat."),
        ("Détail par équipement", "chaque équipement avec ses versions de contrat : EQ-017 sur CT-03 jusqu'au "
                                  "2026-07-14, puis CT-09 ; ses interventions et son coût par contrat et par mois."),
        ("Qualité des données", "lignes lues, gardées, déjà chargées, rejetées par motif, par source et par lot."),
    ],
    textes_app=["Vue direction", "Détail par équipement", "Qualité des données"],
    export_sommes={"fact_intervention": ["heures", "delai_heures", "cout_main_oeuvre_millimes", "cout_pieces_millimes"],
                   "fact_revenu_contrat": ["revenu_millimes"], "dim_contrat": ["revenu_mensuel_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "cout_intervention_millimes", "x": "mois", "serie": "categorie",
         "ordre_series": ["Climatisation", "Ascenseur", "Groupe électrogène"],
         "fichier": "cout_intervention_par_mois_et_categorie",
         "titre": "Coût d'intervention par mois et par catégorie", "libelle_x": "Mois", "libelle_serie": "Catégorie"},
        {"type": "barres", "indicateurs": ["revenu_contrat_millimes", "cout_intervention_millimes", "marge_service_millimes"],
         "axe": "contrat_id", "fichier": "revenu_cout_marge_par_contrat",
         "titre": "Revenu, coût d'intervention et marge de service par contrat", "libelle_x": "Contrat",
         "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["delai_moyen_heures"], "axe": "mois", "fichier": "delai_moyen_par_mois",
         "titre": "Délai moyen d'intervention sur panne (correctifs) par mois", "libelle_x": "Mois",
         "libelle_y": "Délai moyen"},
        {"type": "barres", "indicateurs": ["cout_intervention_millimes"], "axe": "equipement_id || ' (' || categorie || ')'",
         "top": 10, "horizontal": True, "fichier": "cout_top10_equipements",
         "titre": "Les 10 équipements au coût d'intervention le plus élevé (janvier → août)", "libelle_x": "Équipement"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"interventions": "interventions.csv", "consommations": "operations.sqlite"},
    regle_mois="(interventions et revenus de contrat réunis). Un mouvement est rangé dans le mois **de sa propre date**.",
)
