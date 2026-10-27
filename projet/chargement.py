"""Commandes métier fournies ; réutilisées par executer.py et les contrôles."""
from pathlib import Path
from engine import charger, ecrire_json
from lecture import lire_csv
import lecture
import incremental


def initial(data, outputs):
    data, outputs = Path(data), Path(outputs)
    bilan = charger(lire_csv(data / "ventes_initiales.csv"), [], outputs / "atlas.sqlite", data)
    ecrire_json(outputs / "qualite_initial.json", {k: bilan[k] for k in ("raw", "accepted", "rejected", "duplicate", "rejects")})
    ecrire_json(outputs / "chargement_initial.json", bilan)
    return bilan


def increment(data, outputs, batch_id="2026-01-08"):
    data, outputs = Path(data), Path(outputs)
    base = outputs / "atlas.sqlite"
    if not base.is_file():
        raise FileNotFoundError("Exécuter initial avant increment")
    ventes, changements, preuve = lecture.lire_increment_sql(data / "source_operationnelle.sqlite", batch_id)
    preuve.update({"extracted_sales": len(ventes), "extracted_changes": len(changements)})
    ecrire_json(outputs / "extraction_sql.json", preuve)
    bilan = charger(ventes, changements, base, data, incremental.trouver_shop_key, strict=True)
    ecrire_json(outputs / "chargement_increment.json", bilan)
    return bilan
