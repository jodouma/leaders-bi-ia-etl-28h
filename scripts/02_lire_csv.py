"""Mission 02. Une ligne du CSV décrit une vente élémentaire."""
from pathlib import Path
import sys
import csv
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import DATA, OUTPUTS, FIELDS, write_csv

# À VOUS : remplacer 3 par 5, prédire le nombre de lignes affichées.
LIMITE_APERCU = 3

# Ouvrir un fichier texte ; DictReader nomme les colonnes.
with (DATA / "ventes_initiales.csv").open(
    encoding="utf-8-sig", newline=""
) as fichier:
    lignes = list(csv.DictReader(fichier, delimiter=","))

print("Lignes sources :", len(lignes))
print("Colonnes :", ", ".join(FIELDS))
for vente in lignes[:LIMITE_APERCU]:
    print(vente["sale_id"], vente["quantity"], vente["unit_price_tnd"])
write_csv(OUTPUTS / "02" / "apercu.csv", FIELDS, lignes[:LIMITE_APERCU])
print("Aperçu enregistré dans outputs/02/apercu.csv")
