def afficher_tnd(millimes):
    dinars = millimes // 1000
    reste = millimes % 1000
    return f"{dinars}.{reste:03d}"

print(afficher_tnd(115500))
