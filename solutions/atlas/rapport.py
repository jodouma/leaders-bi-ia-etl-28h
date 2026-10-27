"""07 — Interroger SQLite et produire un rapport autonome en HTML."""
from html import escape
from pathlib import Path
from lecture import OUTPUTS
from modele import connecter

SQL_BOUTIQUES = """SELECT s.shop_id, s.shop_name, SUM(f.quantity), SUM(f.amount_millimes)
    FROM fact_sales AS f JOIN dim_shop AS s ON s.shop_key = f.shop_key
    GROUP BY s.shop_id, s.shop_name ORDER BY s.shop_id"""
SQL_PRODUITS = """SELECT p.product_id, p.product_name, SUM(f.quantity), SUM(f.amount_millimes)
    FROM fact_sales AS f JOIN dim_product AS p ON p.product_key = f.product_key
    GROUP BY p.product_id, p.product_name ORDER BY p.product_id"""


def formater_tnd(millimes):
    """Afficher les trois décimales sans convertir le montant en float."""
    return f"{millimes // 1000}.{millimes % 1000:03d}"


def lignes_table(lignes):
    resultat = []
    for ligne in lignes:
        resultat.append(f"<tr><td>{escape(ligne['id'])}</td><th scope='row'>{escape(ligne['name'])}</th>"
                        f"<td>{ligne['quantity']}</td><td>{formater_tnd(ligne['amount_millimes'])}</td></tr>")
    return "".join(resultat)


def generer(chemin_base, chemin_html):
    """Calculer tous les indicateurs depuis la base actuelle, puis écrire le rapport."""
    if not Path(chemin_base).is_file():
        raise FileNotFoundError("Base absente : terminer les missions 04 et 05.")
    connexion = connecter(chemin_base)
    try:
        faits, quantite, montant, debut, fin = connexion.execute("""
            SELECT COUNT(*), COALESCE(SUM(f.quantity), 0), COALESCE(SUM(f.amount_millimes), 0),
                   MIN(d.full_date), MAX(d.full_date)
            FROM fact_sales AS f JOIN dim_date AS d ON d.date_key = f.date_key""").fetchone()
        boutiques = [{"id": r[0], "name": r[1], "quantity": r[2], "amount_millimes": r[3]}
                     for r in connexion.execute(SQL_BOUTIQUES)]
        produits = [{"id": r[0], "name": r[1], "quantity": r[2], "amount_millimes": r[3]}
                    for r in connexion.execute(SQL_PRODUITS)]
    finally:
        connexion.close()
    bilan = {"facts": faits, "quantity": quantite, "amount_millimes": montant,
             "period_start": debut, "period_end": fin, "shops": boutiques, "products": produits}
    periode = f"{debut} au {fin}" if debut else "Aucune vente chargée"
    html = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Papeterie — ventes observées</title><style>
:root{{--encre:#153d4a;--accent:#087f8c;--fond:#f3f7f5}}*{{box-sizing:border-box}}
body{{margin:0;background:var(--fond);color:var(--encre);font:18px/1.6 system-ui,sans-serif}}
main{{max-width:1000px;margin:auto;padding:42px 24px}}h1{{font-size:2.6rem;line-height:1.15}}
h2{{margin-top:2.5rem}}.surtitre{{letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}}
.kpis{{display:flex;flex-wrap:wrap;gap:16px}}.carte{{flex:1;min-width:180px;background:white;padding:24px;border-radius:16px}}
.chiffre{{display:block;font-size:2rem;font-weight:800}}table{{width:100%;border-collapse:collapse;background:white}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #d9e5e4}}td:nth-last-child(-n+2){{text-align:right}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#153d4a;color:white;padding:20px;border-radius:12px;font-size:.85rem}}
.note{{border-left:5px solid var(--accent);padding:8px 20px}}@media print{{body{{background:white}}main{{padding:0}}}}
</style></head><body><main><p class="surtitre">Atlas Papeterie · BI</p>
<h1>Que s’est-il vendu ?</h1><p>Période observée : <strong>{escape(periode)}</strong>.</p>
<div class="kpis"><section class="carte"><span class="chiffre">{faits}</span>ventes élémentaires</section>
<section class="carte"><span class="chiffre">{quantite}</span>unités vendues</section>
<section class="carte"><span class="chiffre">{formater_tnd(montant)}</span>chiffre d’affaires (TND)</section></div>
<h2>Ventes par boutique</h2><table><caption>Sommes sur la période observée</caption>
<thead><tr><th>Code</th><th>Boutique</th><th>Unités</th><th>CA (TND)</th></tr></thead><tbody>{lignes_table(boutiques)}</tbody></table>
<h2>Ventes par produit</h2><table><caption>Sommes sur la période observée</caption>
<thead><tr><th>Code</th><th>Produit</th><th>Unités</th><th>CA (TND)</th></tr></thead><tbody>{lignes_table(produits)}</tbody></table>
<p class="note">Ces ventes aident à discuter des prochains achats. Sans stocks ni coûts, elles ne permettent pas de calculer une marge, un besoin de réapprovisionnement ou une prévision.</p>
<h2>Comment sont obtenus ces résultats ?</h2><p>Grain : un produit vendu dans une boutique à une date, identifié par sale_id.
Chaque montant est quantité × prix unitaire. Les calculs et le stockage utilisent des millimes entiers : 1 TND = 1 000 millimes.</p>
<details><summary>Voir le SQL des agrégats</summary><h3>Boutiques</h3><pre>{escape(SQL_BOUTIQUES)}</pre>
<h3>Produits</h3><pre>{escape(SQL_PRODUITS)}</pre></details>
</main></body></html>"""
    chemin_html = Path(chemin_html)
    chemin_html.parent.mkdir(parents=True, exist_ok=True)
    chemin_html.write_text(html, encoding="utf-8")
    return bilan


def main():
    bilan = generer(OUTPUTS / "atlas.sqlite", OUTPUTS / "rapport_atlas.html")
    print(f"Rapport créé : {bilan['facts']} faits, {bilan['quantity']} unités, "
          f"{formater_tnd(bilan['amount_millimes'])} TND.")
    print(OUTPUTS / "rapport_atlas.html")


if __name__ == "__main__":
    main()
