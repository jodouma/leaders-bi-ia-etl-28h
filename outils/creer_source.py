"""Reproduire la petite source SQL de l'atelier ; refuse une destination existante.

Usage depuis la racine : python3 outils/creer_source.py nouvelle_source.sqlite
La source distribuée est déjà prête : aucune exécution requise pour suivre le cours.
"""
import argparse
from pathlib import Path
import sqlite3

VENTES = [
    ("2026-01-08", "S013", "2026-01-08", "NBE", "P01", 1, "4.500"),
    ("2026-01-08", "S014", "2026-01-08", "TUN", "P03", 2, "6.000"),
    ("2026-01-08", "S012", "2026-01-07", "TUN", "P03", 3, "6.000"),
]
CHANGEMENTS = [("2026-01-08", "NBE", "2026-01-08", "Grand Tunis")]


def creer(chemin):
    chemin = Path(chemin)
    with chemin.open("xb"):
        pass
    conn = sqlite3.connect(chemin)
    try:
        conn.execute("CREATE TABLE source_sales (batch_id TEXT, sale_id TEXT, date TEXT, shop_id TEXT, product_id TEXT, quantity INTEGER, unit_price_tnd TEXT)")
        conn.execute("CREATE TABLE source_shop_changes (batch_id TEXT, shop_id TEXT, effective_date TEXT, commercial_zone TEXT)")
        conn.executemany("INSERT INTO source_sales VALUES (?,?,?,?,?,?,?)", VENTES)
        conn.executemany("INSERT INTO source_shop_changes VALUES (?,?,?,?)", CHANGEMENTS)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    creer(args.destination)
    print(f"Source SQL créée : {args.destination} (3 ventes, 1 changement)")
