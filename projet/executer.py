"""Depuis atelier : python3 executer.py initial / increment / export / rapport."""
import argparse
import json
import sqlite3
from chargement import initial, increment
from engine import ecrire_json, exporter, rapport
from lecture import DATA, OUTPUTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("initial", "increment", "export", "rapport"))
    args = parser.parse_args()
    try:
        if args.action == "initial":
            resultat = initial(DATA, OUTPUTS)
        elif args.action == "increment":
            resultat = increment(DATA, OUTPUTS)
        elif args.action == "export":
            resultat = {"delivery": str(exporter(OUTPUTS / "atlas.sqlite", OUTPUTS / "powerbi"))}
        else:
            resultat = rapport(OUTPUTS / "atlas.sqlite")
            ecrire_json(OUTPUTS / "rapport.json", resultat)
    except (ValueError, NotImplementedError, FileNotFoundError, sqlite3.Error, OverflowError) as erreur:
        parser.exit(1, f"À corriger : {erreur}\n")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
