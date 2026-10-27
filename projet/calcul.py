"""Premier calcul local : 2 carnets à 4,500 TND."""

def montant(quantity, unit_price_millimes):
    return quantity * unit_price_millimes

if __name__ == "__main__":
    print(f"2 × 4500 = {montant(2, 4500)} millimes = 9.000 TND")
