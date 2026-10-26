import sqlite3

base = sqlite3.connect(":memory:")
base.execute("CREATE TABLE ventes (boutique TEXT, montant INT)")
base.execute("INSERT INTO ventes VALUES (?, ?)", ("NBE", 9000))
base.execute("INSERT INTO ventes VALUES (?, ?)", ("TUN", 6000))
question = "SELECT SUM(montant) FROM ventes WHERE boutique = ?"
resultat = base.execute(question, ("NBE",)).fetchone()[0]
print(f"{resultat / 1000:.3f} TND")
base.close()
