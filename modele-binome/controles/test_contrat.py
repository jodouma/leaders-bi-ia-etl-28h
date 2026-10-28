"""Tests de contrat : la référence est complète, vos sorties la respectent, l'oracle détecte les erreurs.

    python -m pytest controles -q

Les tests sur vos sorties sont « ignorés » (skipped) tant que la sortie n'existe pas encore.
Ne modifiez pas ce fichier : si un test échoue, corrigez le code qui produit les sorties.
"""
import csv
import sqlite3

import pytest

from controles import verifier as V


# --------------------------------------------------------------------------- 1. la référence
def test_reference_complete(contrat, attendus):
    for cle in ("tables", "faits", "scd2", "vue_analyse", "indicateurs", "axes", "rejets", "export", "lots"):
        assert cle in contrat, f"contrat_entrepot.json : clé « {cle} » absente"
    lots = list(contrat["lots"])
    for lot in lots:
        a = attendus[lot]
        assert set(a["tables"]) == set(contrat["tables"]), f"{lot} : tables attendues ≠ tables du contrat"
        assert all(a["tables"][t] > 0 for t in contrat["faits"]), f"{lot} : aucun fait attendu"
        assert a["rejets"]["total"] == sum(a["rejets"]["par_motif"].values())
        assert {i["code"] for i in contrat["indicateurs"]} <= set(a["indicateurs"])
    for t in contrat["faits"]:
        assert attendus[lots[-1]]["tables"][t] >= attendus[lots[0]]["tables"][t], "un incrément n'enlève rien"
    assert attendus[lots[-1]]["rejeu"]["lignes_ajoutees"] == 0


def test_sources_presentes(dossier, attendus):
    for lot, a in attendus.items():
        for fichier, info in a["sources"].items():
            chemin = dossier / "sources" / lot / fichier
            assert chemin.exists(), f"source absente : {chemin}"
            if fichier.endswith(".csv"):
                with open(chemin, encoding=info.get("encodage", "utf-8"), newline="") as f:
                    n = sum(1 for _ in csv.reader(f, delimiter=info.get("separateur", ";"))) - 1
                assert n == info["lignes"], f"{chemin} : {n} lignes, la référence en annonce {info['lignes']}"


def test_echantillon_present(dossier):
    e = dossier / "echantillon"
    assert (e / "attendu.md").exists() and (e / "attendu.json").exists()
    for f in e.glob("*.csv"):
        assert len(f.read_text(encoding="utf-8").strip().splitlines()) <= 13, f"{f} : plus de 12 lignes"


# --------------------------------------------------------------------------- 2. vos sorties
def _sans_echec(rapport):
    assert not rapport.echecs, "\n" + "\n".join(f"ÉCHEC — {m}" for m in rapport.echecs)


def test_entrepot_conforme(verificateur, contrat):
    if not verificateur.entrepot.exists():
        pytest.skip("pas encore d'entrepôt (outputs/entrepot.sqlite)")
    lot = verificateur.detecter_lot()
    assert lot is not None, "l'entrepôt ne correspond à aucun lot de référence : lancez le vérificateur pour le détail"
    etape = contrat["lots"][lot]["etape"]
    verificateur.verifier_lot(lot, "rejeu" if etape == "increment" else etape)
    _sans_echec(verificateur.r)


def test_export_conforme(verificateur):
    if not verificateur.manifest.exists():
        pytest.skip("pas encore d'export (outputs/export/manifest.json)")
    verificateur.verifier_export(obligatoire=True)
    _sans_echec(verificateur.r)


def test_app_conforme(verificateur):
    if not verificateur.app.exists():
        pytest.skip("pas encore d'application (outputs/app/index.html)")
    verificateur.verifier_app(obligatoire=True)
    _sans_echec(verificateur.r)


# --------------------------------------------------------------------------- 3. l'oracle sait dire non
def _entrepot_vide(contrat, chemin):
    con = sqlite3.connect(chemin)
    for t, info in contrat["tables"].items():
        cols = ", ".join(f"{c} {'INTEGER' if c in info['colonnes_entieres'] else 'TEXT'}" for c in info["colonnes"])
        con.execute(f"CREATE TABLE {t} ({cols})")
    return con


def _ligne(info, **valeurs):
    return {c: valeurs.get(c, 1 if c in info["colonnes_entieres"] else "x") for c in info["colonnes"]}


def _inserer(con, table, ligne):
    con.execute(f"INSERT INTO {table} ({', '.join(ligne)}) VALUES ({', '.join('?' * len(ligne))})", list(ligne.values()))


def test_oracle_detecte_deux_versions_courantes(verificateur, contrat, attendus, tmp_path):
    con = _entrepot_vide(contrat, tmp_path / "e.sqlite")
    s = contrat["scd2"]
    info = contrat["tables"][s["table"]]
    for k, v in enumerate(attendus[list(attendus)[-1]]["scd2"]["versions"], 1):
        _inserer(con, s["table"], _ligne(info, **{s["cle"]: k, s["cle_metier"]: v["cle_metier"],
                                                  s["attribut"]: v["attribut"], "valid_from": v["valid_from"],
                                                  "valid_to": None}))
    verificateur.scd2(con, attendus[list(attendus)[-1]])
    assert any("version courante" in m for m in verificateur.r.echecs)


def test_oracle_detecte_montant_non_entier_et_orphelin(verificateur, contrat, tmp_path):
    con = _entrepot_vide(contrat, tmp_path / "e.sqlite")
    fait = contrat["faits"][0]
    info = contrat["tables"][fait]
    col = next(c for c in info["colonnes_entieres"] if c not in info["cles_etrangeres"] and c != info["cle"])
    _inserer(con, fait, _ligne(info, **{col: 1.5}))
    verificateur.colonnes_valeurs(con)
    verificateur.cles_etrangeres(con)
    assert any("non entières" in m for m in verificateur.r.echecs)
    assert any("orpheline" in m for m in verificateur.r.echecs)


def test_oracle_formats():
    assert V.tnd(12345678) == "12 345,678 TND"
    assert V.egal(100, 100.0, "millimes", 0) and not V.egal(100, 100.5, "millimes", 0)
    assert V.egal(0.04, 0.04005, "ratio", 0.0001)
    assert V.montrer(2.4109, "jours") == "2,41 jours" and V.montrer(5.5, "heures") == "5,50 h"
    assert V.egal(2.41, 2.4105, "jours", 0.001) and V.texte(18.0) == V.texte("18") == "18"
