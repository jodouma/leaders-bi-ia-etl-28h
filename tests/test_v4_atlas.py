"""Contrats métier et parcours réels. Lancer :
python -m unittest discover -s tests -p test_v4_atlas.py -v
"""
import csv
import importlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "solutions" / "atlas"
sys.path.insert(0, str(REFERENCE))
calcul = importlib.import_module("calcul")
lecture = importlib.import_module("lecture")
nettoyage = importlib.import_module("nettoyage")
modele = importlib.import_module("modele")
chargement = importlib.import_module("chargement")
incremental = importlib.import_module("incremental")
rapport = importlib.import_module("rapport")
DATA = ROOT / "projet" / "data"


class AtlasContrats(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="atlas-tests-")
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        self.base = self.dossier / "atlas.sqlite"
        self.produits, self.boutiques = lecture.catalogues(DATA)
        self.brutes = lecture.lire_csv(DATA / "ventes_initiales.csv")
        self.ventes, self.rejets, self.doublons = nettoyage.nettoyer(self.brutes, self.produits, self.boutiques)

    def charger_initial(self):
        modele.creer_modele(self.base)
        return chargement.charger(self.ventes, self.produits, self.boutiques, self.base)

    def test_calcul_entier_et_variation(self):
        self.assertEqual(calcul.calculer_total([]), 0)
        self.assertEqual(calcul.calculer_total([{"quantity": 2, "unit_price_millimes": 4500},
                                               {"quantity": 3, "unit_price_millimes": 1500}]), 13500)
        self.assertEqual(calcul.calculer_total([{"quantity": 3, "unit_price_millimes": 4500},
                                               {"quantity": 3, "unit_price_millimes": 1500}]), 18000)
        with self.assertRaises(ValueError):
            calcul.calculer_total([{"quantity": 1.5, "unit_price_millimes": 100}])

    def test_qualite_et_millimes_exacts(self):
        self.assertEqual((len(self.brutes), len(self.ventes), len(self.rejets), len(self.doublons)), (16, 12, 3, 1))
        self.assertEqual(sum(v["quantity"] for v in self.ventes), 32)
        self.assertEqual(calcul.calculer_total(self.ventes), 99000)
        self.assertEqual({v["sale_id"] for v in self.rejets}, {"I001", "I002", "I003"})
        self.assertTrue(all(v["motif"] for v in self.rejets))
        self.assertEqual(set(self.ventes[0]), set(nettoyage.CHAMPS_VENTES))
        self.assertTrue(all(type(v["quantity"]) is int and type(v["amount_millimes"]) is int for v in self.ventes))
        v = dict(self.brutes[0], sale_id=" petit ", shop_id=" nbe ", product_id=" p02 ", quantity="3", unit_price_tnd="0,125")
        retenues, rejets, _ = nettoyage.nettoyer([v], self.produits, self.boutiques)
        self.assertEqual(rejets, [])
        self.assertEqual((retenues[0]["sale_id"], retenues[0]["unit_price_millimes"], retenues[0]["amount_millimes"]), ("PETIT", 125, 375))

    def test_invalides_sans_arrondi_silencieux(self):
        exemples = [dict(self.brutes[0], **variation) for variation in (
            {"sale_id": ""}, {"quantity": "1.5"}, {"quantity": "-1"}, {"quantity": "0"},
            {"unit_price_tnd": "0"}, {"unit_price_tnd": "-0.001"}, {"unit_price_tnd": "1.0001"},
            {"unit_price_tnd": "NaN"}, {"unit_price_tnd": "Infinity"}, {"unit_price_tnd": "bonjour"},
            {"date": "2026-02-30"}, {"shop_id": "AUTRE"}, {"product_id": "P99"})]
        retenues, rejets, doublons = nettoyage.nettoyer(exemples, self.produits, self.boutiques)
        self.assertEqual((len(retenues), len(rejets), len(doublons)), (0, len(exemples), 0))

    def test_doublon_normalise_et_conflit_source(self):
        equivalent = dict(self.brutes[0], shop_id=" nbe ", unit_price_tnd="4,5", quantity="02")
        retenues, rejets, doublons = nettoyage.nettoyer([self.brutes[0], equivalent], self.produits, self.boutiques)
        self.assertEqual((len(retenues), len(rejets), len(doublons)), (1, 0, 1))
        with self.assertRaisesRegex(ValueError, "Conflit sale_id S001"):
            nettoyage.nettoyer([self.brutes[0], dict(self.brutes[0], quantity="3")], self.produits, self.boutiques)

    def test_chargement_rejeu_sans_effacement(self):
        self.assertEqual(self.charger_initial(), {"inserted": 12, "existing": 0})
        modele.creer_modele(self.base)
        self.assertEqual(chargement.charger(self.ventes, self.produits, self.boutiques, self.base), {"inserted": 0, "existing": 12})
        self.assertEqual(chargement.total_base(self.base), (12, 32, 99000))

    def test_contraintes_sql_et_cles_etrangeres(self):
        self.charger_initial()
        connexion = modele.connecter(self.base)
        self.addCleanup(connexion.close)
        self.assertEqual(connexion.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        ligne = connexion.execute("SELECT * FROM fact_sales LIMIT 1").fetchone()
        # ID, date, produit, boutique, quantité, prix, montant.
        variantes = [("MAUVAIS_FK", 99999999, *ligne[2:]),
                     ("ZERO", *ligne[1:4], 0, ligne[5], 0),
                     ("FRACTION", *ligne[1:4], 1.5, 100, 150),
                     ("PRIX", *ligne[1:5], 0, 0),
                     ("MONTANT", *ligne[1:6], 1)]
        for valeurs in variantes:
            with self.subTest(valeurs=valeurs), self.assertRaises(sqlite3.IntegrityError):
                with connexion:
                    connexion.execute("INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?)", valeurs)
        self.assertEqual(chargement.total_base(self.base), (12, 32, 99000))
        self.assertEqual(connexion.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_conflit_annule_tout_le_lot_y_compris_dimensions(self):
        self.charger_initial()
        nouvelle = dict(self.ventes[0], sale_id="S099", date="2026-12-31")
        conflit = dict(self.ventes[0], quantity=3, amount_millimes=13500)
        with self.assertRaisesRegex(ValueError, "transaction annulée"):
            chargement.charger([nouvelle, conflit], {**self.produits, "P99": "Test"}, self.boutiques, self.base)
        self.assertEqual(chargement.total_base(self.base), (12, 32, 99000))
        with sqlite3.connect(self.base) as connexion:
            self.assertEqual(connexion.execute("SELECT COUNT(*) FROM dim_date WHERE full_date='2026-12-31'").fetchone()[0], 0)
            self.assertEqual(connexion.execute("SELECT COUNT(*) FROM dim_product WHERE product_id='P99'").fetchone()[0], 0)

    def test_erreur_sql_annule_tout_le_lot(self):
        self.charger_initial()
        nouveau = dict(self.ventes[0], sale_id="NOUVEAU")
        invalide = dict(self.ventes[0], sale_id="INVALIDE", amount_millimes=42)
        with self.assertRaises(sqlite3.IntegrityError):
            chargement.charger([nouveau, invalide], self.produits, self.boutiques, self.base)
        self.assertEqual(chargement.total_base(self.base), (12, 32, 99000))

    def test_rapport_initial_et_final_sont_donnes_reelles(self):
        self.charger_initial()
        initial = rapport.generer(self.base, self.dossier / "initial.html")
        self.assertEqual((initial["facts"], initial["quantity"], initial["amount_millimes"]), (12, 32, 99000))
        self.assertEqual((initial["period_start"], initial["period_end"]), ("2026-01-05", "2026-01-07"))
        self.assertEqual({r["id"]: r["amount_millimes"] for r in initial["shops"]}, {"NBE": 43500, "TUN": 55500})
        self.assertEqual({r["name"]: r["amount_millimes"] for r in initial["products"]},
                         {"Carnet": 22500, "Stylo": 18000, "Classeur": 36000, "Surligneur": 22500})
        resultat = incremental.ajouter(DATA / "ventes_ajout.csv", self.base, DATA)
        self.assertEqual(resultat, {"raw": 3, "accepted": 3, "rejected": 0, "duplicates": 0, "inserted": 2, "existing": 1})
        self.assertEqual(incremental.ajouter(DATA / "ventes_ajout.csv", self.base, DATA)["inserted"], 0)
        final = rapport.generer(self.base, self.dossier / "final.html")
        self.assertEqual((final["facts"], final["quantity"], final["amount_millimes"]), (14, 35, 115500))
        self.assertEqual(final["period_end"], "2026-01-08")
        self.assertIn("115.500", (self.dossier / "final.html").read_text())
        self.assertIn("SUM(f.amount_millimes)", (self.dossier / "final.html").read_text())

    def test_rapport_autre_periode_et_echappement_html(self):
        modele.creer_modele(self.base)
        vente = dict(self.ventes[0], sale_id="AUTRE", date="2028-09-10", quantity=7, amount_millimes=31500)
        chargement.charger([vente], {"P01": "Carnet <spécial>"}, {"NBE": "Nabeul & nord"}, self.base)
        fichier = self.dossier / "autre.html"
        bilan = rapport.generer(self.base, fichier)
        self.assertEqual((bilan["facts"], bilan["quantity"], bilan["amount_millimes"]), (1, 7, 31500))
        self.assertEqual((bilan["period_start"], bilan["period_end"]), ("2028-09-10", "2028-09-10"))
        self.assertIn("Carnet &lt;spécial&gt;", fichier.read_text())
        self.assertIn("Nabeul &amp; nord", fichier.read_text())
        self.assertNotIn("2026-01-05", fichier.read_text())


class ParcoursExecutable(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="atlas parcours espaces ")
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)

    def commande(self, script, *args, succes=0):
        resultat = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=self.dossier,
                                  text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(resultat.returncode, succes, resultat.stdout + resultat.stderr)
        return resultat.stdout

    def test_reference_fraiche_autre_cwd_imports_et_rejeu(self):
        projet = self.dossier / "copie autonome avec espaces"
        projet.mkdir()
        for source in REFERENCE.glob("*.py"):
            shutil.copy2(source, projet / source.name)
        shutil.copytree(DATA, projet / "data")
        # Importer tous les modules ne doit créer ni base ni rapport.
        code = "import sys; sys.path.insert(0, sys.argv[1]); import calcul, lecture, nettoyage, modele, chargement, incremental, rapport, executer, verifier"
        resultat = subprocess.run([sys.executable, "-c", code, str(projet)], cwd=self.dossier, capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        self.assertFalse((projet / "outputs").exists())
        premiere = self.commande(projet / "executer.py")
        self.assertIn("12 nouvelles, 0 existantes", premiere)
        self.assertIn("2 nouvelles, 1 existantes", premiere)
        self.assertIn("115.500 TND", premiere)
        base = projet / "outputs" / "atlas.sqlite"
        avant = base.read_bytes()
        controles = self.commande(projet / "verifier.py", "tout")
        self.assertEqual(controles.count("[OK "), 7)
        self.assertEqual(base.read_bytes(), avant, "Le vérificateur a modifié la base étudiante.")
        seconde = self.commande(projet / "executer.py")
        self.assertIn("0 nouvelles, 12 existantes", seconde)
        self.assertIn("0 nouvelles, 3 existantes", seconde)
        with sqlite3.connect(base) as connexion:
            self.assertEqual(connexion.execute("SELECT COUNT(*), SUM(quantity), SUM(amount_millimes) FROM fact_sales").fetchone(), (14, 35, 115500))

    def test_starter_incomplet_et_controles_sans_solution(self):
        projet = self.dossier / "starter seul"
        shutil.copytree(ROOT / "projet", projet, ignore=shutil.ignore_patterns("__pycache__", "outputs"))
        texte = self.commande(projet / "verifier.py", "01", succes=1)
        self.assertIn("À CONSTRUIRE 01", texte)
        self.assertFalse((projet / "outputs").exists())
        for nom in ("calcul", "lecture", "nettoyage", "modele", "chargement", "incremental", "rapport"):
            self.assertIn("raise NotImplementedError", (projet / f"{nom}.py").read_text())
        self.assertNotIn("solutions", (projet / "verifier.py").read_text())

    def test_jalons_incrementaux_reels_et_refus_ecrasement(self):
        for numero in ("00", "03", "05", "06", "07"):
            with self.subTest(jalon=numero):
                destination = self.dossier / f"reprise {numero}"
                self.commande(ROOT / "outils" / "jalon.py", numero, "--destination", destination)
                if numero == "00":
                    self.commande(destination / "verifier.py", "01", succes=1)
                    continue
                self.commande(destination / "verifier.py", numero)
                if numero == "03":
                    self.assertFalse((destination / "outputs" / "atlas.sqlite").exists())
                    self.commande(destination / "verifier.py", "04", succes=1)
                if numero == "05":
                    self.assertEqual(chargement.total_base(destination / "outputs" / "atlas.sqlite"), (12, 32, 99000))
                    # Un rapport peut légitimement décrire l'état initial avant l'ajout.
                    shutil.copy2(REFERENCE / "rapport.py", destination / "rapport.py")
                    self.commande(destination / "rapport.py")
                    self.assertIn("99.000 TND", self.commande(destination / "verifier.py", "07"))
                    self.assertEqual(chargement.total_base(destination / "outputs" / "atlas.sqlite"), (12, 32, 99000))
                if numero == "07":
                    self.commande(destination / "verifier.py", "tout")
                temoin = destination / "ne_pas_effacer.txt"
                temoin.write_text("travail étudiant")
                self.commande(ROOT / "outils" / "jalon.py", numero, "--destination", destination, succes=1)
                self.assertEqual(temoin.read_text(), "travail étudiant")


if __name__ == "__main__":
    unittest.main()
