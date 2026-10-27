"""05 — Charger un lot dans une transaction, avec identifiants stables."""
from datetime import date
from pathlib import Path
from lecture import OUTPUTS, catalogues, lire_csv
from modele import connecter


def inserer_catalogues(connexion, produits, boutiques):
    """Les identifiants métier retrouvent toujours la même clé technique."""
    for identifiant, nom in produits.items():
        connexion.execute("INSERT OR IGNORE INTO dim_product(product_id, product_name) VALUES (?, ?)",
                          (identifiant, nom))
    for identifiant, nom in boutiques.items():
        connexion.execute("INSERT OR IGNORE INTO dim_shop(shop_id, shop_name) VALUES (?, ?)",
                          (identifiant, nom))
    cles_produits = dict(connexion.execute("SELECT product_id, product_key FROM dim_product"))
    cles_boutiques = dict(connexion.execute("SELECT shop_id, shop_key FROM dim_shop"))
    return cles_produits, cles_boutiques


def charger(ventes, produits, boutiques, chemin_base):
    """Insérer les nouvelles ventes, reconnaître les identiques, annuler tout le lot si conflit."""
    if not Path(chemin_base).is_file():
        raise FileNotFoundError("Base absente : exécuter modele.py après la mission 04.")
    resultat = {"inserted": 0, "existing": 0}
    connexion = connecter(chemin_base)
    try:
        with connexion:
            cles_produits, cles_boutiques = inserer_catalogues(connexion, produits, boutiques)
            for vente in ventes:
                jour = date.fromisoformat(vente["date"])
                cle_date = int(jour.strftime("%Y%m%d"))
                connexion.execute("INSERT OR IGNORE INTO dim_date VALUES (?, ?, ?, ?, ?)",
                                  (cle_date, jour.isoformat(), jour.year, jour.month, jour.day))
                valeurs = (cle_date, cles_produits[vente["product_id"]],
                           cles_boutiques[vente["shop_id"]], vente["quantity"],
                           vente["unit_price_millimes"], vente["amount_millimes"])
                existante = connexion.execute("""SELECT date_key, product_key, shop_key, quantity,
                        unit_price_millimes, amount_millimes FROM fact_sales WHERE sale_id = ?""",
                        (vente["sale_id"],)).fetchone()
                if existante is None:
                    connexion.execute("INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (vente["sale_id"],) + valeurs)
                    resultat["inserted"] += 1
                elif existante == valeurs:
                    resultat["existing"] += 1
                else:
                    raise ValueError(f"Conflit sale_id {vente['sale_id']} : transaction annulée.")
    finally:
        connexion.close()
    return resultat


def lire_ventes_nettoyees(chemin):
    """Relire le résultat de 03 ; les colonnes numériques quittent le format texte CSV."""
    ventes = lire_csv(chemin)
    for vente in ventes:
        for champ in ("quantity", "unit_price_millimes", "amount_millimes"):
            vente[champ] = int(vente[champ])
    return ventes


def total_base(chemin_base):
    connexion = connecter(chemin_base)
    try:
        return connexion.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0), "
                                 "COALESCE(SUM(amount_millimes), 0) FROM fact_sales").fetchone()
    finally:
        connexion.close()


def main():
    produits, boutiques = catalogues()
    ventes = lire_ventes_nettoyees(OUTPUTS / "ventes_nettoyees.csv")
    resultat = charger(ventes, produits, boutiques, OUTPUTS / "atlas.sqlite")
    faits, quantite, montant = total_base(OUTPUTS / "atlas.sqlite")
    print(f"Lot initial : {resultat['inserted']} nouvelles, {resultat['existing']} existantes.")
    print(f"Base actuelle : {faits} faits, {quantite} unités, {montant / 1000:.3f} TND.")


if __name__ == "__main__":
    main()
