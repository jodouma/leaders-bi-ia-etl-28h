"""Mission 04. Calculer sans changer ce que représente une ligne."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import (OUTPUTS, TRANSFORMED_FIELDS, read_csv, write_csv,
                     price_to_millimes, money)

# À VOUS : essayer 10000 et comparer les ventes >= au seuil.
SEUIL_MILLIMES = 9000

propres = read_csv(OUTPUTS / "03" / "ventes_nettoyees.csv")
transformees = []
for vente in propres:
    quantite = int(vente["quantity"])
    prix = price_to_millimes(vente["unit_price_tnd"])
    montant = quantite * prix
    transformees.append({
        "sale_id": vente["sale_id"], "date": vente["date"],
        "shop_id": vente["shop_id"], "product_id": vente["product_id"],
        "quantity": quantite, "unit_price_millimes": prix,
        "amount_millimes": montant,
    })

write_csv(OUTPUTS / "04" / "ventes_transformees.csv",
          TRANSFORMED_FIELDS, transformees)
total = sum(vente["amount_millimes"] for vente in transformees)
print("Total des ventes :", money(total), "TND")
selection = [vente for vente in transformees
             if vente["amount_millimes"] >= SEUIL_MILLIMES]
print("Ventes au-dessus ou égales au seuil :", len(selection))
print("Identifiants :", ", ".join(vente["sale_id"] for vente in selection))
write_csv(OUTPUTS / "04" / "selection.csv", TRANSFORMED_FIELDS, selection)
