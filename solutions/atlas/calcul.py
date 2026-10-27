"""01 — Calculer des ventes en millimes, sans arrondis flottants."""


def calculer_total(ventes):
    """Additionner quantité × prix unitaire pour chaque vente."""
    total = 0
    for vente in ventes:
        quantite = vente["quantity"]
        prix = vente["unit_price_millimes"]
        if type(quantite) is not int or type(prix) is not int:
            raise ValueError("Quantité et prix doivent être des entiers.")
        if quantite <= 0 or prix <= 0:
            raise ValueError("Quantité et prix doivent être positifs.")
        total += quantite * prix
    return total


def main():
    ventes = [
        {"quantity": 2, "unit_price_millimes": 4500},
        {"quantity": 3, "unit_price_millimes": 1500},
    ]
    print(f"Panier : {calculer_total(ventes) / 1000:.3f} TND")
    ventes[0]["quantity"] = 3
    print(f"Variation : {calculer_total(ventes) / 1000:.3f} TND")


if __name__ == "__main__":
    main()
