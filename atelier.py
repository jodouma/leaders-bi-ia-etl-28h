"""Outils communs d'Atlas. Python 3.10+, bibliothèque standard seulement.

Les scripts numérotés montrent les gestes à apprendre. Ce fichier centralise
les chemins, les contrôles et la plomberie répétée. Il peut se lire plus tard.
Aucune donnée réelle de boutique ou de personne n'est utilisée.
"""
from pathlib import Path
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import csv
import html
import json
import sqlite3

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIELDS = ["sale_id", "date", "shop_id", "product_id", "quantity",
          "unit_price_tnd"]
CLEAN_FIELDS = FIELDS
TRANSFORMED_FIELDS = ["sale_id", "date", "shop_id", "product_id", "quantity",
                      "unit_price_millimes", "amount_millimes"]
SCHEMA = """CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_shop (
    shop_key INTEGER PRIMARY KEY,
    shop_id TEXT NOT NULL UNIQUE,
    shop_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id TEXT PRIMARY KEY NOT NULL,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    shop_key INTEGER NOT NULL REFERENCES dim_shop(shop_key),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_millimes INTEGER NOT NULL CHECK (unit_price_millimes > 0),
    amount_millimes INTEGER NOT NULL,
    CHECK (amount_millimes = quantity * unit_price_millimes)
);
"""


def read_csv(path):
    """Lire un CSV UTF-8 ; une liste de dictionnaires, valeurs encore textuelles."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}. Vérifiez l'étape précédente."
        )
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=",")
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("En-têtes CSV absents ou répétés.")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("Une ligne CSV a plus de cellules que les en-têtes.")
    return rows


def write_csv(path, fields, rows):
    """Écrire sans changer les données sources ; prix séparés par un point."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return path


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def read_catalogs(data_dir=DATA):
    products = {row["product_id"]: row["product_name"]
                for row in read_csv(Path(data_dir) / "produits.csv")}
    shops = {row["shop_id"]: row["shop_name"]
             for row in read_csv(Path(data_dir) / "boutiques.csv")}
    return products, shops


def price_to_millimes(text):
    """Pas de float : 4.500 TND devient exactement 4500 millimes."""
    try:
        value = Decimal(str(text).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("prix illisible") from None
    if not value.is_finite() or value <= 0:
        raise ValueError("prix non positif ou non fini")
    millimes = value * 1000
    if millimes != millimes.to_integral_value():
        raise ValueError("prix avec plus de trois décimales significatives")
    return int(millimes)


def money(millimes):
    """Formater un entier en TND avec trois décimales, sans arrondi flottant."""
    return f"{Decimal(int(millimes)) / 1000:.3f}"


def clean_sales(raw, products, shops):
    """Normaliser, contrôler, isoler les rejets et compter les doublons.

    Retour : (valides, rejets, doublons). Les rejets gardent la ligne source
    (numéro CSV, en-tête = 1) et sa raison. Un ID réutilisé avec un contenu
    différent est un conflit bloquant : rien n'est choisi silencieusement.
    """
    accepted, rejected, duplicates = [], [], []
    seen = {}
    for line_number, original in enumerate(raw, start=2):
        if set(original) != set(FIELDS):
            raise ValueError("Colonnes attendues : " + ", ".join(FIELDS))
        row = {key: str(original.get(key) or "").strip() for key in FIELDS}
        row["shop_id"] = row["shop_id"].upper()
        row["product_id"] = row["product_id"].upper()
        try:
            if not all(row.values()):
                raise ValueError("champ manquant")
            try:
                parsed_date = date.fromisoformat(row["date"])
            except ValueError:
                raise ValueError("date impossible ou mal formée") from None
            if parsed_date.isoformat() != row["date"]:
                raise ValueError("date attendue au format AAAA-MM-JJ")
            if row["shop_id"] not in shops:
                raise ValueError("boutique inconnue")
            if row["product_id"] not in products:
                raise ValueError("produit inconnu")
            if not row["quantity"].isascii() or not row["quantity"].isdigit():
                raise ValueError("quantité attendue : entier positif")
            quantity = int(row["quantity"])
            if quantity <= 0:
                raise ValueError("quantité non positive")
            price = price_to_millimes(row["unit_price_tnd"])
            row["quantity"] = str(quantity)
            row["unit_price_tnd"] = money(price)
        except (ValueError, OverflowError) as error:
            rejected.append({"source_line": line_number, **original,
                             "reason": str(error)})
            continue
        sale_id = row["sale_id"]
        if sale_id in seen:
            if seen[sale_id] != row:
                raise ValueError(f"Conflit : {sale_id} a deux contenus différents.")
            duplicates.append({"source_line": line_number, **row,
                               "reason": "vente identique déjà retenue"})
            continue
        seen[sale_id] = row
        accepted.append(row)
    assert len(raw) == len(accepted) + len(rejected) + len(duplicates)
    return accepted, rejected, duplicates


def save_cleaning(raw, products, shops, folder):
    """Produire les trois chemins de contrôle, sans modifier le CSV original."""
    folder = Path(folder)
    clean, rejects, duplicates = clean_sales(raw, products, shops)
    write_csv(folder / "ventes_nettoyees.csv", FIELDS, clean)
    audit_fields = ["source_line", *FIELDS, "reason"]
    write_csv(folder / "rejets.csv", audit_fields, rejects)
    write_csv(folder / "doublons.csv", audit_fields, duplicates)
    receipt = {"timestamp_utc": utc_now(), "raw": len(raw),
               "accepted": len(clean), "rejected": len(rejects),
               "duplicates": len(duplicates)}
    write_json(folder / "qualite.json", receipt)
    return clean, rejects, duplicates


def transform_sales(clean):
    """Une vente nettoyée devient une vente calculée, toujours au même grain."""
    result = []
    for row in clean:
        quantity = int(row["quantity"])
        unit_price = price_to_millimes(row["unit_price_tnd"])
        result.append({"sale_id": row["sale_id"], "date": row["date"],
                       "shop_id": row["shop_id"],
                       "product_id": row["product_id"],
                       "quantity": quantity,
                       "unit_price_millimes": unit_price,
                       "amount_millimes": quantity * unit_price})
    return result


def read_transformed(path):
    rows = read_csv(path)
    for row in rows:
        for field in ("quantity", "unit_price_millimes", "amount_millimes"):
            row[field] = int(row[field])
    return rows


def connect(db_path):
    """Le fichier de base est local. Les clés étrangères sont toujours actives."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection):
    """Créer les tables vides, sans effacer une table existante."""
    connection.executescript(SCHEMA)


def load_sales(db_path, rows, products, shops):
    """Charger dimensions puis faits dans UNE transaction.

    Même sale_id + mêmes valeurs : déjà présent. Même ID + changement :
    ValueError et annulation de tout le lot. Pas de DELETE ou de remplacement.
    """
    connection = connect(db_path)
    create_schema(connection)
    inserted = existing = 0
    try:
        with connection:
            for product_id, product_name in products.items():
                connection.execute(
                    "INSERT OR IGNORE INTO dim_product "
                    "(product_id, product_name) VALUES (?, ?)",
                    (product_id, product_name))
            for shop_id, shop_name in shops.items():
                connection.execute(
                    "INSERT OR IGNORE INTO dim_shop "
                    "(shop_id, shop_name) VALUES (?, ?)", (shop_id, shop_name))
            for row in rows:
                day = date.fromisoformat(row["date"])
                date_key = int(day.strftime("%Y%m%d"))
                connection.execute(
                    "INSERT OR IGNORE INTO dim_date VALUES (?, ?, ?, ?, ?)",
                    (date_key, day.isoformat(), day.year, day.month, day.day))
                product = connection.execute(
                    "SELECT product_key FROM dim_product WHERE product_id = ?",
                    (row["product_id"],)).fetchone()
                shop = connection.execute(
                    "SELECT shop_key FROM dim_shop WHERE shop_id = ?",
                    (row["shop_id"],)).fetchone()
                if product is None or shop is None:
                    raise ValueError("Dimension inconnue : contrôler les catalogues.")
                values = (date_key, product[0], shop[0], int(row["quantity"]),
                          int(row["unit_price_millimes"]),
                          int(row["amount_millimes"]))
                old = connection.execute(
                    "SELECT date_key, product_key, shop_key, quantity, "
                    "unit_price_millimes, amount_millimes FROM fact_sales "
                    "WHERE sale_id = ?", (row["sale_id"],)).fetchone()
                if old is not None:
                    if old != values:
                        raise ValueError(
                            f"Conflit : {row['sale_id']} existe avec un autre contenu."
                        )
                    existing += 1
                    continue
                connection.execute(
                    "INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (row["sale_id"], *values))
                inserted += 1
        return {"inserted": inserted, "existing": existing}
    finally:
        connection.close()


def totals(connection):
    sale_count, quantity, amount = connection.execute(
        "SELECT COUNT(*), COALESCE(SUM(quantity), 0), "
        "COALESCE(SUM(amount_millimes), 0) FROM fact_sales"
    ).fetchone()
    return {"sales": sale_count, "quantity": quantity,
            "amount_millimes": amount}


def database_totals(db_path):
    if not Path(db_path).is_file():
        raise FileNotFoundError("Base absente : exécutez d'abord le script 07.")
    connection = connect(db_path)
    try:
        return totals(connection)
    finally:
        connection.close()


def group_sales(connection, dimension):
    """SQL fixe, noms choisis dans une petite liste fermée, aucune saisie SQL."""
    queries = {
        "product": """SELECT d.product_name, SUM(f.quantity),
            SUM(f.amount_millimes)
            FROM fact_sales AS f
            JOIN dim_product AS d ON f.product_key = d.product_key
            GROUP BY d.product_key, d.product_name
            ORDER BY SUM(f.amount_millimes) DESC, d.product_name""",
        "shop": """SELECT d.shop_name, SUM(f.quantity), SUM(f.amount_millimes)
            FROM fact_sales AS f
            JOIN dim_shop AS d ON f.shop_key = d.shop_key
            GROUP BY d.shop_key, d.shop_name
            ORDER BY SUM(f.amount_millimes) DESC, d.shop_name""",
        "date": """SELECT d.full_date, SUM(f.quantity), SUM(f.amount_millimes)
            FROM fact_sales AS f
            JOIN dim_date AS d ON f.date_key = d.date_key
            GROUP BY d.date_key, d.full_date ORDER BY d.date_key""",
    }
    if dimension not in queries:
        raise ValueError("Choisir product, shop ou date.")
    return connection.execute(queries[dimension]).fetchall()


def build_report(db_path, html_path, title="Atlas Papeterie — ventes observées"):
    """Un HTML autonome et des CSV d'agrégats issus de la vraie base SQLite."""
    if not Path(db_path).is_file():
        raise FileNotFoundError("Base absente : exécutez d'abord le script 07.")
    html_path = Path(html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(db_path)
    try:
        summary = totals(connection)
        groups = {key: group_sales(connection, key)
                  for key in ("product", "shop", "date")}
    finally:
        connection.close()
    sections = []
    dates = [row[0] for row in groups["date"]]
    period = f"du {dates[0]} au {dates[-1]}" if dates else "aucune vente chargée"
    labels = {"product": "Par produit", "shop": "Par boutique", "date": "Par date"}
    for key, rows in groups.items():
        export = [{"label": name, "quantity": quantity,
                   "amount_tnd": money(amount)} for name, quantity, amount in rows]
        write_csv(html_path.parent / f"ventes_par_{key}.csv",
                  ["label", "quantity", "amount_tnd"], export)
        cells = "".join(
            f"<tr><th scope='row'>{html.escape(name)}</th>"
            f"<td>{quantity}</td><td>{money(amount)}</td></tr>"
            for name, quantity, amount in rows)
        max_amount = max((amount for _, _, amount in rows), default=1) or 1
        bars = "".join(
            f"<div class='barrow'><span>{html.escape(name)}</span>"
            f"<div class='bar' style='width:{amount / max_amount * 100:.2f}%'>"
            f"</div><b>{money(amount)} TND</b></div>"
            for name, _, amount in rows)
        sections.append(f"<section><h2>{labels[key]}</h2><div class='bars'>{bars}"
                        f"</div><table><thead><tr><th>Groupe</th>"
                        f"<th>Articles vendus</th><th>Montant (TND)</th></tr>"
                        f"</thead><tbody>{cells}</tbody></table></section>")
    document = """<!doctype html><html lang="fr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title><style>
:root {color-scheme:light} * {box-sizing:border-box} body {margin:0;
background:#f3f5fc;color:#1a1f4d;font:17px/1.55 Arial,sans-serif}
main {max-width:1000px;margin:auto;padding:40px 24px} h1 {font-size:38px;
line-height:1.1;color:#2b3180} .tag {font-size:13px;text-transform:uppercase;
letter-spacing:.1em} .kpis {display:flex;gap:18px;flex-wrap:wrap}
.kpi {background:#07152f;color:white;border-radius:18px;padding:22px;
flex:1;min-width:190px}.kpi b {display:block;font-size:32px;color:#ff9a3c}
section {background:white;padding:24px;margin-top:24px;border-radius:18px}
h2 {color:#2b3180} table {border-collapse:collapse;width:100%;margin-top:20px}
th,td {text-align:left;padding:10px;border-bottom:1px solid #dde0ef}
.bar {background:#2b3180;height:18px;border-radius:20px;max-width:100%}
.barrow {display:grid;grid-template-columns:110px minmax(30px,1fr) 120px;
gap:12px;align-items:center;margin:12px 0}.barrow b {font-size:14px}
small {color:#535a7a}.note {border-radius:12px;background:#f3f5fc;padding:18px}
@media(max-width:560px){h1{font-size:28px}main{padding:24px 12px}
section{padding:16px}.barrow{grid-template-columns:85px 1fr 105px;gap:6px}}
</style><main><p class="tag">Leaders University · Atlas Papeterie · données fictives</p>
<h1>__TITLE__</h1><p>Des lignes contrôlées à une lecture des ventes.</p>
<p><strong>Période des ventes :</strong> __PERIOD__.</p>
<div class="kpis"><div class="kpi"><b>__SALES__</b>ventes élémentaires</div>
<div class="kpi"><b>__QUANTITY__</b>articles vendus</div>
<div class="kpi"><b>__AMOUNT__ TND</b>montant des ventes</div></div>
__SECTIONS__<section><h2>Lire avant de décider</h2><p class="note">
Une ligne = une vente élémentaire, pas un client ni une commande complète.
Montant = quantité × prix unitaire. Les barres comparent les montants en TND ;
leur largeur est relative au montant maximum de chaque section.</p>
<p>Les ventes observées aident à choisir quels produits examiner. Elles ne
mesurent ni les stocks, ni les coûts, ni la marge. Des totaux sur des nombres
de jours différents ne prouvent pas une hausse de performance.</p>
<p>Question : quelles données supplémentaires demander avant un achat ?</p>
<small>Source : __SOURCE__. Généré le __TIME__.</small></section></main></html>"""
    replacements = {"__TITLE__": html.escape(title),
                    "__SALES__": str(summary["sales"]),
                    "__QUANTITY__": str(summary["quantity"]),
                    "__AMOUNT__": money(summary["amount_millimes"]),
                    "__PERIOD__": html.escape(period),
                    "__SECTIONS__": "".join(sections),
                    "__SOURCE__": html.escape(Path(db_path).name),
                    "__TIME__": utc_now()}
    for marker, value in replacements.items():
        document = document.replace(marker, value)
    html_path.write_text(document, encoding="utf-8")
    return summary


def describe(summary):
    return (f"{summary['sales']} ventes | {summary['quantity']} articles | "
            f"{money(summary['amount_millimes'])} TND")
