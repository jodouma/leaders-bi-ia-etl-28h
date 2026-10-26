"""Mission 05. SQL interroge une table ; Python apporte les lignes."""
from pathlib import Path
import sys
import sqlite3
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import OUTPUTS, read_transformed, write_csv, money

# À VOUS : remplacer NBE par TUN. Quel total attendez-vous ?
BOUTIQUE = "NBE"

ventes = read_transformed(OUTPUTS / "04" / "ventes_transformees.csv")
# :memory: signifie une base temporaire, recréée à chaque exécution.
base = sqlite3.connect(":memory:")
base.execute("CREATE TABLE ventes (sale_id TEXT, shop_id TEXT, "
             "quantity INTEGER, amount_millimes INTEGER)")
base.executemany("INSERT INTO ventes VALUES (?, ?, ?, ?)", [
    (v["sale_id"], v["shop_id"], v["quantity"], v["amount_millimes"])
    for v in ventes
])

# Le ? est une valeur transmise à part, pas du texte collé au SQL.
requete = """SELECT sale_id, quantity, amount_millimes
FROM ventes WHERE shop_id = ? ORDER BY sale_id"""
resultats = base.execute(requete, (BOUTIQUE,)).fetchall()
for identifiant, quantite, montant in resultats:
    print(identifiant, quantite, money(montant), "TND")
print("Boutique :", BOUTIQUE)
print("Ventes :", len(resultats))
print("Montant :", money(sum(ligne[2] for ligne in resultats)), "TND")

print("Regroupement de toutes les boutiques :")
for boutique, montant in base.execute(
    "SELECT shop_id, SUM(amount_millimes) FROM ventes "
    "GROUP BY shop_id ORDER BY shop_id"
):
    print(boutique, money(montant), "TND")
write_csv(OUTPUTS / "05" / "requete.csv",
          ["sale_id", "quantity", "amount_millimes"], [
              dict(zip(["sale_id", "quantity", "amount_millimes"], ligne))
              for ligne in resultats
          ])
base.close()
