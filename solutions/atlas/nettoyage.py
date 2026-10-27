"""03 — Normaliser, vérifier, puis distinguer rejets et doublons."""
from datetime import date
from decimal import Decimal, InvalidOperation
from lecture import DATA, OUTPUTS, catalogues, ecrire_csv, lire_csv

CHAMPS_SOURCE = ["sale_id", "date", "shop_id", "product_id", "quantity", "unit_price_tnd"]
CHAMPS_VENTES = CHAMPS_SOURCE + ["unit_price_millimes", "amount_millimes"]


def normaliser(ligne, produits, boutiques):
    """Valider une vente. Les prix sont lus avec Decimal, puis stockés en entiers."""
    vente = {champ: str(ligne.get(champ, "") or "").strip() for champ in CHAMPS_SOURCE}
    for champ in ("sale_id", "shop_id", "product_id"):
        vente[champ] = vente[champ].upper()
    if not vente["sale_id"]:
        raise ValueError("sale_id manquant")
    jour = date.fromisoformat(vente["date"])
    vente["date"] = jour.isoformat()
    if vente["product_id"] not in produits:
        raise ValueError("produit inconnu")
    if vente["shop_id"] not in boutiques:
        raise ValueError("boutique inconnue")
    quantite = int(vente["quantity"])
    if quantite <= 0:
        raise ValueError("quantité non positive")
    prix = Decimal(vente["unit_price_tnd"].replace(",", "."))
    millimes = prix * 1000
    if not prix.is_finite() or prix <= 0 or millimes != millimes.to_integral_value():
        raise ValueError("prix positif avec au plus trois décimales requis")
    vente["quantity"] = quantite
    vente["unit_price_tnd"] = f"{prix:.3f}"
    vente["unit_price_millimes"] = int(millimes)
    vente["amount_millimes"] = quantite * int(millimes)
    return vente


def nettoyer(lignes, produits, boutiques):
    """Renvoyer retenues, rejets avec motif, doublons. Un ID contradictoire arrête le lot."""
    retenues, rejets, doublons = [], [], []
    vues = {}
    for ligne in lignes:
        try:
            vente = normaliser(ligne, produits, boutiques)
        except (ValueError, InvalidOperation, OverflowError) as erreur:
            rejet = {champ: ligne.get(champ, "") for champ in CHAMPS_SOURCE}
            rejet["motif"] = str(erreur)
            rejets.append(rejet)
            continue
        identifiant = vente["sale_id"]
        if identifiant in vues:
            if vente != vues[identifiant]:
                raise ValueError(f"Conflit sale_id {identifiant} : contenus différents.")
            doublons.append(vente)
        else:
            vues[identifiant] = vente
            retenues.append(vente)
    return retenues, rejets, doublons


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
