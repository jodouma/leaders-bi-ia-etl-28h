"""Mission 09. Le rapport lit la base réellement présente, pas un chiffre fixé."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import OUTPUTS, build_report, describe

# À VOUS : personnaliser le titre sans annoncer un résultat non démontré.
TITRE_RAPPORT = "Atlas Papeterie — ventes observées"

rapport = OUTPUTS / "rapport_atlas.html"
synthese = build_report(OUTPUTS / "atlas.sqlite", rapport, TITRE_RAPPORT)
print(describe(synthese))
print("Rapport :", rapport)
print("Dans l'Explorateur Windows, ouvrir ce HTML avec le navigateur.")
print("Après un nouveau calcul, actualiser le navigateur avec Ctrl+R.")
print("Les CSV d'agrégats sont à côté du rapport, dans outputs/.")
print("Question : ventes élevées signifie-t-il stock suffisant ou marge élevée ?")
