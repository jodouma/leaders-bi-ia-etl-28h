deja_presents = {"S001", "S012"}
recus = ["S012", "S013", "S014"]
for identifiant in recus:
    if identifiant in deja_presents:
        print(identifiant, "deja present")
    else:
        print(identifiant, "nouveau")
        deja_presents.add(identifiant)
print(len(deja_presents))
