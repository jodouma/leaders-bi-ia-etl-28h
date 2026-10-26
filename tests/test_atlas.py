"""Contrôles reproductibles : données, ETL, transaction et route étudiante.
Lancer depuis la racine : python -m unittest discover -s tests -v
Aucun paquet tiers. Les tests travaillent dans des dossiers temporaires.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import csv
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import atelier


class DataAndTransformTests(unittest.TestCase):
    def setUp(self):
        self.products, self.shops = atelier.read_catalogs()
        self.raw = atelier.read_csv(atelier.DATA / "ventes_initiales.csv")
        self.clean, self.rejects, self.duplicates = atelier.clean_sales(
            self.raw, self.products, self.shops)
        self.rows = atelier.transform_sales(self.clean)

    def test_every_source_line_is_accounted_for(self):
        self.assertEqual(len(self.raw), 16)
        self.assertEqual(len(self.clean), 12)
        self.assertEqual(len(self.rejects), 3)
        self.assertEqual(len(self.duplicates), 1)
        self.assertEqual({r["sale_id"] for r in self.rejects},
                         {"I001", "I002", "I003"})
        self.assertEqual(self.duplicates[0]["sale_id"], "S003")
        self.assertTrue(all(r["reason"] for r in self.rejects))

    def test_normalization_changes_not_the_sale_identity(self):
        self.assertEqual(self.raw[4]["shop_id"], " nbe ")
        self.assertEqual(self.clean[4]["shop_id"], "NBE")
        self.assertEqual(self.clean[6]["product_id"], "P02")
        self.assertEqual(self.clean[4]["sale_id"], "S005")

    def test_independent_expected_amounts_and_quantities(self):
        self.assertEqual(sum(r["quantity"] for r in self.rows), 32)
        self.assertEqual(sum(r["amount_millimes"] for r in self.rows), 99000)
        by_shop, by_product = {}, {}
        for row in self.rows:
            shop, product = row["shop_id"], row["product_id"]
            by_shop[shop] = by_shop.get(shop, 0) + row["amount_millimes"]
            by_product[product] = by_product.get(product, 0) + row["amount_millimes"]
        self.assertEqual(by_shop, {"NBE": 43500, "TUN": 55500})
        self.assertEqual(by_product, {"P01": 22500, "P02": 18000,
                                     "P03": 36000, "P04": 22500})
        self.assertEqual(self.rows[0]["amount_millimes"], 9000)

    def test_price_is_exact_and_bad_prices_are_rejected(self):
        self.assertEqual(atelier.price_to_millimes("4.500"), 4500)
        self.assertEqual(atelier.price_to_millimes("0.001"), 1)
        self.assertEqual(atelier.money(115500), "115.500")
        for bad in ("NaN", "Infinity", "-1", "0", "4.0001", "abc"):
            with self.subTest(price=bad), self.assertRaises(ValueError):
                atelier.price_to_millimes(bad)

    def test_conflicting_duplicate_id_blocks_instead_of_choosing(self):
        other = dict(self.raw[0], quantity="3")
        with self.assertRaisesRegex(ValueError, "Conflit"):
            atelier.clean_sales(self.raw + [other], self.products, self.shops)

    def test_bad_quantities_dates_catalogues_and_blanks_are_isolated(self):
        for field, value in [("quantity", "2.5"), ("quantity", "-2"),
                             ("date", "20260105"), ("shop_id", "???"),
                             ("product_id", "P99"), ("sale_id", "")]:
            with self.subTest(field=field, value=value):
                row = dict(self.raw[0], **{field: value})
                good, rejected, duplicated = atelier.clean_sales(
                    [row], self.products, self.shops)
                self.assertEqual((len(good), len(rejected), len(duplicated)),
                                 (0, 1, 0))

    def test_missing_file_and_wrong_columns_explain_the_problem(self):
        with self.assertRaisesRegex(FileNotFoundError, "introuvable"):
            atelier.read_csv(atelier.DATA / "not_here.csv")
        with self.assertRaisesRegex(ValueError, "Colonnes"):
            atelier.clean_sales([{"sale_id": "S001"}], self.products, self.shops)

    def test_threshold_variations_have_real_different_results(self):
        self.assertEqual([r["sale_id"] for r in self.rows
                          if r["amount_millimes"] >= 9000],
                         ["S001", "S004", "S006", "S011", "S012"])
        self.assertEqual([r["sale_id"] for r in self.rows
                          if r["amount_millimes"] >= 10000],
                         ["S004", "S006", "S012"])


class WarehouseTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.db = self.folder / "atlas.sqlite"
        self.products, self.shops = atelier.read_catalogs()
        clean, _, _ = atelier.clean_sales(
            atelier.read_csv(atelier.DATA / "ventes_initiales.csv"),
            self.products, self.shops)
        self.rows = atelier.transform_sales(clean)
        added, _, _ = atelier.clean_sales(
            atelier.read_csv(atelier.DATA / "ventes_ajout.csv"),
            self.products, self.shops)
        self.added = atelier.transform_sales(added)

    def tearDown(self):
        self.temp.cleanup()

    def load(self, rows):
        return atelier.load_sales(self.db, rows, self.products, self.shops)

    def test_initial_and_repeated_load_are_idempotent(self):
        self.assertEqual(self.load(self.rows), {"inserted": 12, "existing": 0})
        self.assertEqual(self.load(self.rows), {"inserted": 0, "existing": 12})
        self.assertEqual(atelier.database_totals(self.db),
                         {"sales": 12, "quantity": 32, "amount_millimes": 99000})

    def test_increment_and_replay_never_double_count(self):
        self.load(self.rows)
        self.assertEqual(self.load(self.added), {"inserted": 2, "existing": 1})
        self.assertEqual(self.load(self.added), {"inserted": 0, "existing": 3})
        self.assertEqual(atelier.database_totals(self.db),
                         {"sales": 14, "quantity": 35, "amount_millimes": 115500})
        self.load(self.rows)
        self.assertEqual(atelier.database_totals(self.db)["sales"], 14)

    def test_conflict_rolls_back_whole_batch_including_new_date(self):
        self.load(self.rows)
        new = dict(self.added[0], sale_id="S100", date="2026-02-01")
        conflict = dict(self.rows[0], quantity=3, amount_millimes=13500)
        with self.assertRaisesRegex(ValueError, "Conflit"):
            self.load([new, conflict])
        self.assertEqual(atelier.database_totals(self.db)["sales"], 12)
        conn = atelier.connect(self.db)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0], 3)
        finally:
            conn.close()

    def test_foreign_keys_and_measure_constraint_are_enforced(self):
        self.load(self.rows)
        conn = atelier.connect(self.db)
        try:
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?)",
                             ("X", 19990101, 999, 999, 1, 1000, 1000))
            conn.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE fact_sales SET amount_millimes=1 WHERE sale_id='S001'")
            conn.rollback()
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            conn.close()

    def test_star_schema_has_expected_grain_and_dimension_sizes(self):
        self.load(self.rows)
        conn = atelier.connect(self.db)
        try:
            for table, expected in [("dim_product", 4), ("dim_shop", 2),
                                    ("dim_date", 3), ("fact_sales", 12)]:
                self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],
                                 expected)
            groups = dict((name, amount) for name, _, amount in atelier.group_sales(conn, "product"))
            self.assertEqual(groups["Classeur"], 36000)
        finally:
            conn.close()

    def test_report_reads_real_database_escapes_title_and_exports(self):
        self.load(self.rows)
        self.load(self.added)
        target = self.folder / "rapport.html"
        summary = atelier.build_report(self.db, target, "Atlas <test>")
        self.assertEqual(summary["amount_millimes"], 115500)
        html = target.read_text(encoding="utf-8")
        self.assertIn("115.500 TND", html)
        self.assertIn("Atlas &lt;test&gt;", html)
        self.assertNotIn("__SALES__", html)
        self.assertNotIn("<script", html)
        self.assertIn("UTC", html)
        rows = atelier.read_csv(self.folder / "ventes_par_product.csv")
        self.assertEqual(rows[0], {"label": "Classeur", "quantity": "8",
                                  "amount_tnd": "48.000"})
        self.assertNotIn("https://", html)

    def test_absent_database_does_not_create_empty_fake_report(self):
        with self.assertRaisesRegex(FileNotFoundError, "Base absente"):
            atelier.build_report(self.db, self.folder / "rapport.html")
        self.assertFalse(self.db.exists())


class StudentRouteTests(unittest.TestCase):
    def test_actual_scripts_run_from_unrelated_working_directory(self):
        with TemporaryDirectory() as temp:
            sandbox = Path(temp)
            root = sandbox / "cours avec espaces"
            root.mkdir()
            shutil.copyfile(atelier.ROOT / "atelier.py", root / "atelier.py")
            shutil.copytree(atelier.ROOT / "data", root / "data")
            shutil.copytree(atelier.ROOT / "scripts", root / "scripts")
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            logs = []
            for script in sorted((root / "scripts").glob("*.py")):
                run = subprocess.run([sys.executable, str(script)], cwd=sandbox,
                                     env=env, encoding="utf-8", capture_output=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                logs.append((script.name, run.stdout))
            self.assertEqual(len(logs), 10)
            self.assertIn("99.000 TND", logs[6][1])
            self.assertIn("115.500 TND", logs[8][1])
            self.assertEqual(atelier.database_totals(root / "outputs" / "atlas.sqlite"),
                             {"sales": 14, "quantity": 35, "amount_millimes": 115500})
            # Rejouer le lot avec les vrais scripts, pas une imitation du pipeline.
            repeat = subprocess.run([sys.executable, str(root / "scripts" / "08_incremental.py")],
                                    cwd=sandbox, env=env, encoding="utf-8", capture_output=True)
            self.assertEqual(repeat.returncode, 0, repeat.stderr)
            self.assertIn("Nouvelles ventes : 0", repeat.stdout)
            self.assertIn("Déjà présentes : 3", repeat.stdout)
            # Réparer la copie du défi, modifier le paramètre publié et exécuter.
            challenge = root / "outputs" / "10" / "ventes_a_reparer.csv"
            rows = atelier.read_csv(challenge)
            rows[-1]["quantity"] = "2"
            atelier.write_csv(challenge, atelier.FIELDS, rows)
            script = root / "scripts" / "10_defi.py"
            content = script.read_text(encoding="utf-8").replace(
                'SOURCE_AJOUT = DATA / "ventes_ajout.csv"',
                'SOURCE_AJOUT = DOSSIER / "ventes_a_reparer.csv"')
            script.write_text(content, encoding="utf-8")
            for _ in range(2):
                run = subprocess.run([sys.executable, str(script)], cwd=sandbox,
                                     env=env, encoding="utf-8", capture_output=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertIn("15 ventes | 37 articles | 118.500 TND", run.stdout)
            self.assertEqual(atelier.database_totals(root / "outputs" / "atlas.sqlite")["sales"], 14)

    def test_script_04_requires_legitimate_upstream_file(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copyfile(atelier.ROOT / "atelier.py", root / "atelier.py")
            shutil.copytree(atelier.ROOT / "scripts", root / "scripts")
            run = subprocess.run([sys.executable, str(root / "scripts" / "04_transformer.py")],
                                 encoding="utf-8", capture_output=True,
                                 env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Fichier introuvable", run.stderr)
            self.assertFalse((root / "outputs").exists())


if __name__ == "__main__":
    unittest.main()
