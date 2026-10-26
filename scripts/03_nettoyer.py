"""Mission 03. Contrôler avant de calculer, garder la raison des rejets."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import DATA, OUTPUTS, read_csv, read_catalogs, save_cleaning

# Pour le parcours de référence, conserver ce fichier intact.
SOURCE = "ventes_initiales.csv"

# Un petit exemple visible : espaces retirés, code en majuscules.
code_boutique = " nbe "
print("Normalisation :", repr(code_boutique), "->", code_boutique.strip().upper())

produits, boutiques = read_catalogs()
lignes = read_csv(DATA / SOURCE)
# Le contrôleur applique aussi les règles de date, quantité et catalogue.
valides, rejets, doublons = save_cleaning(
    lignes, produits, boutiques, OUTPUTS / "03"
)
print("Sources :", len(lignes))
print("Retenues :", len(valides))
print("Doublons :", len(doublons))
print("Rejets :", len(rejets))
for rejet in rejets:
    print(rejet["sale_id"], ":", rejet["reason"])
print("Contrôles et fichiers dans outputs/03/")
