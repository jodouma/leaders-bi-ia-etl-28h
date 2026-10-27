"""Une ligne devient une vente canonique ; le contrôle du lot est fourni."""
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
import re

CHAMPS_SOURCE = ["sale_id", "date", "shop_id", "product_id", "quantity", "unit_price_tnd"]
CHAMPS_VENTES = ["sale_id", "date", "shop_id", "product_id", "quantity", "unit_price_millimes", "amount_millimes"]


def date_iso(texte):
    texte = str(texte).strip()
    if date.fromisoformat(texte).isoformat() != texte:
        raise ValueError("date attendue YYYY-MM-DD")
    return texte


def entier_positif(texte):
    texte = str(texte).strip()
    if not re.fullmatch(r"[0-9]+", texte) or int(texte) <= 0:
        raise ValueError("quantité entière strictement positive attendue")
    return int(texte)


def millimes(texte):
    try:
        prix = Decimal(str(texte).strip())
        if not prix.is_finite() or prix <= 0:
            raise ValueError("prix fini strictement positif attendu")
        # Assez de précision pour ne jamais arrondir silencieusement un long texte.
        with localcontext() as contexte:
            contexte.prec = max(28, len(prix.as_tuple().digits) + 4)
            valeur = prix * 1000
        if valeur != valeur.to_integral_value():
            raise ValueError("prix non représentable en millimes sans arrondi")
        return int(valeur)
    except InvalidOperation as erreur:
        raise ValueError("prix décimal invalide") from erreur


def normaliser_vente(ligne):
    # TODO 02 : strip/upper sur sale_id, shop_id, product_id ; vérifier non vides.
    # Utiliser date_iso, entier_positif et millimes. Ne pas utiliser float.
    # Renvoyer CHAMPS_VENTES : amount_millimes = quantity * unit_price_millimes.
    raise NotImplementedError("Compléter nettoyage.normaliser_vente")


def nettoyer(lignes, produits, boutiques):
    retenues, rejets, doublons, vus = [], [], [], {}
    for numero, ligne in enumerate(lignes, 2):
        try:
            vente = normaliser_vente(ligne)
            if vente["product_id"] not in produits or vente["shop_id"] not in boutiques:
                raise ValueError("produit ou boutique absent du catalogue")
        except (ValueError, KeyError, TypeError) as erreur:
            rejets.append({"line": numero, "source": dict(ligne), "reason": str(erreur)})
            continue
        identifiant = vente["sale_id"]
        if identifiant in vus:
            if vente != vus[identifiant]:
                raise ValueError(f"Conflit dans le lot : {identifiant}")
            doublons.append(vente)
        else:
            vus[identifiant] = vente
            retenues.append(vente)
    return retenues, rejets, doublons
