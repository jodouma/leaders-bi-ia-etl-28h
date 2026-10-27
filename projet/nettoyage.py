"""03 — Normaliser, vérifier, puis distinguer rejets et doublons."""
from datetime import date
from decimal import Decimal, InvalidOperation
from lecture import DATA, OUTPUTS, catalogues, ecrire_csv, lire_csv

CHAMPS_SOURCE = ["sale_id", "date", "shop_id", "product_id", "quantity", "unit_price_tnd"]
CHAMPS_VENTES = CHAMPS_SOURCE + ["unit_price_millimes", "amount_millimes"]


def nettoyer(lignes, produits, boutiques):
    # TODO — mission 03 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter nettoyage.py : nettoyer.")


def main():
    produits, boutiques = catalogues()
    retenues, rejets, doublons = nettoyer(lire_csv(DATA / "ventes_initiales.csv"), produits, boutiques)
    ecrire_csv(OUTPUTS / "ventes_nettoyees.csv", retenues, CHAMPS_VENTES)
    ecrire_csv(OUTPUTS / "rejets.csv", rejets, CHAMPS_SOURCE + ["motif"])
    ecrire_csv(OUTPUTS / "doublons.csv", doublons, CHAMPS_VENTES)
    print(f"Qualité : {len(retenues)} retenues, {len(rejets)} rejets, {len(doublons)} doublon(s).")
    print("Journaux et ventes enregistrés dans outputs/.")


if __name__ == "__main__":
    main()
