"""05 — Charger un lot dans une transaction, avec identifiants stables."""
from datetime import date
from pathlib import Path
from lecture import OUTPUTS, catalogues, lire_csv
from modele import connecter


def charger(ventes, produits, boutiques, chemin_base):
    # TODO — mission 05 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter chargement.py : charger.")


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
