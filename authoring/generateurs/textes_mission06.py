"""Textes et règles de la mission M06 (Dar Azur, hôtellerie). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

# Une ligne par mouvement : séjours (+), annulations (−) et chambres disponibles (une ligne par
# établissement et par jour du calendrier). Tout est rangé dans le mois de la DATE D'ARRIVÉE.
VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, e.etablissement_id,
       e.etablissement_id || ' ' || printf('%04d-%02d', d.annee, d.mois) AS etab_mois,
       c.canal_id, c.taux_commission_pct,
       f.nuitees AS nuitees_vendues, 0 AS nuitees_annulees, f.montant_millimes AS montant,
       0 AS remboursement, f.commission_millimes AS commission, 1 AS sejours, 0 AS chambres_nuits
FROM fact_sejour f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_etablissement e ON e.etablissement_key = f.etablissement_key
JOIN dim_canal c ON c.canal_key = f.canal_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), e.etablissement_id,
       e.etablissement_id || ' ' || printf('%04d-%02d', d.annee, d.mois), c.canal_id, c.taux_commission_pct,
       0, a.nuitees, 0, a.remboursement_millimes, 0, 0, 0
FROM fact_annulation a
JOIN dim_date d ON d.date_key = a.date_key
JOIN dim_etablissement e ON e.etablissement_key = a.etablissement_key
JOIN dim_canal c ON c.canal_key = a.canal_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), e.etablissement_id,
       e.etablissement_id || ' ' || printf('%04d-%02d', d.annee, d.mois), NULL, NULL,
       0, 0, 0, 0, 0, 0, e.nombre_chambres
FROM dim_date d CROSS JOIN dim_etablissement e
"""

# L'attribut historisé est un entier. Le vérificateur compare désormais l'attribut SCD2 en texte des deux côtés ;
# le CAST est gardé pour que la référence publiée (attendu_*.json : scd2.attribut) reste identique.
ATTRIBUT_SCD2 = "CAST(taux_commission_pct AS TEXT)"

SPEC_TEXTES = dict(
    code="M06",
    numero="06",
    titre="Hôtellerie — Dar Azur",
    entreprise="Dar Azur",
    secteur="petit groupe de quatre maisons d'hôtes : Hammamet, Sidi Bou Saïd, Tozeur et Djerba",
    contexte=("Dar Azur exploite quatre maisons d'hôtes (64 chambres au total). Le logiciel de réception exporte "
              "les séjours dans un CSV, l'inventaire des chambres vit dans un classeur Excel, les contrats des "
              "canaux de vente (direct, agence en ligne, tour-opérateur, entreprise) et leurs commissions dans un "
              "fichier JSON, et les annulations et paiements dans une petite base SQLite. Le gérant voit des "
              "réservations partout, mais ne sait pas si ses chambres sont vraiment remplies ni ce qu'il reste "
              "après les annulations. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nJe veux savoir quelles maisons remplissent leurs chambres et lesquelles "
             "gagnent de l'argent. Par établissement et par mois : les nuitées vendues, le taux d'occupation, le "
             "revenu net d'annulations et le RevPAR. Je dois décider où mettre l'effort commercial cet hiver.\n\n"
             "Pour information : à partir du 15 juillet, l'agence en ligne ne nous prend plus 18 % mais 15 % de "
             "commission. Les séjours arrivés avant cette date gardent 18 %.\n\nDites-moi aussi ce que vous avez "
             "dû écarter, et pourquoi.\n\nLamia Ben Salah, directrice (Solen Digital, pour le compte de Dar Azur)"),
    grain="un séjour (une réservation de chambre, de la date d'arrivée à la date de départ)",
    sources=[
        Source("sejours.csv", "csv", "Séjours exportés du logiciel de réception (séparateur `;`). "
               "`lot1` en UTF-8, **`lot2` en Windows-1252 (cp1252)**.", [
                   ColonneSource("sejour_id", "texte", "Identifiant du séjour.", "DA-10234"),
                   ColonneSource("date_reservation", "texte", "Jour de la réservation, trois formats possibles.", "12/02/2026"),
                   ColonneSource("date_arrivee", "texte", "Jour d'arrivée (première nuit).", "2026-03-04"),
                   ColonneSource("date_depart", "texte", "Jour de départ (pas de nuit ce jour-là).", "7 mars 2026"),
                   ColonneSource("etablissement", "texte", "Code établissement (casse et espaces variables).", " dah "),
                   ColonneSource("type_chambre", "texte", "Code du type de chambre.", "DBL"),
                   ColonneSource("canal", "texte", "Code du canal de vente.", "OTA"),
                   ColonneSource("nuitees", "texte", "Nombre de nuits = départ − arrivée.", "3"),
                   ColonneSource("prix_total", "texte", "Prix du séjour en TND (taxe de séjour comprise), formats variés.",
                                 "1 007,000"),
                   ColonneSource("provenance", "texte", "Pays du client (avec accents).", "Algérie"),
               ], ["formats de prix et de dates mélangés", "doublons", "identifiants vides ou en conflit",
                   "codes inconnus", "nuitées invalides", "lot2 : encodage cp1252",
                   "lot2 : recopie les séjours de juin partis en juillet"]),
        Source("chambres.xlsx", "excel", "Feuille `Chambres` (en-têtes à la ligne 3) + feuille `Types`.", [
            ColonneSource("Établissement", "texte", "Code établissement (une cellule mal saisie).", " dsb"),
            ColonneSource("Nom", "texte", "Nom de l'établissement.", "Dar Azur Tozeur"),
            ColonneSource("Ville", "texte", "Ville.", "Tozeur"),
            ColonneSource("Type de chambre", "texte", "Code du type (feuille Types).", "FAM"),
            ColonneSource("Nombre de chambres", "nombre ou texte", "Chambres de ce type dans l'établissement.", "6"),
            ColonneSource("Prix affiché (TND / nuit)", "nombre ou texte", "Prix public indicatif (non utilisé).", "180,000"),
            ColonneSource("Code type / Libellé type", "texte", "Feuille Types.", "FAM / Familiale"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte",
            "capacité d'un établissement = somme de ses lignes"]),
        Source("canaux.json", "json", "Contrats des canaux de vente avec l'historique du taux de commission.", [
            ColonneSource("canaux[].code", "texte", "Code canal.", "OTA"),
            ColonneSource("canaux[].libelle", "texte", "`direct`, `agence en ligne`, `tour-opérateur`, `entreprise`.",
                          "agence en ligne"),
            ColonneSource("canaux[].historique[].taux_commission", "nombre", "Commission en % du prix total.", "18"),
            ColonneSource("canaux[].historique[].valide_depuis", "date ISO", "Début du taux (inclus).", "2025-01-01"),
        ], ["un taux écrit `10.0`", "lot2 : une deuxième version pour OTA (15 % au 2026-07-15)"]),
        Source("operations.sqlite", "sqlite", "Base opérationnelle : tables `annulation`, `motif_annulation`, "
               "`paiement`, `parametre`.", [
                   ColonneSource("annulation.id", "entier", "Numéro interne de la ligne.", "57"),
                   ColonneSource("annulation.numero_annulation", "texte", "Numéro de l'annulation (unique).", "AN26-0057"),
                   ColonneSource("annulation.ref_sejour", "texte", "`sejour_id` du séjour annulé.", "DA-10234"),
                   ColonneSource("annulation.code_etablissement", "texte", "Établissement du séjour.", "DDJ"),
                   ColonneSource("annulation.date_annulation", "texte", "Date et heure de l'annulation.", "2026-03-01 10:15:00"),
                   ColonneSource("annulation.montant_rembourse", "réel", "Montant rendu au client en TND (0 possible).", "395.25"),
                   ColonneSource("annulation.code_motif", "texte", "Motif → `motif_annulation`.", "PER"),
                   ColonneSource("annulation.statut", "texte", "`CONFIRMEE` ou `RETIREE` (le client a renoncé).", "CONFIRMEE"),
                   ColonneSource("paiement.*", "—", "Encaissements par séjour (non chargés ; variante 3).",
                                 "DA-10234 · 520.5 · carte"),
               ], ["annulations retirées", "annulations vers un séjour inconnu",
                   "lot2 : recopie des annulations depuis le 20 juin"]),
    ],
    indicateurs=[
        Indicateur("nuitees_vendues", "Nuitées vendues", "nombre",
                   "nuitées des séjours acceptés − nuitées des séjours annulés (annulations CONFIRMEE acceptées)",
                   "SUM(nuitees_vendues) - SUM(nuitees_annulees)"),
        Indicateur("chambres_disponibles", "Chambres disponibles (chambres × nuits)", "nombre",
                   "nombre de chambres de l'établissement × nombre de nuits de la période (jours de dim_date)",
                   "SUM(chambres_nuits)", principal=False),
        Indicateur("taux_occupation", "Taux d'occupation", "ratio",
                   "nuitées vendues / (chambres × nuits de la période)",
                   "ROUND(1.0 * (SUM(nuitees_vendues) - SUM(nuitees_annulees)) / NULLIF(SUM(chambres_nuits), 0), 6)",
                   tolerance=0.0001),
        Indicateur("montant_sejours_millimes", "Montant des séjours", "millimes",
                   "somme des prix totaux des séjours acceptés", "SUM(montant)", principal=False),
        Indicateur("remboursements_millimes", "Remboursements", "millimes",
                   "somme des montants remboursés des annulations CONFIRMEE acceptées", "SUM(remboursement)",
                   principal=False),
        Indicateur("revenu_net_millimes", "Revenu net d'annulations", "millimes",
                   "montant des séjours − remboursements", "SUM(montant) - SUM(remboursement)"),
        Indicateur("revpar_millimes", "RevPAR", "millimes",
                   "revenu net / (chambres × nuits de la période), en TND par chambre disponible, arrondi au millime",
                   "CAST(ROUND(1.0 * (SUM(montant) - SUM(remboursement)) / NULLIF(SUM(chambres_nuits), 0)) AS INTEGER)"),
        Indicateur("commissions_millimes", "Commissions des canaux", "millimes",
                   "somme de montant × taux de commission (version valable à la date d'arrivée) / 100",
                   "SUM(commission)", principal=False),
        Indicateur("sejours", "Séjours acceptés", "nombre", "nombre de lignes de fact_sejour", "SUM(sejours)",
                   principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_etablissement": "etablissement_id", "par_mois": "mois", "par_etablissement_mois": "etab_mois"},
    scd2=SCD2("dim_canal", "canal_key", "canal_id", ATTRIBUT_SCD2,
              faits=[("fact_sejour", "canal_key", "date_key"), ("fact_annulation", "canal_key", "date_key")],
              frontieres=[("OTA", "2026-06-30"), ("OTA", "2026-07-14"), ("OTA", "2026-07-15"), ("DIR", "2026-07-15")],
              changement="Le canal OTA (agence en ligne) passe d'une commission de 18 % à 15 % le 2026-07-15 "
                         "(inclus). Cette information arrive avec `lot2/canaux.json`.",
              libelle_attribut="taux_commission_pct (%)"),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`DA-90003` deux fois avec des nuitées différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`sejour_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "établissement `DMH`, canal `AGC`, type `VIL`, annulation vers `DA-09990`",
         "rejet `cle_inconnue`"),
        ("Format décimal", "`520.500`, `520,500`, `520.5`, `520,5`, `1 007,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` dah `, `Ota`, ` dsb`", "supprimer les espaces autour + majuscules"),
        ("Nuitées invalides", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`lot2/sejours.csv` en cp1252 (`Algérie`, `Côte d'Ivoire`)",
         "lot1 en UTF-8 ; lot2 en `cp1252` (essayer UTF-8, sinon cp1252)"),
        ("Annulation retirée", "`statut = 'RETIREE'`", "ignorer (ce n'est pas un rejet) : le séjour reste vendu"),
        ("Ligne déjà chargée", "lot2 recopie les séjours arrivés en juin et partis en juillet",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD, cle_inconnue="code absent des référentiels (établissement, type de chambre de "
                                              "cet établissement, canal) ou annulation vers un séjour inconnu",
                quantite_invalide="nuitées nulles, négatives ou non entières"),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`sejour_id` vide → `id_manquant` ;",
        "`sejour_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "établissement, canal ou couple (établissement, type de chambre) absent des référentiels → `cle_inconnue` ;",
        "nuitées non entières ou ≤ 0 → `quantite_invalide` ;",
        "`sejour_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Annulations : `RETIREE` ignorée → `ref_sejour` absente de `fact_sejour` = `cle_inconnue` "
        "(numero_ligne = `annulation.id`) → `numero_annulation` déjà chargé = ignorée.",
    ],
    regles_metier=[
        "Grain : un séjour = une ligne de `fact_sejour`. Nuitées = date de départ − date d'arrivée (toujours vrai pour les lignes acceptées).",
        "**Date du fait = date d'arrivée** : toutes les nuitées et tout le montant d'un séjour sont rangés dans le mois "
        "de son arrivée, même si le client part le mois suivant (règle à clarifier, décision de la direction).",
        "Montant d'un séjour = `prix_total` converti en millimes (taxe de séjour comprise).",
        "Commission = montant × taux de commission du canal / 100, avec le taux de la **version valable à la date "
        "d'arrivée** (pas à la date de réservation). Les montants sont des multiples de 0,500 TND : le calcul tombe juste au millime.",
        "Une annulation `CONFIRMEE` reprend l'établissement, le canal (même version), les nuitées et la **date "
        "d'arrivée** de son séjour (`ref_sejour` → `fact_sejour`) ; la date d'annulation est gardée en texte.",
        "Remboursement = `montant_rembourse` converti en millimes (0 possible : séjour non remboursable).",
        "Capacité : `nombre_chambres` d'un établissement = somme de ses lignes de la feuille `Chambres`. Chambres "
        "disponibles d'une période = nombre_chambres × nombre de jours de la période présents dans `dim_date` "
        "(un mois entier : 31, 28 ou 30 nuits). Total : 64 × 181 = 11 584 après le lot 1, 64 × 243 = 15 552 après le lot 2.",
        "Taux d'occupation et RevPAR ne se somment pas : on les recalcule à partir des sommes (nuitées, revenu net, chambres disponibles).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": "Un client arrive le 30 juin et repart le 3 juillet (3 nuitées) : le séjour compte-t-il en juin, "
                    "en juillet, ou nuit par nuit ? Et une réservation faite le 10 juillet sur l'agence en ligne pour "
                    "une arrivée le 20 juillet : commission à 18 % (taux du jour de la réservation) ou 15 % (taux du jour d'arrivée) ?",
        "options": "- A : tout au mois d'arrivée ; commission au taux valable à la date d'arrivée.\n"
                   "- B : nuit par nuit (2 nuits en juin, 1 en juillet) ; il faut découper le montant.\n"
                   "- C : commission au taux valable à la date de réservation.",
        "decision": "A. La date d'arrivée est la date du fait : nuitées, montant, commission (version du canal valable "
                    "ce jour-là) et annulations éventuelles sont rangés dans le mois d'arrivée. Simple, stable et "
                    "identique pour tous les établissements.",
    },
    variantes=[
        "Nouvel indicateur : revenu net après commissions = revenu net d'annulations − commissions, par canal et par établissement.",
        "Nouvelle règle : répartir les nuitées et le montant d'un séjour à cheval sur deux mois nuit par nuit "
        "(option B) — le fait passe au grain « nuitée » ; comparer le taux d'occupation de juin et juillet avec la règle actuelle.",
        "Nouvelle source : charger la table `paiement` de `operations.sqlite` dans un `fact_paiement` et suivre le "
        "taux d'encaissement = paiements reçus / revenu net d'annulations.",
    ],
    ecrans_app=[
        ("Vue direction", "nuitées vendues, taux d'occupation, revenu net d'annulations et RevPAR, puis le revenu "
                          "net par mois et par établissement (barres empilées) ; filtres période et établissement."),
        ("Détail par canal", "chaque canal avec ses versions : OTA à 18 % jusqu'au 2026-07-14, puis 15 % ; "
                             "nuitées, revenu net et commissions par version."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot ; annulations retirées ; "
                                "séjours déjà chargés ignorés au lot 2."),
    ],
    textes_app=["Vue direction", "Détail par canal", "Qualité des données"],
    export_sommes={"fact_sejour": ["nuitees", "montant_millimes", "commission_millimes"],
                   "fact_annulation": ["nuitees", "remboursement_millimes"],
                   "dim_etablissement": ["nombre_chambres"]},
    visuels=[
        {"type": "empile", "indicateur": "revenu_net_millimes", "x": "mois", "serie": "etablissement_id",
         "ordre_series": ["DAH", "DSB", "DTZ", "DDJ"], "fichier": "revenu_net_par_mois_et_etablissement",
         "titre": "Revenu net d'annulations par mois et par établissement", "libelle_x": "Mois (d'arrivée)",
         "libelle_serie": "Établissement"},
        {"type": "barres", "indicateurs": ["taux_occupation"], "axe": "etablissement_id",
         "fichier": "taux_occupation_par_etablissement", "titre": "Taux d'occupation par établissement (janvier → août)",
         "libelle_x": "Établissement"},
        {"type": "barres", "indicateurs": ["revpar_millimes"], "axe": "mois", "fichier": "revpar_par_mois",
         "titre": "RevPAR par mois (TND par chambre disponible)", "libelle_x": "Mois", "libelle_y": "RevPAR"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"sejours": "sejours.csv", "annulations": "operations.sqlite"},
)
