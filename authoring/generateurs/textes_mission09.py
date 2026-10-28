"""Textes et règles de la mission M09 (Scène Libre, événementiel). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

# Une ligne par mouvement : billets vendus, remboursements acceptés, et une ligne « capacité » par événement
# (la capacité ne dépend d'aucun canal : son canal_id vaut « (capacité) »).
# `mois` = mois de l'ÉVÉNEMENT (date du spectacle), pas de la vente.
VUE = """
SELECT substr(e.date_evenement, 1, 7) AS mois, e.evenement_id, e.type_evenement, e.lieu,
       c.canal_id, c.frais_pour_mille,
       1 AS vendu, 0 AS rembourse, f.prix_millimes AS prix, 0 AS montant_rembourse,
       f.frais_millimes AS frais, 0 AS capacite
FROM fact_billet f
JOIN dim_evenement e ON e.evenement_key = f.evenement_key
JOIN dim_canal c ON c.canal_key = f.canal_key
UNION ALL
SELECT substr(e.date_evenement, 1, 7), e.evenement_id, e.type_evenement, e.lieu, c.canal_id, c.frais_pour_mille,
       0, 1, 0, r.montant_millimes, 0, 0
FROM fact_remboursement r
JOIN dim_evenement e ON e.evenement_key = r.evenement_key
JOIN dim_canal c ON c.canal_key = r.canal_key
UNION ALL
SELECT substr(e.date_evenement, 1, 7), e.evenement_id, e.type_evenement, e.lieu, '(capacité)', NULL,
       0, 0, 0, 0, 0, e.capacite
FROM dim_evenement e
"""

SPEC_TEXTES = dict(
    code="M09",
    numero="09",
    titre="Événementiel — Scène Libre",
    entreprise="Scène Libre",
    secteur="organisateur de spectacles : concerts, théâtre et festivals dans cinq salles",
    contexte=("Scène Libre organise des concerts, des pièces de théâtre et des festivals dans cinq salles "
              "(Tunis, Sousse, Sfax, Nabeul). Les billets sont vendus par quatre canaux : la billetterie en ligne, "
              "le guichet, des revendeurs et des partenaires. Chaque canal prend des frais de distribution. La "
              "billetterie exporte les billets dans un CSV, le programme et les tarifs vivent dans un classeur "
              "Excel, les canaux et leurs frais dans un fichier JSON, et les remboursements dans une petite base "
              "SQLite. Cette saison, un concert a été annulé, un autre reporté. La direction ne sait plus quels "
              "spectacles se vendent vraiment bien. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNous vendons beaucoup de billets, mais après les annulations, les "
             "remboursements et les frais des canaux, que reste-t-il ? Je veux, par événement, par type de "
             "spectacle, par mois et par canal : les billets nets, le taux de remplissage et les recettes nettes. "
             "Dites-moi quels événements se vendent bien une fois les remboursements déduits, et ce que vous avez "
             "dû écarter dans les fichiers.\n\nPour information : à partir du 15 juillet, les revendeurs (canal "
             "REV) prennent 11 % au lieu de 9 %. Les billets vendus avant gardent l'ancien taux.\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Scène Libre)"),
    grain="un billet vendu",
    sources=[
        Source("billets.csv", "csv", "Billets exportés de la billetterie (UTF-8, séparateur `;`), une ligne = un billet.", [
            ColonneSource("billet_id", "texte", "Identifiant du billet.", "B100234"),
            ColonneSource("evenement", "texte", "Code de l'événement (casse et espaces variables).", " ev04 "),
            ColonneSource("canal", "texte", "Code du canal de vente.", "REV"),
            ColonneSource("date_vente", "texte", "Date de la vente, trois formats possibles.", "04/03/2026"),
            ColonneSource("categorie", "texte", "Catégorie de place : `VIP`, `CAT1` ou `CAT2`.", "cat2"),
            ColonneSource("nb_places", "texte", "Nombre de places de la ligne : toujours 1.", "1"),
            ColonneSource("prix", "texte", "Prix payé en TND (tarif réduit possible), formats variés.", "35,000"),
        ], ["formats de prix et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "événements ou canaux inconnus", "nb_places invalide", "lot2 : recopie des 16 derniers billets de juin"]),
        Source("evenements.xlsx", "excel", "Feuille `Programme` (en-têtes à la ligne 3) + feuille `Tarifs`.", [
            ColonneSource("Code", "texte", "Code événement (une cellule mal saisie).", " ev07"),
            ColonneSource("Événement", "texte", "Nom du spectacle.", "Contes de la Médina"),
            ColonneSource("Type", "texte", "`Concert`, `Théâtre` ou `Festival`.", "Théâtre"),
            ColonneSource("Lieu / Ville", "texte", "Salle et ville.", "Salle Zéphyr / Sfax"),
            ColonneSource("Date", "date ou texte", "Date (actuelle) du spectacle.", "4 avril 2026"),
            ColonneSource("Capacité", "nombre ou texte", "Nombre de places de la salle pour ce spectacle.", "1 000"),
            ColonneSource("Statut", "texte", "`programmé`, `reporté` ou `annulé` (information).", "reporté"),
            ColonneSource("Tarifs : Code événement / Catégorie / Tarif (TND)", "texte / nombre",
                          "Feuille Tarifs : prix plein par catégorie.", "EV03 / VIP / 80"),
        ], ["titre au-dessus du tableau", "dates et capacités stockées comme texte",
            "lot2 : le programme complet (anciens et nouveaux événements)"]),
        Source("canaux.json", "json", "Référentiel des canaux de vente avec l'historique des frais de distribution.", [
            ColonneSource("canaux[].code", "texte", "Code canal.", "REV"),
            ColonneSource("canaux[].libelle", "texte", "Nom du canal.", "revendeur"),
            ColonneSource("canaux[].historique[].frais_distribution", "nombre ou texte",
                          "Frais en % du prix du billet.", "4,5 %"),
            ColonneSource("canaux[].historique[].valide_depuis", "date ISO", "Début du taux (inclus).", "2025-09-01"),
        ], ["frais écrits de plusieurs façons (`9`, `\"9 %\"`, `\"4,5 %\"`)",
            "lot2 : une deuxième version pour REV (11 % au 2026-07-15)"]),
        Source("remboursements.sqlite", "sqlite",
               "Base opérationnelle du service client : tables `remboursement`, `motif`, `parametre`.", [
            ColonneSource("remboursement.id", "entier", "Numéro interne de la ligne.", "57"),
            ColonneSource("remboursement.numero", "texte", "Numéro de la demande (unique).", "RB26-00057"),
            ColonneSource("remboursement.billet_id", "texte", "`billet_id` du billet concerné.", "B100234"),
            ColonneSource("remboursement.date_operation", "texte", "Date et heure de la décision.", "2026-04-12 10:15:00"),
            ColonneSource("remboursement.montant_rembourse", "réel", "Montant rendu en TND (0 si rien n'est rendu).", "35.0"),
            ColonneSource("remboursement.code_motif", "texte", "`ANNULATION`, `REPORT` ou `CONVENANCE` (convenance personnelle : toujours `REFUSE`, donc ignorée) → `motif`.", "REPORT"),
            ColonneSource("remboursement.statut", "texte",
                          "`REMBOURSE` (argent rendu), `CONSERVE` (billet gardé pour la nouvelle date) ou `REFUSE`.",
                          "CONSERVE"),
            ColonneSource("remboursement.traite_par", "texte", "Agent du service client.", "agent-2"),
        ], ["demandes refusées ou billets conservés (report)", "remboursements vers un billet inconnu",
            "lot2 : recopie des remboursements depuis le 1er juin"]),
    ],
    indicateurs=[
        Indicateur("billets_vendus", "Billets vendus", "nombre", "nombre de billets acceptés", "SUM(vendu)",
                   principal=False),
        Indicateur("billets_rembourses", "Billets remboursés", "nombre",
                   "nombre de remboursements acceptés (statut REMBOURSE, un par billet)", "SUM(rembourse)",
                   principal=False),
        Indicateur("billets_nets", "Billets nets", "nombre", "billets vendus − billets remboursés",
                   "SUM(vendu) - SUM(rembourse)"),
        Indicateur("taux_remplissage", "Taux de remplissage", "ratio",
                   "billets nets / capacité des événements (somme des capacités des événements concernés)",
                   "ROUND(1.0 * (SUM(vendu) - SUM(rembourse)) / NULLIF(SUM(capacite), 0), 6)", tolerance=0.0001),
        Indicateur("recettes_billets_millimes", "Recettes des billets", "millimes",
                   "somme des prix payés des billets acceptés", "SUM(prix)", principal=False),
        Indicateur("remboursements_millimes", "Remboursements", "millimes",
                   "somme des montants rendus des remboursements acceptés", "SUM(montant_rembourse)", principal=False),
        Indicateur("frais_distribution_millimes", "Frais de distribution", "millimes",
                   "somme des frais des billets acceptés (taux du canal valable à la date de vente)", "SUM(frais)",
                   principal=False),
        Indicateur("recettes_nettes_millimes", "Recettes nettes", "millimes",
                   "recettes des billets − remboursements − frais de distribution",
                   "SUM(prix) - SUM(montant_rembourse) - SUM(frais)"),
    ],
    vue_analyse=VUE,
    axes={"par_evenement": "evenement_id", "par_type": "type_evenement", "par_mois": "mois",
          "par_lieu": "lieu", "par_canal": "canal_id"},
    scd2=SCD2("dim_canal", "canal_key", "canal_id", "frais_pour_mille",
              faits=[("fact_billet", "canal_key", "date_key"), ("fact_remboursement", "canal_key", "date_key")],
              frontieres=[("REV", "2026-06-30"), ("REV", "2026-07-14"), ("REV", "2026-07-15"), ("WEB", "2026-07-15")],
              changement="Le canal REV (revendeur) passe de 9 % (90 ‰) à 11 % (110 ‰) de frais de distribution le "
                         "2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`."),
    regles=[
        ("Doublon exact", "le même billet deux fois, caractère pour caractère", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`B800037` deux fois avec des `nb_places` différents",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`billet_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "événement `EV99`, canal `TEL`, remboursement vers `B990001`", "rejet `cle_inconnue`"),
        ("Format décimal", "`35.000`, `35,000`, `35`, `35,5`, `1 240,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` ev04 `, `Rev`, `cat2`, ` ev07`", "supprimer les espaces autour + majuscules"),
        ("Nombre de places invalide", "`0`, `-2`, `1.5`, `2,5`", "rejet `quantite_invalide` (une ligne = un billet : `nb_places` vaut 1)"),
        ("Frais écrits en texte", "`9`, `\"9 %\"`, `\"4,5 %\"`", "convertir en pour mille entier : 9 % → 90, 4,5 % → 45"),
        ("Demande non remboursée", "`statut` = `CONSERVE` ou `REFUSE`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les 16 derniers billets de juin et les remboursements depuis le 1er juin",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD, cle_inconnue="code absent du référentiel (événement, canal) ou billet inconnu"),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`billet_id` vide → `id_manquant` ;",
        "`billet_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "événement ou canal absent des référentiels → `cle_inconnue` ;",
        "`nb_places` différent de l'entier 1 → `quantite_invalide` ;",
        "`billet_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Remboursements : seules les lignes `REMBOURSE` comptent (`CONSERVE` et `REFUSE` ignorées) → `billet_id` absent "
        "de `fact_billet` = `cle_inconnue` (numero_ligne = `remboursement.id`) → `numero` déjà chargé = ignoré.",
    ],
    regles_metier=[
        "Prix d'un billet = le prix **payé** (`prix` du CSV) : un tarif réduit peut être inférieur au tarif de la feuille Tarifs.",
        "Frais de distribution d'un billet = prix × `frais_pour_mille` / 1 000, arrondi au millime le plus proche, avec le "
        "taux du canal valable à la **date de vente** (les prix étant en TND entiers, le calcul tombe juste).",
        "Les frais sont calculés **une fois**, dans `fact_billet`. Un remboursement ne les annule pas et ne les recalcule pas.",
        "Un remboursement prend l'événement de son billet, la **date de l'opération** (heure ignorée) et la version du canal "
        "du billet valable à cette date.",
        "Montant d'un remboursement = `montant_rembourse` converti en millimes. Un billet a au plus un remboursement `REMBOURSE`.",
        "Taux de remplissage = billets nets / capacité. Il se lit **par événement** (ou par type, lieu, mois de l'événement). "
        "Par canal il n'a pas de sens : la capacité est rangée sous le canal `(capacité)` dans la vue d'analyse.",
        "`mois` (axe d'analyse) = mois de la **date de l'événement**, pas de la vente.",
        "`dim_evenement` : un événement par ligne ; `date_evenement` = date actuelle du spectacle (après report). Le lot 2 "
        "apporte le programme complet : les événements déjà connus ne changent pas, les nouveaux sont ajoutés.",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": ("1) Un billet REV vendu le 10 juillet (frais 9 %) est remboursé le 20 juillet, après le passage à "
                     "11 %. Quels frais garde-t-on ? 2) Un spectacle reporté : une demande « report » compte-t-elle "
                     "comme un remboursement ?"),
        "options": ("- 1A : frais de la version valable à la date de **vente** (9 %), jamais recalculés.\n"
                    "- 1B : frais recalculés à la date du remboursement (11 %).\n"
                    "- 1C : frais annulés quand le billet est remboursé.\n"
                    "- 2A : toute demande de motif `REPORT` est un remboursement.\n"
                    "- 2B : seul le statut `REMBOURSE` compte ; `CONSERVE` (billet gardé pour la nouvelle date) n'est "
                    "pas un remboursement."),
        "decision": ("1A et 2B. Les frais sont dus au canal le jour de la vente : ils restent au taux de la version valable "
                     "à la date de vente et ne sont ni remboursés ni recalculés. Un report n'est pas un remboursement : "
                     "seules les lignes `REMBOURSE` (argent rendu) réduisent les billets nets et les recettes, quel que "
                     "soit le motif (`ANNULATION` ou `REPORT`)."),
    },
    variantes=[
        "Nouvel indicateur : recette nette moyenne par billet net = recettes nettes / billets nets, par événement.",
        "Nouvelle règle : en cas d'annulation, le canal rend ses frais → frais nets = frais des billets non remboursés ; "
        "nouvelle colonne `frais_rendus_millimes` dans `fact_remboursement`.",
        "Changement historique : le canal PAR (partenaire) passe de 6 % à 5 % le 2026-08-01 (deuxième version de PAR "
        "dans `dim_canal`).",
    ],
    ecrans_app=[
        ("Vue direction", "billets nets, taux de remplissage, recettes nettes ; recettes nettes par mois de l'événement et "
                          "par type (barres empilées) ; filtre par événement et par type."),
        ("Détail par canal", "chaque canal avec ses versions de frais : REV à 90 ‰ jusqu'au 2026-07-14, puis 110 ‰ ; "
                             "recettes et frais par version."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot ; demandes non remboursées ignorées."),
    ],
    textes_app=["Vue direction", "Détail par canal", "Qualité des données"],
    export_sommes={"fact_billet": ["prix_millimes", "frais_millimes"], "fact_remboursement": ["montant_millimes"],
                   "dim_evenement": ["capacite"]},
    visuels=[
        {"type": "empile", "indicateur": "recettes_nettes_millimes", "x": "mois", "serie": "type_evenement",
         "ordre_series": ["Concert", "Théâtre", "Festival"], "fichier": "recettes_nettes_par_mois_et_type",
         "titre": "Recettes nettes par mois de l'événement et par type", "libelle_x": "Mois de l'événement",
         "libelle_serie": "Type"},
        {"type": "barres", "indicateurs": ["taux_remplissage"], "axe": "evenement_id",
         "fichier": "taux_remplissage_par_evenement", "titre": "Taux de remplissage par événement (billets nets / capacité)",
         "libelle_x": "Événement"},
        {"type": "barres", "indicateurs": ["recettes_nettes_millimes", "remboursements_millimes"], "axe": "type_evenement",
         "fichier": "recettes_nettes_et_remboursements_par_type",
         "titre": "Recettes nettes et remboursements par type de spectacle", "libelle_x": "Type", "libelle_y": "Montant"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"billets": "billets.csv", "remboursements": "remboursements.sqlite"},
    regle_mois="(billets, remboursements et une ligne « capacité » par événement). L'axe `mois` est le mois de la "
               "**date de l'événement** ; `par_canal` contient une clé `(capacité)` (les capacités ne dépendent "
               "d'aucun canal), et le taux de remplissage d'un canal est vide.",
)
