"""04 — Créer un schéma en étoile sans effacer les données."""
import sqlite3
from pathlib import Path
from lecture import OUTPUTS


def connecter(chemin_base):
    """SQLite active les clés étrangères pour chaque nouvelle connexion."""
    connexion = sqlite3.connect(chemin_base)
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def creer_modele(chemin_base):
    # TODO — mission 04 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter modele.py : creer_modele.")


def main():
    creer_modele(OUTPUTS / "atlas.sqlite")
    print("Modèle prêt : 3 dimensions, 1 table de faits. Données conservées.")


if __name__ == "__main__":
    main()
