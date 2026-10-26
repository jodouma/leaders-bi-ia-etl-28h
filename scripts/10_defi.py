"""Mission 10. Rejouer le pipeline et expliquer chaque contrôle."""
from pathlib import Path
import sys
import shutil
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import (DATA, OUTPUTS, read_csv, read_catalogs, save_cleaning,
                     transform_sales, load_sales, build_report, describe)

# Départ : garder ces valeurs. Le défi s'effectue dans une base séparée.
DOSSIER = OUTPUTS / "10"
SOURCE_AJOUT = DATA / "ventes_ajout.csv"
BASE = DOSSIER / "defi.sqlite"
DOSSIER.mkdir(parents=True, exist_ok=True)

# Une copie de travail est proposée, sans modifier le fichier source.
copie_defi = DOSSIER / "ventes_a_reparer.csv"
if not copie_defi.exists():
    shutil.copyfile(DATA / "ventes_defi.csv", copie_defi)

produits, boutiques = read_catalogs()
for nom, source in [("initial", DATA / "ventes_initiales.csv"),
                    ("ajout", SOURCE_AJOUT)]:
    valides, rejets, doublons = save_cleaning(
        read_csv(source), produits, boutiques, DOSSIER / nom
    )
    resultat = load_sales(BASE, transform_sales(valides), produits, boutiques)
    print(nom, ":", len(valides), "retenues,", len(rejets), "rejets,",
          len(doublons), "doublons du fichier")
    print("Chargement :", resultat)

synthese = build_report(BASE, DOSSIER / "rapport_defi.html")
print(describe(synthese))
print("Défi : ouvrir outputs/10/ventes_a_reparer.csv dans Thonny.")
print("Repérer S015 : une quantité nulle doit être rejetée.")
print("Dans la COPIE, mettre sa quantité à 2 et enregistrer.")
print('Puis choisir SOURCE_AJOUT = DOSSIER / "ventes_a_reparer.csv".')
print("Prévoir l'effet sur les ventes, les articles et les TND, puis rejouer.")
print("Les résultats du défi restent dans outputs/10/, séparés d'Atlas.")
