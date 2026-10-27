"""02 — Lire les fichiers CSV du projet."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# La référence utilise les mêmes sources ; une copie de projet reste autonome.
DATA = ROOT / "data"
if not DATA.is_dir():
    DATA = ROOT.parents[1] / "projet" / "data"
OUTPUTS = ROOT / "outputs"


def lire_csv(chemin):
    """Renvoyer une liste de dictionnaires ; chaque valeur reste du texte."""
    with Path(chemin).open(encoding="utf-8-sig", newline="") as fichier:
        return list(csv.DictReader(fichier))


def catalogues(chemin_data=DATA):
    """Préparer les deux dictionnaires attendus par le nettoyage."""
    chemin_data = Path(chemin_data)
    produits = {ligne["product_id"]: ligne["product_name"]
                for ligne in lire_csv(chemin_data / "produits.csv")}
    boutiques = {ligne["shop_id"]: ligne["shop_name"]
                 for ligne in lire_csv(chemin_data / "boutiques.csv")}
    return produits, boutiques


def ecrire_csv(chemin, lignes, champs):
    """Sauver un résultat lisible ; même un journal vide possède un en-tête."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=champs)
        writer.writeheader()
        writer.writerows(lignes)


def main():
    lignes = lire_csv(DATA / "ventes_initiales.csv")
    print(f"Lecture : {len(lignes)} lignes ; champs : {', '.join(lignes[0])}")
    print("Première vente :", lignes[0])


if __name__ == "__main__":
    main()
