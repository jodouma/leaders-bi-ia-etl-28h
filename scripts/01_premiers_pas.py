"""Mission 01. Ouvrir ce fichier dans Thonny, puis F5 (Exécuter)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import OUTPUTS, money

# À VOUS : prévoir le résultat, puis changer seulement QUANTITE en 3.
QUANTITE = 2
PRIX_MILLIMES = 4500

# 1 TND = 1000 millimes. 2 carnets à 4.500 TND : 9.000 TND.
montant_millimes = QUANTITE * PRIX_MILLIMES
message = f"{QUANTITE} carnets : {money(montant_millimes)} TND"
print(message)

# Sauvegarder une trace : le script ne modifie pas les données d'entrée.
dossier = OUTPUTS / "01"
dossier.mkdir(parents=True, exist_ok=True)
(dossier / "mon_calcul.txt").write_text(message + "\n", encoding="utf-8")
print("Trace :", dossier / "mon_calcul.txt")
