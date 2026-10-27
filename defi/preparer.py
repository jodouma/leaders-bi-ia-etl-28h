"""Préparer un incident Atlas isolé : python3 defi/preparer.py atelier-defi.

L'incident porte sur une règle de quantité, jamais sur les données originales.
"""
from pathlib import Path
import argparse
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("outil_jalon", ROOT / "outils" / "jalon.py")
jalon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jalon)


def preparer(destination):
    destination = jalon.creer_reprise(7, destination)
    fichier = destination / "nettoyage.py"
    code = fichier.read_text(encoding="utf-8")
    avant = 'vente["quantity"] = entier_positif(ligne["quantity"])'
    if code.count(avant) != 1:
        raise ValueError("Amorce quantité inattendue")
    fichier.write_text(code.replace(avant, avant + " + 1"), encoding="utf-8")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    try:
        destination = preparer(args.destination)
    except (FileExistsError, ValueError) as erreur:
        parser.exit(1, f"Préparation interrompue : {erreur}\n")
    print(f"Incident préparé dans {destination}. Lire defi/student_challenge.md depuis la racine.")
