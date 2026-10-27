"""Contrats observables, sur des copies isolées du scaffold distribué."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def outil(nom, chemin):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Atlas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = TemporaryDirectory(prefix="atlas-tests-reference-")
        cls.atelier = outil("jalon_tests", ROOT / "outils/jalon.py").creer_reprise(7, Path(cls.work.name) / "atelier")
        sys.path.insert(0, str(cls.atelier))
        global engine, lecture, nettoyage, chargement, incremental, modele
        import engine, lecture, nettoyage, chargement, incremental, modele

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(cls.atelier))
        cls.work.cleanup()

    def setUp(self):
        self.temp = TemporaryDirectory(prefix="atlas-test-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.data = self.home / "data"
        shutil.copytree(self.atelier / "data", self.data)
        self.outputs = self.home / "outputs"
        self.base = self.outputs / "atlas.sqlite"

    def init(self):
        return chargement.initial(self.data, self.outputs)

    def final(self):
        self.init()
        return chargement.increment(self.data, self.outputs)

    def snapshot(self):
        conn = modele.connecter(self.base)
        try:
            return {t: [tuple(r) for r in conn.execute(f"SELECT * FROM {t} ORDER BY 1")] for t in engine.TABLE_COLUMNS}
        finally:
            conn.close()

    def sale(self, **changes):
        row = dict(sale_id="S100", date="2026-01-07", shop_id="NBE", product_id="P01", quantity="1", unit_price_tnd="4.500")
        row.update(changes)
        return row

    def load(self, rows, changes=()):
        return engine.charger(rows, changes, self.base, self.data, incremental.trouver_shop_key, strict=True)

    def test_csv_quality_money_and_normalization(self):
        self.assertEqual(nettoyage.normaliser_vente(self.sale(shop_id=" nbe ", product_id=" p01 "))["shop_id"], "NBE")
        bilan = self.init()
        self.assertEqual(tuple(bilan[k] for k in ("raw", "accepted", "duplicate", "rejected")), (16,12,1,3))
        r = engine.rapport(self.base)
        self.assertEqual((r["facts"], r["quantity"], r["amount_millimes"]), (12,32,99000))
        self.assertEqual((r["products"],r["shop_versions"],r["dates"]), (4,2,3))

    def test_money_rejects_rounding_nonfinite_and_nonpositive(self):
        for value in ("0", "-1", "NaN", "Infinity", "0.0001", "1.0000000000000000000000000001", "bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nettoyage.millimes(value)
        self.assertEqual(nettoyage.millimes(" 4.500 "), 4500)

    def test_quantity_and_dates(self):
        for value in ("0", "-1", "2.5", "NaN", "2.0", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nettoyage.entier_positif(value)
        for value in ("2026-02-30", "20260107", "2026-1-7"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nettoyage.date_iso(value)

    def test_duplicate_within_batch_conflict_is_fatal(self):
        self.init()
        avant = self.snapshot()
        with self.assertRaises(ValueError):
            self.load([self.sale(), self.sale(quantity="2")])
        self.assertEqual(self.snapshot(), avant)

    def test_sql_source_real_parameterized_and_readonly(self):
        source = self.data / "source_operationnelle.sqlite"
        ventes, changements, preuve = lecture.lire_increment_sql(source)
        self.assertEqual((len(ventes),len(changements)), (3,1))
        self.assertEqual(preuve["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(preuve["path"], str(source.resolve()))
        self.assertEqual(preuve["queries"][0]["params"], ["2026-01-08"])
        self.assertIn("batch_id = ?", preuve["queries"][0]["sql"])
        conn = lecture.connexion_source(source)
        try:
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM source_sales")
        finally:
            conn.close()
        conn = sqlite3.connect(source)
        try:
            conn.execute("UPDATE source_sales SET quantity=9 WHERE sale_id='S013'")
            conn.commit()
        finally:
            conn.close()
        nouveau, _, _ = lecture.lire_increment_sql(source)
        self.assertEqual(next(r for r in nouveau if r["sale_id"] == "S013")["quantity"], 9)
        self.assertEqual(lecture.lire_increment_sql(source, "x' OR 1=1 --")[:2], ([], []))

    def test_sql_missing_does_not_create_database(self):
        chemin = self.data / "missing.sqlite"
        with self.assertRaises(FileNotFoundError):
            lecture.lire_increment_sql(chemin)
        self.assertFalse(chemin.exists())

    def test_fk_and_integer_constraints_really_enforced(self):
        self.init()
        conn = modele.connecter(self.base)
        try:
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            for values in (("BAD",20260105,999,1,1,4500,4500),
                           ("BAD",20260105,1,1,1.5,4500,6750),
                           ("BAD",20260105,1,1,1,4500,999)):
                with self.subTest(values=values), self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?)", values)
        finally:
            conn.close()

    def test_increment_and_history_boundary_stable_old_facts(self):
        self.init()
        avant = self.snapshot()["fact_sales"]
        ajout = chargement.increment(self.data, self.outputs)
        self.assertEqual((ajout["inserted"],ajout["existing"],ajout["new_shop_versions"]), (2,1,1))
        apres = self.snapshot()
        self.assertEqual(apres["fact_sales"][:12], avant)
        self.assertEqual([r[1:] for r in apres["dim_shop"]], [
            ("NBE","Nabeul","Cap Bon","2026-01-05","2026-01-08"),
            ("TUN","Tunis","Grand Tunis","2026-01-05",None),
            ("NBE","Nabeul","Grand Tunis","2026-01-08",None)])
        r = engine.rapport(self.base)
        self.assertEqual((r["facts"],r["quantity"],r["amount_millimes"],r["dates"]), (14,35,115500,4))
        self.assertEqual(r["zone_amounts_millimes"], {"Cap Bon":43500,"Grand Tunis":72000})

    def test_full_replay_and_initial_replay_preserve_all_keys(self):
        self.final()
        avant = self.snapshot()
        rejoue = chargement.increment(self.data, self.outputs)
        self.assertEqual((rejoue["inserted"],rejoue["existing"],rejoue["new_shop_versions"]), (0,3,0))
        self.init()  # Le catalogue initial ne rouvre jamais l'ancienne version.
        self.assertEqual(self.snapshot(), avant)

    def test_late_sales_before_and_at_boundary(self):
        self.final()
        self.load([self.sale(sale_id="LATE07"), self.sale(sale_id="LATE08", date="2026-01-08")])
        conn = modele.connecter(self.base)
        try:
            zones = dict(conn.execute("SELECT sale_id,commercial_zone FROM fact_sales JOIN dim_shop USING(shop_key) WHERE sale_id LIKE 'LATE%'"))
            self.assertEqual(zones, {"LATE07":"Cap Bon","LATE08":"Grand Tunis"})
        finally:
            conn.close()
        avant = self.snapshot()
        with self.assertRaises(ValueError):
            self.load([self.sale(date="2026-01-04")])
        self.assertEqual(self.snapshot(), avant)

    def test_missing_overlapping_gap_and_multiple_match_fail(self):
        self.final()
        conn = modele.connecter(self.base)
        try:
            with self.assertRaises(ValueError):
                incremental.trouver_shop_key(conn,"NOPE","2026-01-07")
            conn.execute("UPDATE dim_shop SET valid_to='2026-01-09' WHERE shop_key=1")
            with self.assertRaises(ValueError):
                engine.verifier_histoire(conn)
            with self.assertRaises(ValueError):
                incremental.trouver_shop_key(conn,"NBE","2026-01-08")
            conn.execute("UPDATE dim_shop SET valid_to='2026-01-07' WHERE shop_key=1")
            with self.assertRaises(ValueError):
                engine.verifier_histoire(conn)
        finally:
            conn.close()

    def test_same_sale_conflict_rolls_back_dimensions_and_facts(self):
        self.init()
        avant = self.snapshot()
        changes = [{"shop_id":"NBE","effective_date":"2026-01-08","commercial_zone":"Grand Tunis"}]
        with self.assertRaises(ValueError):
            self.load([self.sale(sale_id="S100", date="2026-01-09"), self.sale(sale_id="S001",date="2026-01-05",quantity="99")], changes)
        self.assertEqual(self.snapshot(), avant)

    def test_change_conflict_same_date_and_same_zone_new_date(self):
        self.final()
        avant = self.snapshot()
        for debut, zone in (("2026-01-08","Autre"),("2026-01-09","Grand Tunis"),("2026-01-06","Autre")):
            with self.subTest(debut=debut,zone=zone), self.assertRaises(ValueError):
                self.load([], [{"shop_id":"NBE","effective_date":debut,"commercial_zone":zone}])
            self.assertEqual(self.snapshot(), avant)

    def test_retroactive_change_reclassifying_existing_facts_rejected(self):
        self.init()
        self.load([self.sale(date="2026-01-09")])
        avant = self.snapshot()
        with self.assertRaisesRegex(ValueError, "rétroactif"):
            self.load([], [{"shop_id":"NBE","effective_date":"2026-01-08","commercial_zone":"Grand Tunis"}])
        self.assertEqual(self.snapshot(), avant)

    def test_invalid_sql_batch_rejects_whole_change(self):
        self.init()
        avant = self.snapshot()
        conn = sqlite3.connect(self.data / "source_operationnelle.sqlite")
        try:
            conn.execute("UPDATE source_sales SET quantity=0 WHERE sale_id='S014'")
            conn.commit()
        finally:
            conn.close()
        with self.assertRaises(ValueError):
            chargement.increment(self.data,self.outputs)
        self.assertEqual(self.snapshot(), avant)

    def test_export_roundtrip_schema_keys_totals_and_no_fanout(self):
        self.final()
        dossier = engine.exporter(self.base,self.home / "powerbi", "test")
        manifest = json.loads((dossier / "manifest.json").read_text())
        self.assertEqual(set(p.name for p in dossier.iterdir()), {t+".csv" for t in engine.TABLE_COLUMNS} | {"manifest.json"})
        self.assertEqual(manifest["sums"], {"quantity":35,"amount_millimes":115500})
        tables = {}
        for table, colonnes in engine.TABLE_COLUMNS.items():
            chemin = dossier / (table+".csv")
            self.assertTrue(chemin.read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertEqual(hashlib.sha256(chemin.read_bytes()).hexdigest(), manifest["files"][chemin.name]["sha256"])
            with chemin.open(encoding="utf-8-sig", newline="") as flux:
                reader = csv.DictReader(flux)
                self.assertEqual(reader.fieldnames,colonnes)
                tables[table] = list(reader)
            self.assertEqual(len(tables[table]),manifest["files"][chemin.name]["rows"])
        shops = {r["shop_key"]:r for r in tables["dim_shop"]}
        self.assertEqual(len(shops), 3)
        self.assertEqual(sum(r["valid_to"] == "" for r in shops.values()),2)
        self.assertEqual(sum(int(r["amount_millimes"]) for r in tables["fact_sales"]),115500)
        zones = {}
        for r in tables["fact_sales"]:
            zone = shops[r["shop_key"]]["commercial_zone"]
            zones[zone] = zones.get(zone,0)+int(r["amount_millimes"])
        self.assertEqual(zones,{"Cap Bon":43500,"Grand Tunis":72000})
        for table,key in (("dim_product","product_key"),("dim_shop","shop_key"),("dim_date","date_key")):
            keys = {r[key] for r in tables[table]}
            self.assertTrue(all(r[key] in keys for r in tables["fact_sales"]))

    def test_failed_export_has_no_visible_manifest_or_partial_delivery(self):
        self.final()
        dossier = self.home / "powerbi"
        ancien = engine.exporter(self.base,dossier,"bon")
        avant = (ancien / "manifest.json").read_bytes()
        with patch.object(engine.csv,"writer",side_effect=OSError("disque indisponible")):
            with self.assertRaises(OSError):
                engine.exporter(self.base,dossier,"echec")
        self.assertEqual(sorted(p.name for p in dossier.iterdir()),["bon"])
        self.assertEqual((ancien / "manifest.json").read_bytes(),avant)
        with self.assertRaises(FileExistsError):
            engine.exporter(self.base,dossier,"bon")

    def test_missing_warehouse_export_leaves_no_partial_delivery(self):
        dossier = self.home / "powerbi"
        with self.assertRaises(FileNotFoundError):
            engine.exporter(self.base,dossier,"missing")
        self.assertEqual(list(dossier.iterdir()),[])

    def test_checkpoint01_is_ready_and_refuses_overwrite(self):
        jalon = outil("jalon_test_fresh",ROOT / "outils/jalon.py")
        dossier = jalon.creer_reprise(1,self.home / "starter")
        run = subprocess.run([sys.executable,"verifier.py","01"],cwd=dossier,text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn("OK 01",run.stdout)
        with self.assertRaises(FileExistsError):
            jalon.creer_reprise(7,dossier)
        self.assertIn("NotImplementedError",(dossier / "nettoyage.py").read_text())
        self.assertEqual(list((dossier / "outputs").iterdir()),[])

    def test_challenge_isolated_reproducible_and_bounded(self):
        preparer = outil("defi_test",ROOT / "defi/preparer.py")
        dossier = preparer.preparer(self.home / "defi")
        run = subprocess.run([sys.executable,"verifier.py","02"],cwd=dossier,text=True,capture_output=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn("32 unités",run.stderr)
        original = ROOT / "projet/data/ventes_initiales.csv"
        self.assertEqual((dossier / "data/ventes_initiales.csv").read_bytes(),original.read_bytes())
        shutil.copy2(ROOT / "solutions/atlas/nettoyage.py",dossier / "nettoyage.py")
        run = subprocess.run([sys.executable,"verifier.py","tout"],cwd=dossier,text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)


if __name__ == "__main__":
    unittest.main()
