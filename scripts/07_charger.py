"""Mission 07. Charger les dimensions avant les ventes qui les référencent."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import (OUTPUTS, connect, read_catalogs, read_transformed, load_sales,
                     database_totals, write_json, utc_now, describe)

# À VOUS : exécuter deux fois. Compter les nouvelles lignes et les existantes.
BASE = OUTPUTS / "atlas.sqlite"
produits, boutiques = read_catalogs()
ventes = read_transformed(OUTPUTS / "04" / "ventes_transformees.csv")

# load_sales réalise dans une transaction :
# 1. dimensions produit/boutique/date ; 2. faits et clés étrangères.
# Même identifiant et mêmes valeurs : déjà présent, jamais additionné deux fois.
resultat = load_sales(BASE, ventes, produits, boutiques)
synthese = database_totals(BASE)
print("Nouvelles ventes :", resultat["inserted"])
print("Déjà présentes :", resultat["existing"])
print(describe(synthese))
# Cette requête SQLite cherche des liens vers des dimensions absentes.
# [] signifie qu'aucun lien invalide n'a été trouvé.
connexion = connect(BASE)
try:
    liens_invalides = connexion.execute("PRAGMA foreign_key_check").fetchall()
finally:
    connexion.close()
print("Liens invalides :", liens_invalides)
write_json(OUTPUTS / "07" / "chargement.json", {
    "timestamp_utc": utc_now(), **resultat, **synthese
})
print("Base :", BASE)
print("Un rejeu conserve aussi les ventes ajoutées plus tard à la mission 08.")
