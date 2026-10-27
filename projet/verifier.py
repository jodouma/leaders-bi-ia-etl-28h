"""Vérifications publiques : vos modules et vos sorties, jamais les corrigés.

Chaque contrôle travaille dans un dossier temporaire et lit les sorties existantes.
Il ne termine pas une mission à votre place et ne remet pas votre base à zéro.
"""
import argparse
import importlib
import sqlite3
import tempfile
from pathlib import Path
from lecture import DATA, OUTPUTS, lire_csv


class VerificationErreur(Exception):
    pass


def exiger(condition, message):
    if not condition:
        raise VerificationErreur(message)


def module(nom):
    return importlib.import_module(nom)


def exception_attendue(type_erreur, fonction, *args):
    try:
        fonction(*args)
    except type_erreur:
        return
    raise VerificationErreur(f"Une erreur {type_erreur.__name__} était attendue.")


def catalogues_publics():
    return ({r["product_id"]: r["product_name"] for r in lire_csv(DATA / "produits.csv")},
            {r["shop_id"]: r["shop_name"] for r in lire_csv(DATA / "boutiques.csv")})


def vente_exemple(identifiant="ESSAI", quantity="2", price="0.125"):
    return {"sale_id": identifiant, "date": "2026-03-11", "shop_id": " nbe ",
            "product_id": " p01 ", "quantity": quantity, "unit_price_tnd": price}


def lecture_base(chemin):
    exiger(Path(chemin).is_file(), "Base absente : exécuter modele.py, puis chargement.py.")
    # mode=ro empêche ce vérificateur de créer ou d'écrire votre base.
    connexion = sqlite3.connect(Path(chemin).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return connexion.execute("""SELECT f.sale_id, d.full_date, s.shop_id, p.product_id,
            f.quantity, f.unit_price_millimes, f.amount_millimes FROM fact_sales f
            JOIN dim_date d ON f.date_key=d.date_key
            JOIN dim_shop s ON f.shop_key=s.shop_key
            JOIN dim_product p ON f.product_key=p.product_key ORDER BY f.sale_id""").fetchall()
    finally:
        connexion.close()


def verifier_01(dossier):
    calculer = module("calcul").calculer_total
    vide = calculer([])
    exiger(type(vide) is int and vide == 0, "Une liste vide doit donner l'entier 0 millime.")
    exiger(calculer([{"quantity": 4, "unit_price_millimes": 125},
                     {"quantity": 3, "unit_price_millimes": 200}]) == 1100,
           "Additionner quantité × prix, pas seulement les prix.")
    exiger(calculer([{"quantity": 3, "unit_price_millimes": 4500},
                     {"quantity": 3, "unit_price_millimes": 1500}]) == 18000,
           "La variation attend 18000 millimes.")
    return "Calcul entier validé, y compris une variation."


def verifier_02(dossier):
    chemin = dossier / "lecture avec espaces.csv"
    chemin.write_text('\ufeffnom,texte\n"École, nord",001\n', encoding="utf-8")
    lignes = lire_csv(chemin)
    exiger(lignes == [{"nom": "École, nord", "texte": "001"}],
           "Préserver accents, virgule entre guillemets et valeurs texte.")
    exiger(len(lire_csv(DATA / "ventes_initiales.csv")) == 16, "La source Atlas contient 16 lignes.")
    return "Lecture CSV validée ; 16 lignes source."


def verifier_03(dossier):
    nettoyer = module("nettoyage").nettoyer
    produits, boutiques = catalogues_publics()
    exemple = vente_exemple()
    retenues, rejets, doublons = nettoyer([exemple, dict(exemple), vente_exemple("INVALIDE", "0")], produits, boutiques)
    exiger((len(retenues), len(rejets), len(doublons)) == (1, 1, 1), "Distinguer une retenue, un rejet, un doublon.")
    exiger(retenues[0]["shop_id"] == "NBE" and retenues[0]["product_id"] == "P01", "Normaliser les codes.")
    exiger(type(retenues[0]["unit_price_millimes"]) is int
           and type(retenues[0]["amount_millimes"]) is int
           and retenues[0]["unit_price_millimes"] == 125 and retenues[0]["amount_millimes"] == 250,
           "0.125 TND × 2 donne 250 millimes entiers.")
    exiger(bool(rejets[0].get("motif")), "Chaque rejet explique son motif.")
    exception_attendue(ValueError, nettoyer, [exemple, vente_exemple(quantity="3")], produits, boutiques)
    for nom in ("ventes_nettoyees.csv", "rejets.csv", "doublons.csv"):
        exiger((OUTPUTS / nom).is_file(), f"Sortie absente : {nom}. Exécuter nettoyage.py.")
    propres = lire_csv(OUTPUTS / "ventes_nettoyees.csv")
    exiger(len(propres) == 12, "Le fichier nettoyé initial doit contenir 12 ventes.")
    exiger(sum(int(v["amount_millimes"]) for v in propres) == 99000, "Le lot initial vaut 99000 millimes.")
    exiger(len(lire_csv(OUTPUTS / "rejets.csv")) == 3, "Trois rejets sont à expliquer.")
    exiger(len(lire_csv(OUTPUTS / "doublons.csv")) == 1, "Un doublon exact est à isoler.")
    return "Qualité validée : 12 retenues, 3 rejets, 1 doublon ; 99.000 TND."


def verifier_04(dossier):
    creer = module("modele").creer_modele
    base = dossier / "schema.sqlite"
    creer(base)
    connexion = sqlite3.connect(base)
    try:
        connexion.execute("PRAGMA foreign_keys = ON")
        tables = {r[0] for r in connexion.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        exiger({"dim_product", "dim_shop", "dim_date", "fact_sales"} <= tables, "Il faut 3 dimensions et fact_sales.")
        exiger(len(connexion.execute("PRAGMA foreign_key_list(fact_sales)").fetchall()) == 3, "Trois relations sont attendues.")
        connexion.execute("INSERT INTO dim_product VALUES (1, 'TEST', 'Essai')")
        connexion.commit()
    finally:
        connexion.close()
    creer(base)
    with sqlite3.connect(base) as connexion:
        exiger(connexion.execute("SELECT COUNT(*) FROM dim_product").fetchone()[0] == 1,
               "creer_modele ne doit pas effacer les dimensions existantes.")
    exiger((OUTPUTS / "atlas.sqlite").is_file(), "Exécuter modele.py pour créer outputs/atlas.sqlite.")
    return "Schéma validé ; second appel sans effacement."


def verifier_05(dossier):
    produits, boutiques = catalogues_publics()
    ventes, _, _ = module("nettoyage").nettoyer([vente_exemple()], produits, boutiques)
    base = dossier / "chargement.sqlite"
    module("modele").creer_modele(base)
    charger = module("chargement").charger
    exiger(charger(ventes, produits, boutiques, base) == {"inserted": 1, "existing": 0}, "Première insertion attendue.")
    exiger(charger(ventes, produits, boutiques, base) == {"inserted": 0, "existing": 1}, "Le rejeu doit reconnaître la vente.")
    nouvelle = dict(ventes[0], sale_id="NOUVELLE")
    conflit = dict(ventes[0], quantity=3, amount_millimes=375)
    exception_attendue(ValueError, charger, [nouvelle, conflit], produits, boutiques, base)
    exiger(len(lecture_base(base)) == 1, "Le conflit doit annuler aussi l'insertion précédente du même lot.")
    lignes = lecture_base(OUTPUTS / "atlas.sqlite")
    exiger(len(lignes) in (12, 14), "Charger d'abord les 12 ventes initiales (14 après ajout).")
    attendus = (32, 99000) if len(lignes) == 12 else (35, 115500)
    exiger((sum(r[4] for r in lignes), sum(r[6] for r in lignes)) == attendus,
           "Quantité ou montant actuel incohérent.")
    return f"Chargement transactionnel et rejeu validés ; base actuelle : {len(lignes)} faits."


def verifier_06(dossier):
    produits, boutiques = catalogues_publics()
    ventes, _, _ = module("nettoyage").nettoyer(lire_csv(DATA / "ventes_initiales.csv"), produits, boutiques)
    base = dossier / "ajout.sqlite"
    module("modele").creer_modele(base)
    module("chargement").charger(ventes, produits, boutiques, base)
    ajouter = module("incremental").ajouter
    resultat = ajouter(DATA / "ventes_ajout.csv", base, DATA)
    exiger(resultat == {"raw": 3, "accepted": 3, "rejected": 0, "duplicates": 0, "inserted": 2, "existing": 1},
           "L'ajout attend 3 retenues, 2 nouvelles et 1 existante.")
    rejeu = ajouter(DATA / "ventes_ajout.csv", base, DATA)
    exiger(rejeu["inserted"] == 0 and rejeu["existing"] == 3, "Le rejeu doit insérer 0 vente.")
    lignes = lecture_base(OUTPUTS / "atlas.sqlite")
    exiger((len(lignes), sum(r[4] for r in lignes), sum(r[6] for r in lignes)) == (14, 35, 115500),
           "Exécuter incremental.py : la base finale attend 14 faits, 35 unités, 115500 millimes.")
    return "Ajout et rejeu validés : 14 faits, 35 unités, 115.500 TND."


def verifier_07(dossier):
    lignes = lecture_base(OUTPUTS / "atlas.sqlite")
    exiger(bool(lignes), "Charger des ventes avant le rapport.")
    bilan = module("rapport").generer(OUTPUTS / "atlas.sqlite", dossier / "rapport.html")
    exiger(bilan["facts"] == len(lignes) and bilan["quantity"] == sum(r[4] for r in lignes)
           and bilan["amount_millimes"] == sum(r[6] for r in lignes), "Le rapport doit interroger la base actuelle.")
    exiger(bilan["period_start"] == min(r[1] for r in lignes)
           and bilan["period_end"] == max(r[1] for r in lignes), "Calculer la période depuis les dates chargées.")
    for categorie in ("shops", "products"):
        exiger(sum(r["amount_millimes"] for r in bilan[categorie]) == bilan["amount_millimes"], "Les agrégats doivent retrouver le total.")
    cible = OUTPUTS / "rapport_atlas.html"
    exiger(cible.is_file(), "Exécuter rapport.py pour créer outputs/rapport_atlas.html.")
    html = cible.read_text(encoding="utf-8")
    montant = f"{bilan['amount_millimes'] // 1000}.{bilan['amount_millimes'] % 1000:03d}"
    exiger(montant in html and bilan["period_start"] in html and bilan["period_end"] in html,
           "Le fichier HTML doit refléter le montant et la période actuels ; le régénérer après ajout.")
    exiger("<style" in html and "TND" in html, "Fournir un rapport autonome et des unités explicites.")
    return f"Rapport validé sur la base actuelle : {montant} TND."


CONTROLES = {f"{n:02d}": globals()[f"verifier_{n:02d}"] for n in range(1, 8)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mission", choices=[*CONTROLES, "tout"])
    args = parser.parse_args()
    numeros = list(CONTROLES) if args.mission == "tout" else [args.mission]
    for numero in numeros:
        try:
            with tempfile.TemporaryDirectory(prefix="atlas-verification-") as dossier:
                message = CONTROLES[numero](Path(dossier))
            print(f"[OK {numero}] {message}")
        except NotImplementedError as erreur:
            print(f"[À CONSTRUIRE {numero}] {erreur}")
            print("Compléter la fonction de cette mission, enregistrer le fichier, puis relancer ce contrôle.")
            return 1
        except Exception as erreur:
            print(f"[À REVOIR {numero}] {type(erreur).__name__} : {erreur}")
            print("Vérifier la mission et ses sorties précédentes. Le contrôle ne les crée pas à votre place.")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
