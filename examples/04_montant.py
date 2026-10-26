from decimal import Decimal

prix_texte = "4.500"
prix_millimes = int(Decimal(prix_texte) * 1000)
quantite = 2
montant_millimes = quantite * prix_millimes
print(f"{montant_millimes / 1000:.3f} TND")
print(montant_millimes >= 9000)
