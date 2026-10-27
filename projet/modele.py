"""Schéma fourni : clés, contraintes et connexions SQLite."""
from pathlib import Path
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS dim_product (
 product_key INTEGER PRIMARY KEY, product_id TEXT NOT NULL UNIQUE, product_name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dim_shop (
 shop_key INTEGER PRIMARY KEY, shop_id TEXT NOT NULL, shop_name TEXT NOT NULL,
 commercial_zone TEXT NOT NULL, valid_from TEXT NOT NULL, valid_to TEXT,
 UNIQUE(shop_id, valid_from), CHECK(valid_to IS NULL OR valid_to > valid_from));
CREATE UNIQUE INDEX IF NOT EXISTS one_current_shop ON dim_shop(shop_id) WHERE valid_to IS NULL;
CREATE TABLE IF NOT EXISTS dim_date (
 date_key INTEGER PRIMARY KEY, full_date TEXT NOT NULL UNIQUE,
 year INTEGER NOT NULL, month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
 day INTEGER NOT NULL CHECK(day BETWEEN 1 AND 31));
CREATE TABLE IF NOT EXISTS fact_sales (
 sale_id TEXT PRIMARY KEY NOT NULL,
 date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
 product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
 shop_key INTEGER NOT NULL REFERENCES dim_shop(shop_key),
 quantity INTEGER NOT NULL CHECK(typeof(quantity)='integer' AND quantity > 0),
 unit_price_millimes INTEGER NOT NULL CHECK(typeof(unit_price_millimes)='integer' AND unit_price_millimes > 0),
 amount_millimes INTEGER NOT NULL CHECK(typeof(amount_millimes)='integer' AND amount_millimes = quantity*unit_price_millimes));
"""


def connecter(chemin, preparer=False):
    chemin = Path(chemin)
    if preparer:
        chemin.parent.mkdir(parents=True, exist_ok=True)
    elif not chemin.is_file():
        raise FileNotFoundError(f"Entrepôt absent : {chemin}. Exécuter initial.")
    conn = sqlite3.connect(chemin, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")  # Avant BEGIN, pour chaque connexion.
    if preparer:
        conn.executescript(SCHEMA)  # Préparation hors transaction métier.
    return conn
