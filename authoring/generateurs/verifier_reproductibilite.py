"""Vérifie que chaque générateur reproduit le CONTENU des données publiées dans modele-binome/.

Pour chaque mission :
  1. les fichiers publiés correspondent à reference/empreintes.json (écrit par le générateur) ;
  2. le générateur est relancé sur place, puis le contenu régénéré est comparé à ces mêmes empreintes ;
  3. le dossier de la mission et v7-data.json sont restaurés tels qu'ils étaient.

On compare le contenu, pas les octets, pour que le résultat soit le même sous Linux, macOS et Windows :
textes (CSV, JSON, MD) avec fins de ligne normalisées, classeurs Excel cellule par cellule, bases SQLite
par schéma + lignes triées ; les visuels PNG/SVG (rendu dépendant de matplotlib) sont seulement présents.
Utilisé par la CI du cours ; aucun réseau, aucune IA. La vérité privée n'est jamais écrite ici
(SOLEN_VERITE_PRIVEE est retirée de l'environnement du générateur).
"""
from __future__ import annotations

import json
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
sys.path.insert(0, str(HERE))
from common import EMPREINTES, V7_DATA, empreintes_contenu  # noqa: E402


def cible(generateur: Path) -> Path:
    num = generateur.stem[7:9]  # mission00_commerce360 → tronc-commun ; mission03_xxx → catalogue/M03
    return MODELE / "tronc-commun" if num == "00" else MODELE / "catalogue" / f"M{num}"


def ecarts(attendu: dict[str, str], observe: dict[str, str]) -> list[str]:
    return sorted(k for k in set(attendu) | set(observe) if attendu.get(k) != observe.get(k))


def main() -> int:
    echecs = 0
    env = {k: v for k, v in os.environ.items() if k != "SOLEN_VERITE_PRIVEE"}
    env.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    for gen in GENERATEURS:
        dest = cible(gen)
        nom = dest.relative_to(ROOT).as_posix()
        f = dest / "reference" / EMPREINTES
        if not dest.is_dir():
            print(f"IGNORÉ {gen.name} : {nom} absent")
            continue
        if not f.exists():
            echecs += 1
            print(f"ÉCHEC {gen.name} : {nom}/reference/{EMPREINTES} absent (relancez le générateur)")
            continue
        ref = json.loads(f.read_text(encoding="utf-8"))["fichiers"]
        publie = ecarts(ref, empreintes_contenu(dest))
        with tempfile.TemporaryDirectory() as tmp:
            sauvegarde, v7 = Path(tmp) / "avant", Path(tmp) / "v7-data.json"
            shutil.copytree(dest, sauvegarde)
            if V7_DATA.exists():
                shutil.copy2(V7_DATA, v7)
            try:
                r = subprocess.run([sys.executable, str(gen)], cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
                regenere = ecarts(ref, empreintes_contenu(dest)) if r.returncode == 0 else []
                ref2 = json.loads((dest / "reference" / EMPREINTES).read_text(encoding="utf-8"))["fichiers"] \
                    if r.returncode == 0 else ref
            finally:
                shutil.rmtree(dest)
                shutil.copytree(sauvegarde, dest)
                if v7.exists():
                    shutil.copy2(v7, V7_DATA)
        if r.returncode != 0:
            echecs += 1
            print(f"ÉCHEC {gen.name} : le générateur a échoué (code {r.returncode})\n{r.stderr[-1500:]}")
        elif publie or regenere or ref2 != ref:
            echecs += 1
            if publie:
                print(f"ÉCHEC {gen.name} : {len(publie)} fichier(s) publiés ≠ {EMPREINTES}, ex. {publie[:5]}")
            if regenere or ref2 != ref:
                d = regenere or ecarts(ref, ref2)
                print(f"ÉCHEC {gen.name} : {len(d)} fichier(s) régénérés au contenu différent, ex. {d[:5]}")
        else:
            print(f"OK {gen.name} : {len(ref)} fichiers, contenu identique → {nom}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
