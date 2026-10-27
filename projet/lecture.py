"""CSV et vraie source SQL. Seul lire_increment_sql est à compléter."""
import csv
import hashlib
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
SQL_VENTES = "SELECT sale_id, date, shop_id, product_id, quantity, unit_price_tnd FROM source_sales WHERE batch_id = ? ORDER BY sale_id"
SQL_CHANGEMENTS = "SELECT shop_id, effective_date, commercial_zone FROM source_shop_changes WHERE batch_id = ? ORDER BY effective_date, shop_id"


def lire_csv(chemin):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as fichier:
        return list(csv.DictReader(fichier))


def connexion_source(chemin):
    # mode=ro refuse de créer silencieusement une base vide.
    chemin = Path(chemin).resolve(strict=True)
    conn = sqlite3.connect(chemin.as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def preuve_source(chemin, batch_id):
    chemin = Path(chemin).resolve(strict=True)
    return {"path": str(chemin), "sha256": hashlib.sha256(chemin.read_bytes()).hexdigest(),
            "queries": [{"sql": SQL_VENTES, "params": [batch_id]},
                        {"sql": SQL_CHANGEMENTS, "params": [batch_id]}]}


def lire_increment_sql(chemin_source, batch_id="2026-01-08"):
    # TODO 03 : ouvrir connexion_source ; exécuter les deux SELECT avec (batch_id,).
    # Convertir chaque sqlite3.Row avec dict(row). Fermer dans finally.
    # Renvoyer (ventes, changements, preuve_source(chemin_source, batch_id)).
    raise NotImplementedError("Compléter lecture.lire_increment_sql")
