"""Mission 08. Ajouter les nouvelles ventes, puis rejouer sans doublonner."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import (DATA, OUTPUTS, read_csv, read_catalogs, save_cleaning,
                     transform_sales, load_sales, database_totals,
                     write_json, utc_now, describe)

# À VOUS : exécuter, prévoir le résultat d'un deuxième passage, puis rejouer.
SOURCE = "ventes_ajout.csv"
BASE = OUTPUTS / "atlas.sqlite"
if not BASE.is_file():
    raise FileNotFoundError("Base absente : exécuter le script 07 d'abord.")

produits, boutiques = read_catalogs()
valides, rejets, doublons = save_cleaning(
    read_csv(DATA / SOURCE), produits, boutiques, OUTPUTS / "08"
)
# On parcourt tout le petit lot : l'identifiant décide s'il est nouveau.
# Ce n'est pas un filtre sur la date maximale : S012 peut réapparaître.
resultat = load_sales(BASE, transform_sales(valides), produits, boutiques)
synthese = database_totals(BASE)
print("Nouvelles ventes :", resultat["inserted"])
print("Déjà présentes :", resultat["existing"])
print(describe(synthese))
write_json(OUTPUTS / "08" / "chargement.json", {
    "timestamp_utc": utc_now(), **resultat, **synthese
})
print("Journal : outputs/08/chargement.json")
