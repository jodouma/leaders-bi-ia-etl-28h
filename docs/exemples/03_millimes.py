from decimal import Decimal
prix = Decimal("4.500")
prix_millimes = int(prix * 1000)
quantite = 2
montant = quantite * prix_millimes
print(prix_millimes)
print(montant)
