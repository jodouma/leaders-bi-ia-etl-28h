"""Vérifie que chaque générateur reproduit exactement les données publiées dans modele-binome/.

Régénère chaque mission dans un dossier temporaire (variable SOLEN_RACINE si le générateur la lit,
sinon copie puis compare) et compare les empreintes fichier par fichier avec le dépôt.
Utilisé par la CI du cours ; aucun réseau, aucune IA.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODELE = ROOT / "modele-binome"
GENERATEURS = sorted(p for p in HERE.glob("mission*.py") if not p.name.startswith("textes_"))
IGNORES = {"outputs"}


def empreintes(dossier: Path) -> dict[str, str]:
    res = {}
    for p in sorted(dossier.rglob("*")):
        if p.is_file() and not any(part in IGNORES for part in p.relative_to(dossier).parts):
            res[str(p.relative_to(dossier)).replace(os.sep, "/")] = hashlib.sha256(p.read_bytes()).hexdigest()
    return res


def cible(generateur: Path) -> Path:
    nom = generateur.stem  # mission00_commerce360 → tronc-commun ; mission03_xxx → catalogue/M03
    num = nom[7:9]
    return MODELE / "tronc-commun" if num == "00" else MODELE / "catalogue" / f"M{num}"


def main() -> int:
    echecs = 0
    for gen in GENERATEURS:
        dest = cible(gen)
        if not dest.is_dir():
            print(f"IGNORÉ {gen.name} : {dest.relative_to(ROOT)} absent")
            continue
        avant = empreintes(dest)
        with tempfile.TemporaryDirectory() as tmp:
            sauvegarde = Path(tmp) / "avant"
            shutil.copytree(dest, sauvegarde)
            try:
                subprocess.run([sys.executable, str(gen)], cwd=ROOT, check=True,
                               stdout=subprocess.DEVNULL, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                apres = empreintes(dest)
            finally:
                shutil.rmtree(dest)
                shutil.copytree(sauvegarde, dest)
        diff = sorted(k for k in set(avant) | set(apres) if avant.get(k) != apres.get(k))
        if diff:
            echecs += 1
            print(f"ÉCHEC {gen.name} : {len(diff)} fichier(s) diffèrent, ex. {diff[:5]}")
        else:
            print(f"OK {gen.name} : {len(avant)} fichiers identiques → {dest.relative_to(ROOT)}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
