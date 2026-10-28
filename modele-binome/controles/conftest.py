"""Réglages pytest des contrôles fournis (ne pas modifier).

Variables d'environnement facultatives : SOLEN_RACINE (racine du dépôt), SOLEN_MISSION
(sinon mission.txt), SOLEN_SORTIES (sinon <racine>/outputs).
"""
import json
import os
from pathlib import Path

import pytest

from controles import verifier as V


@pytest.fixture(scope="session")
def racine() -> Path:
    return Path(os.environ.get("SOLEN_RACINE") or Path(__file__).resolve().parents[1]).resolve()


@pytest.fixture(scope="session")
def mission(racine) -> str:
    return V.lire_mission(racine, os.environ.get("SOLEN_MISSION"))


@pytest.fixture(scope="session")
def dossier(racine, mission) -> Path:
    return V.dossier_mission(racine, mission)


@pytest.fixture(scope="session")
def contrat(dossier) -> dict:
    return json.loads((dossier / "reference" / "contrat_entrepot.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def attendus(dossier, contrat) -> dict:
    return {lot: json.loads((dossier / "reference" / info["attendu"]).read_text(encoding="utf-8"))
            for lot, info in contrat["lots"].items()}


@pytest.fixture(scope="session")
def sorties(racine) -> Path:
    return Path(os.environ.get("SOLEN_SORTIES") or racine / "outputs").resolve()


@pytest.fixture()
def verificateur(racine, mission, sorties):
    return V.Verificateur(racine, mission, sorties)
