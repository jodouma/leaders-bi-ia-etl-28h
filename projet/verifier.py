"""Contrôles du code courant dans des sorties temporaires isolées, jamais dans outputs/.

python3 verifier.py 01 ... 07 / tout. Un contrôle ne complète aucune fonction.
Une réussite ETL ne prouve aucune exécution Power BI, installation ou connexion Codex.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from calcul import montant
from chargement import initial, increment
from engine import exporter, rapport
from lecture import DATA, lire_csv
import lecture
from nettoyage import nettoyer
import incremental


def exiger(condition, message):
    if not condition:
        raise ValueError(message)


def controler(numero, temporaire):
    temporaire = Path(temporaire)
    if numero == 1:
        exiger(len(lire_csv(DATA / "ventes_initiales.csv")) == 16, "16 lignes CSV attendues")
        conn = lecture.connexion_source(DATA / "source_operationnelle.sqlite")
        try:
            exiger(conn.execute("SELECT count(*) FROM source_sales").fetchone()[0] == 3, "3 ventes SQL attendues")
        finally:
            conn.close()
        exiger(montant(2, 4500) == 9000, "Le calcul de départ doit donner 9000 millimes")
        return "sources disponibles ; calcul 9000 millimes"
    if numero == 2:
        from engine import catalogues
        produits, boutiques = catalogues(DATA)
        ventes, rejets, doublons = nettoyer(lire_csv(DATA / "ventes_initiales.csv"), produits, boutiques)
        exiger((len(ventes), len(rejets), len(doublons)) == (12, 3, 1), "Qualité attendue : 12 / 3 / 1")
        exiger(sum(r["quantity"] for r in ventes) == 32, "32 unités attendues")
        exiger(sum(r["amount_millimes"] for r in ventes) == 99000, "99000 millimes attendus")
        return "12 acceptées, 3 rejets, 1 doublon ; 32 unités, 99000 millimes"
    if numero == 3:
        ventes, changements, preuve = lecture.lire_increment_sql(DATA / "source_operationnelle.sqlite")
        exiger((len(ventes), len(changements)) == (3, 1), "Extraction SQL attendue : 3 ventes et 1 changement")
        exiger({r["sale_id"] for r in ventes} == {"S012", "S013", "S014"}, "Ventes du lot attendues")
        exiger(preuve["queries"][0]["params"] == ["2026-01-08"], "Paramètre de lot manquant")
        return "vraie extraction SQL : 3 ventes, 1 changement"
    if numero == 5:
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("CREATE TABLE dim_shop(shop_key INTEGER, shop_id TEXT, valid_from TEXT, valid_to TEXT)")
            conn.executemany("INSERT INTO dim_shop VALUES (?,?,?,?)", [(1,"NBE","2026-01-05","2026-01-08"), (3,"NBE","2026-01-08",None)])
            exiger(incremental.trouver_shop_key(conn,"NBE","2026-01-07") == 1, "Le 7 janvier appartient à l'ancienne version")
            exiger(incremental.trouver_shop_key(conn,"NBE","2026-01-08") == 3, "Le 8 janvier appartient à la nouvelle version")
            try:
                incremental.trouver_shop_key(conn,"NBE","2026-01-04")
            except ValueError:
                pass
            else:
                raise ValueError("Une date avant le début doit être refusée")
        finally:
            conn.close()
        return "frontière [début, fin) et version absente contrôlées"
    initial(DATA, temporaire)
    base = temporaire / "atlas.sqlite"
    if numero == 4:
        r = rapport(base)
        exiger((r["facts"], r["quantity"], r["amount_millimes"], r["shop_versions"]) == (12,32,99000,2), "Bilan initial incorrect")
        return "étoile initiale : 12 faits, 32 unités, 99000 millimes"
    ajout = increment(DATA, temporaire)
    exiger((ajout["inserted"], ajout["existing"], ajout["new_shop_versions"]) == (2,1,1), "Incrément attendu : 2 / 1 / 1")
    r = rapport(base)
    exiger((r["facts"], r["quantity"], r["amount_millimes"], r["shop_versions"]) == (14,35,115500,3), "Bilan final incorrect")
    exiger(r["zone_amounts_millimes"] == {"Cap Bon":43500,"Grand Tunis":72000}, "Zones historiques incorrectes")
    rejeu = increment(DATA, temporaire)
    exiger((rejeu["inserted"],rejeu["existing"],rejeu["new_shop_versions"]) == (0,3,0), "Rejeu incorrect")
    exiger(rapport(base) == r, "Le rejeu a modifié les résultats")
    if numero == 6:
        return "14 faits, 35 unités, 115500 millimes ; rejeu 0 / 3 / 0 ; zones 43500 / 72000"
    livraison = exporter(base, temporaire / "powerbi")
    manifest = json.loads((livraison / "manifest.json").read_text(encoding="utf-8"))
    for nom, info in manifest["files"].items():
        fichier = livraison / nom
        exiger(hashlib.sha256(fichier.read_bytes()).hexdigest() == info["sha256"], "Empreinte export incorrecte")
        with fichier.open(encoding="utf-8-sig", newline="") as flux:
            lecteur = csv.DictReader(flux)
            exiger(lecteur.fieldnames == info["columns"], "Colonnes export incorrectes")
            exiger(len(list(lecteur)) == info["rows"], "Nombre de lignes export incorrect")
    return "4 CSV + manifeste cohérents ; Power BI Desktop reste à manipuler sur Windows"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jalon", choices=[f"{n:02d}" for n in range(1,8)] + ["tout"])
    args = parser.parse_args()
    numeros = range(1,8) if args.jalon == "tout" else [int(args.jalon)]
    for numero in numeros:
        try:
            with TemporaryDirectory(prefix="atlas-verification-") as travail:
                message = controler(numero, travail)
        except (ValueError, NotImplementedError, FileNotFoundError, KeyError, sqlite3.Error) as erreur:
            parser.exit(1, f"À corriger — {numero:02d} : {erreur}\n")
        print(f"OK {numero:02d} — {message} (sorties isolées)")


if __name__ == "__main__":
    main()
