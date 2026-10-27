from contextlib import closing
import sqlite3
from pathlib import Path
racine = Path(__file__).resolve().parents[2]
base = racine / "projet" / "outputs" / "atlas.sqlite"
uri = base.as_uri() + "?mode=ro"
with closing(sqlite3.connect(uri, uri=True)) as connexion:
    resultat = connexion.execute(
        "SELECT COUNT(*), SUM(quantity), "
        "SUM(amount_millimes) FROM fact_sales"
    ).fetchone()
print(resultat)
