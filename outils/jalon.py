"""Copie neuve et autonome : python3 outils/jalon.py 01 atelier.

Jalon = fonctions complétées jusqu'à ce contrôle. Les sorties restent vides.
01 : starter ; 02 : normalisation ; 03/04 : + SQL ; 05/06/07 : + lookup temporel.
"""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def creer_reprise(numero, destination):
    if numero not in range(1, 8):
        raise ValueError("Jalon attendu : 01 à 07")
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f"Dossier déjà présent : {destination}. Choisir un dossier neuf.")
    source = ROOT / "projet"
    if source in destination.parents:
        raise ValueError("Choisir une destination en dehors de projet/.")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("outputs", "__pycache__", "*.pyc"))
    (destination / "outputs").mkdir()
    for seuil, module in ((2, "nettoyage.py"), (3, "lecture.py"), (5, "incremental.py")):
        if numero >= seuil:
            shutil.copy2(ROOT / "solutions" / "atlas" / module, destination / module)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jalon", choices=[f"{n:02d}" for n in range(1, 8)])
    parser.add_argument("destination", help="Dossier neuf, jamais un dossier existant")
    args = parser.parse_args()
    try:
        destination = creer_reprise(int(args.jalon), args.destination)
    except (FileExistsError, ValueError) as erreur:
        parser.exit(1, f"Reprise interrompue : {erreur}\n")
    print(f"Jalon {args.jalon} créé : {destination}")
    print(f"Depuis ce dossier : python3 verifier.py {args.jalon}")
    print("Aucune sortie préchargée. Le dossier de travail précédent reste disponible.")


if __name__ == "__main__":
    main()
