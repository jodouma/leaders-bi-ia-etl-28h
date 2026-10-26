quantite = 2
prix_millimes = 4500
montant = quantite * prix_millimes
if montant >= 9000:
    print("Vente importante")
print(f"{montant / 1000:.3f} TND")
