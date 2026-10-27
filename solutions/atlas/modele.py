"""04 — Créer un schéma en étoile sans effacer les données."""
import sqlite3
from pathlib import Path
from lecture import OUTPUTS


def connecter(chemin_base):
    """SQLite active les clés étrangères pour chaque nouvelle connexion."""
    connexion = sqlite3.connect(chemin_base)
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def creer_modele(chemin_base):
    """Créer les tables absentes. Un second appel conserve les faits présents."""
    chemin_base = Path(chemin_base)
    chemin_base.parent.mkdir(parents=True, exist_ok=True)
    connexion = connecter(chemin_base)
    try:
        connexion.executescript("""
        CREATE TABLE IF NOT EXISTS dim_product (
            product_key INTEGER PRIMARY KEY,
            product_id TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dim_shop (
            shop_key INTEGER PRIMARY KEY,
            shop_id TEXT NOT NULL UNIQUE,
            shop_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT NOT NULL UNIQUE,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
            day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31)
        );
        CREATE TABLE IF NOT EXISTS fact_sales (
            sale_id TEXT PRIMARY KEY NOT NULL,
            date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
            product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
            shop_key INTEGER NOT NULL REFERENCES dim_shop(shop_key),
            quantity INTEGER NOT NULL CHECK (typeof(quantity) = 'integer' AND quantity > 0),
            unit_price_millimes INTEGER NOT NULL
                CHECK (typeof(unit_price_millimes) = 'integer' AND unit_price_millimes > 0),
            amount_millimes INTEGER NOT NULL
                CHECK (typeof(amount_millimes) = 'integer'
                       AND amount_millimes = quantity * unit_price_millimes)
        );
        """)
        connexion.commit()
    finally:
        connexion.close()


def main():
    creer_modele(OUTPUTS / "atlas.sqlite")
    print("Modèle prêt : 3 dimensions, 1 table de faits. Données conservées.")


if __name__ == "__main__":
    main()
