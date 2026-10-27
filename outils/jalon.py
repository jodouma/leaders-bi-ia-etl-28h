"""Créer une NOUVELLE copie de reprise, complète seulement jusqu'au jalon choisi.

Exemple depuis la racine : python outils/jalon.py 03 --destination reprise-03
La copie projet/ actuelle n'est jamais modifiée. L'accès aux corrigés est explicite.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULES = ["calcul.py", "lecture.py", "nettoyage.py", "modele.py", "chargement.py", "incremental.py", "rapport.py"]


def creer_reprise(numero, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f"Destination déjà présente : {destination}. Choisir un nouveau dossier.")
    source = ROOT / "projet"
    if source == destination or source in destination.parents:
        raise ValueError("Choisir une destination en dehors de projet/.")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("outputs", "__pycache__", "*.pyc"))
    (destination / "outputs").mkdir()
    for nom in MODULES[:numero]:
        shutil.copy2(ROOT / "solutions" / "atlas" / nom, destination / nom)
    # Exécuter uniquement les étapes rendues complètes, dans la nouvelle copie.
    for nom in MODULES[:numero]:
        subprocess.run([sys.executable, str(destination / nom)], cwd=destination, check=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jalon", choices=[f"{n:02d}" for n in range(8)])
    parser.add_argument("--destination", required=True, help="Nouveau dossier, jamais un dossier existant")
    args = parser.parse_args()
    try:
        destination = creer_reprise(int(args.jalon), args.destination)
    except (FileExistsError, ValueError, subprocess.CalledProcessError) as erreur:
        parser.exit(1, f"Reprise interrompue : {erreur}\n")
    print(f"Copie créée : {destination}")
    print(f"Étapes 01 à {args.jalon} terminées dans cette copie ; poursuivre avec la suivante.")


if __name__ == "__main__":
    main()
