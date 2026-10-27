"""01 — Calculer des ventes en millimes, sans arrondis flottants."""


def calculer_total(ventes):
    # TODO — mission 01 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter calcul.py : calculer_total.")


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
