import sqlite3

base = sqlite3.connect(":memory:")
base.execute("PRAGMA foreign_keys = ON")
base.execute("CREATE TABLE produit (id TEXT PRIMARY KEY)")
base.execute("INSERT INTO produit VALUES (?)", ("P01",))
base.execute("""CREATE TABLE vente (
    produit_id TEXT REFERENCES produit(id), quantite INTEGER
)""")
base.execute("INSERT INTO vente VALUES (?, ?)", ("P01", 2))
print(base.execute("SELECT COUNT(*) FROM vente").fetchone()[0])
base.close()
