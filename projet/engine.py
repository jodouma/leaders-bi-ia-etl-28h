"""Ossature fournie. Lire les étapes ; adapter seulement les petites fonctions indiquées.

Une transaction contient dimensions, changement SCD2 et faits. Une erreur annule le lot.
Les cas généraux de correction rétroactive restent hors du socle.
"""
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import shutil
from uuid import uuid4

from lecture import lire_csv
from modele import connecter
from nettoyage import date_iso, nettoyer

TABLE_COLUMNS = {
    "dim_product": ["product_key", "product_id", "product_name"],
    "dim_shop": ["shop_key", "shop_id", "shop_name", "commercial_zone", "valid_from", "valid_to"],
    "dim_date": ["date_key", "full_date", "year", "month", "day"],
    "fact_sales": ["sale_id", "date_key", "product_key", "shop_key", "quantity", "unit_price_millimes", "amount_millimes"],
}


def catalogues(data):
    data = Path(data)
    produits = {r["product_id"]: r["product_name"] for r in lire_csv(data / "produits.csv")}
    boutiques = {r["shop_id"]: r for r in lire_csv(data / "boutiques.csv")}
    return produits, boutiques


def temporal_key(conn, shop_id, sale_date):
    """Recherche fournie pour charger le socle ; le module incremental la fera adapter."""
    rows = conn.execute("SELECT shop_key FROM dim_shop WHERE shop_id=? AND valid_from<=? "
                        "AND (valid_to IS NULL OR ?<valid_to)", (shop_id, sale_date, sale_date)).fetchall()
    if len(rows) != 1:
        raise ValueError(f"Version temporelle unique attendue : {shop_id} au {sale_date}")
    return rows[0][0]


def verifier_histoire(conn):
    groupes = {}
    for row in conn.execute("SELECT * FROM dim_shop ORDER BY shop_id, valid_from"):
        date_iso(row["valid_from"])
        if row["valid_to"] is not None:
            date_iso(row["valid_to"])
            if row["valid_to"] <= row["valid_from"]:
                raise ValueError("Intervalle vide ou inversé")
        groupes.setdefault(row["shop_id"], []).append(row)
    for versions in groupes.values():
        if sum(r["valid_to"] is None for r in versions) != 1 or versions[-1]["valid_to"] is not None:
            raise ValueError("Une seule version courante est attendue")
        for avant, apres in zip(versions, versions[1:]):
            if avant["valid_to"] != apres["valid_from"]:
                raise ValueError("Trou ou chevauchement dans l'histoire")
        if len({r["shop_name"] for r in versions}) != 1:
            raise ValueError("Nom de boutique modifié hors socle")
    if conn.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("Clé étrangère invalide")
    for r in conn.execute("SELECT f.shop_key,d.full_date,s.shop_id FROM fact_sales f "
                          "JOIN dim_date d USING(date_key) JOIN dim_shop s USING(shop_key)"):
        if temporal_key(conn, r["shop_id"], r["full_date"]) != r["shop_key"]:
            raise ValueError("Fait rattaché à une mauvaise version temporelle")


def charger_catalogues(conn, produits, boutiques):
    for identifiant, nom in produits.items():
        ancien = conn.execute("SELECT product_name FROM dim_product WHERE product_id=?", (identifiant,)).fetchone()
        if ancien is None:
            conn.execute("INSERT INTO dim_product(product_id,product_name) VALUES (?,?)", (identifiant, nom))
        elif ancien[0] != nom:
            raise ValueError(f"Catalogue produit incohérent : {identifiant}")
    for identifiant, r in boutiques.items():
        debut = date_iso(r["valid_from"])
        versions = conn.execute("SELECT * FROM dim_shop WHERE shop_id=? ORDER BY valid_from", (identifiant,)).fetchall()
        if not versions:
            conn.execute("INSERT INTO dim_shop(shop_id,shop_name,commercial_zone,valid_from) VALUES (?,?,?,?)",
                         (identifiant, r["shop_name"], r["commercial_zone"], debut))
        else:
            premiere = versions[0]
            if (premiere["shop_name"], premiere["commercial_zone"], premiere["valid_from"]) != (r["shop_name"], r["commercial_zone"], debut):
                raise ValueError(f"Catalogue boutique incohérent : {identifiant}")
            # Ne jamais réouvrir la version initiale ni effacer une version avancée.


def appliquer_changement(conn, changement):
    identifiant = str(changement["shop_id"]).strip().upper()
    debut = date_iso(changement["effective_date"])
    zone = str(changement["commercial_zone"]).strip()
    if not zone:
        raise ValueError("Zone commerciale vide")
    meme_date = conn.execute("SELECT commercial_zone FROM dim_shop WHERE shop_id=? AND valid_from=?",
                             (identifiant, debut)).fetchone()
    if meme_date:
        if meme_date[0] != zone:
            raise ValueError("Changement conflictuel à la même date")
        return 0
    courante = conn.execute("SELECT * FROM dim_shop WHERE shop_id=? AND valid_to IS NULL", (identifiant,)).fetchone()
    if courante is None or debut <= courante["valid_from"]:
        raise ValueError("Changement hors ordre ou boutique inconnue")
    if zone == courante["commercial_zone"]:
        raise ValueError("Changement sans nouvelle zone")
    affectes = conn.execute("SELECT 1 FROM fact_sales f JOIN dim_date d USING(date_key) "
                            "WHERE shop_key=? AND full_date>=? LIMIT 1", (courante["shop_key"], debut)).fetchone()
    if affectes:
        raise ValueError("Changement rétroactif : faits existants à reclasser")
    conn.execute("UPDATE dim_shop SET valid_to=? WHERE shop_key=?", (debut, courante["shop_key"]))
    conn.execute("INSERT INTO dim_shop(shop_id,shop_name,commercial_zone,valid_from) VALUES (?,?,?,?)",
                 (identifiant, courante["shop_name"], zone, debut))
    return 1


def charger(lignes, changements, chemin_base, data, lookup=temporal_key, strict=False):
    produits, boutiques = catalogues(data)
    ventes, rejets, doublons = nettoyer(lignes, produits, boutiques)
    if strict and rejets:
        raise ValueError(f"Lot SQL rejeté entièrement : {len(rejets)} ligne(s) invalide(s)")
    bilan = {"raw": len(lignes), "accepted": len(ventes), "rejected": len(rejets), "duplicate": len(doublons),
             "inserted": 0, "existing": 0, "new_shop_versions": 0, "rejects": rejets}
    conn = connecter(chemin_base, preparer=True)
    try:
        conn.execute("BEGIN IMMEDIATE")
        verifier_histoire(conn)
        charger_catalogues(conn, produits, boutiques)
        verifier_histoire(conn)
        for evenement in changements:
            bilan["new_shop_versions"] += appliquer_changement(conn, evenement)
        for vente in ventes:
            jour = date.fromisoformat(vente["date"])
            date_key = int(jour.strftime("%Y%m%d"))
            product_key = conn.execute("SELECT product_key FROM dim_product WHERE product_id=?", (vente["product_id"],)).fetchone()[0]
            shop_key = lookup(conn, vente["shop_id"], vente["date"])
            valeurs = (vente["sale_id"], date_key, product_key, shop_key, vente["quantity"],
                       vente["unit_price_millimes"], vente["amount_millimes"])
            ancien = conn.execute("SELECT * FROM fact_sales WHERE sale_id=?", (vente["sale_id"],)).fetchone()
            if ancien is not None:
                if tuple(ancien) != valeurs:
                    raise ValueError(f"Vente existante en conflit : {vente['sale_id']}")
                bilan["existing"] += 1
                continue
            conn.execute("INSERT OR IGNORE INTO dim_date VALUES (?,?,?,?,?)", (date_key, jour.isoformat(), jour.year, jour.month, jour.day))
            conn.execute("INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?)", valeurs)
            bilan["inserted"] += 1
        verifier_histoire(conn)
        conn.execute("COMMIT")
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
    return bilan


def rapport(chemin_base):
    conn = connecter(chemin_base)
    try:
        verifier_histoire(conn)
        facts, quantity, amount = conn.execute("SELECT count(*),coalesce(sum(quantity),0),coalesce(sum(amount_millimes),0) FROM fact_sales").fetchone()
        zones = dict(conn.execute("SELECT commercial_zone,sum(amount_millimes) FROM fact_sales JOIN dim_shop USING(shop_key) GROUP BY commercial_zone"))
        versions = dict(conn.execute("SELECT shop_id||'@'||valid_from,sum(amount_millimes) FROM fact_sales JOIN dim_shop USING(shop_key) GROUP BY shop_key"))
        return {"facts": facts, "quantity": quantity, "amount_millimes": amount, "zone_amounts_millimes": zones,
                "shop_version_amounts_millimes": versions,
                "products": conn.execute("SELECT count(*) FROM dim_product").fetchone()[0],
                "shop_versions": conn.execute("SELECT count(*) FROM dim_shop").fetchone()[0],
                "dates": conn.execute("SELECT count(*) FROM dim_date").fetchone()[0]}
    finally:
        conn.close()


def ecrire_json(chemin, contenu):
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
    temporaire.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporaire.replace(chemin)


def exporter(chemin_base, repertoire, delivery_id=None):
    delivery_id = delivery_id or "livraison-" + uuid4().hex[:12]
    if Path(delivery_id).name != delivery_id or delivery_id in (".", ".."):
        raise ValueError("Identifiant de livraison invalide")
    repertoire = Path(repertoire)
    repertoire.mkdir(parents=True, exist_ok=True)
    cible = repertoire / delivery_id
    if cible.exists():
        raise FileExistsError("Livraison déjà présente : choisir un nouvel identifiant")
    travail = repertoire / (".part-" + uuid4().hex)
    travail.mkdir()
    conn = None
    try:
        conn = connecter(chemin_base)
        conn.execute("BEGIN")  # Un seul instant logique pour les quatre tables.
        verifier_histoire(conn)
        manifest = {"schema_version": "atlas-v6-1", "delivery_id": delivery_id, "encoding": "utf-8-sig",
                    "delimiter": ",", "files": {}, "sums": {}}
        for table, colonnes in TABLE_COLUMNS.items():
            lignes = conn.execute(f"SELECT * FROM {table} ORDER BY {colonnes[0]}").fetchall()
            fichier = travail / (table + ".csv")
            with fichier.open("w", encoding="utf-8-sig", newline="") as flux:
                writer = csv.writer(flux)
                writer.writerow(colonnes)
                writer.writerows(tuple(ligne) for ligne in lignes)
            manifest["files"][fichier.name] = {"columns": colonnes, "rows": len(lignes), "sha256": hashlib.sha256(fichier.read_bytes()).hexdigest()}
        quantite, montant = conn.execute("SELECT coalesce(sum(quantity),0),coalesce(sum(amount_millimes),0) FROM fact_sales").fetchone()
        manifest["sums"] = {"quantity": quantite, "amount_millimes": montant}
        conn.execute("COMMIT")
        ecrire_json(travail / "manifest.json", manifest)  # Dernier fichier, puis publication du dossier entier.
        travail.rename(cible)
        return cible
    except BaseException:
        if conn is not None and conn.in_transaction:
            conn.execute("ROLLBACK")
        shutil.rmtree(travail, ignore_errors=True)
        raise
    finally:
        if conn is not None:
            conn.close()
