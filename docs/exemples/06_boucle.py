quantites = [2, 0, 3]
total = 0
for quantite in quantites:
    if quantite > 0:
        total = total + quantite
    else:
        print("Quantité ignorée :", quantite)
print("Total :", total)
