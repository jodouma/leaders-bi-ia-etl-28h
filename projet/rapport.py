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
    # TODO — mission 07 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter rapport.py : generer.")


def main():
    bilan = generer(OUTPUTS / "atlas.sqlite", OUTPUTS / "rapport_atlas.html")
    print(f"Rapport créé : {bilan['facts']} faits, {bilan['quantity']} unités, "
          f"{formater_tnd(bilan['amount_millimes'])} TND.")
    print(OUTPUTS / "rapport_atlas.html")


if __name__ == "__main__":
    main()
