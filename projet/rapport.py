"""Preuves ETL locales ; Power BI Desktop reste une manipulation Windows distincte."""
from html import escape
from pathlib import Path
from engine import rapport, exporter


def ecrire_html(resultat, chemin):
    """Vue fournie du même dictionnaire que rapport.json, sans nouvelle requête SQL."""
    def tnd(millimes):
        valeur = int(millimes)
        return f"{valeur // 1000:,}.{valeur % 1000:03d}".replace(",", " ")

    zones = resultat["zone_amounts_millimes"]
    maximum = max(zones.values(), default=1) or 1
    barres = "".join(
        f'<div class="zone"><div class="zone-label"><span>{escape(str(zone))}</span>'
        f'<strong>{tnd(montant)} TND</strong></div><div class="track">'
        f'<div class="bar" style="width:{100 * montant / maximum:.2f}%"></div></div></div>'
        for zone, montant in sorted(zones.items()))
    lignes = "".join(
        f'<tr><td>{escape(str(version).partition("@")[0])}</td>'
        f'<td>{escape(str(version).partition("@")[2])}</td><td>{tnd(montant)}</td></tr>'
        for version, montant in sorted(resultat["shop_version_amounts_millimes"].items()))
    contenu = f'''<!doctype html>
<html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas — preuves ETL</title>
<style>
:root{{color-scheme:light;--ink:#24243b;--muted:#666879;--accent:#6656a2;--line:#dedee7}}
*{{box-sizing:border-box}}body{{margin:0;background:#f4f3ee;color:var(--ink);font:17px/1.5 system-ui,sans-serif}}
main{{max-width:1120px;margin:40px auto;padding:0 28px}}.eyebrow{{font-size:13px;letter-spacing:.16em;font-weight:750;color:var(--accent)}}
h1{{font-size:clamp(30px,5vw,48px);line-height:1.12;letter-spacing:-.04em;margin:14px 0}}p{{color:var(--muted)}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:30px 0}}.card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:23px}}
.kpi strong{{display:block;font-size:38px;line-height:1.2;letter-spacing:-.04em}}.kpi span{{font-size:14px;color:var(--muted)}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}h2{{font-size:20px;margin:0 0 5px}}.note{{font-size:14px;margin:0 0 24px}}
.zone{{margin:24px 0}}.zone-label{{display:flex;justify-content:space-between;gap:15px;font-size:15px}}.track{{height:15px;border-radius:8px;background:#eeedf5;margin-top:10px;overflow:hidden}}.bar{{height:100%;background:var(--accent);border-radius:8px}}
table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:15px}}th,td{{padding:12px 7px;text-align:left;border-bottom:1px solid var(--line)}}th{{font-size:12px;color:var(--muted)}}td:last-child,th:last-child{{text-align:right}}
.status{{margin:25px 0;padding:18px 22px;border-left:5px solid #c18b44;background:#fff6e5;border-radius:6px;font-size:14px}}footer{{font-size:13px;color:var(--muted);padding:0 0 25px}}
@media(max-width:750px){{.columns,.kpis{{grid-template-columns:1fr}}main{{margin-top:25px;padding:0 18px}}}}
</style><main>
<div class="eyebrow">ATLAS PAPETERIE · PREUVES ETL</div>
<h1>Les ventes, avec leur histoire.</h1>
<p>Lecture locale des chiffres calculés dans l’entrepôt SQLite.<br>Un fait représente une ligne de vente ; les montants restent stockés en millimes entiers.</p>
<section class="kpis" aria-label="Indicateurs de ventes">
<div class="card kpi"><strong>{int(resultat["facts"])}</strong><span>lignes de vente</span></div>
<div class="card kpi"><strong>{int(resultat["quantity"])}</strong><span>unités vendues</span></div>
<div class="card kpi"><strong>{tnd(resultat["amount_millimes"])}</strong><span>chiffre d’affaires · TND</span></div>
</section><div class="columns"><section class="card"><h2>Zone commerciale historique</h2>
<p class="note">La zone est celle de la boutique au moment de la vente.</p>{barres}</section>
<section class="card"><h2>Les versions qui portent les ventes</h2><p class="note">{int(resultat["shop_versions"])} versions de boutique dans l’entrepôt. Une nouvelle date de début identifie une nouvelle version.</p>
<table><thead><tr><th>Boutique</th><th>Début de version</th><th>CA · TND</th></tr></thead><tbody>{lignes}</tbody></table>
<p class="note">Seules les versions portant des ventes figurent dans ce tableau.</p></section></div>
<aside class="status"><strong>Preuve ETL locale.</strong> Cette vue aide à contrôler les résultats. Le modèle, les relations et l’actualisation Power BI Desktop restent à réaliser sur Windows.</aside>
<footer>Même résultat que <code>outputs/rapport.json</code> · {int(resultat["products"])} produits · {int(resultat["dates"])} dates de vente · Affichage autonome, sans connexion réseau.</footer>
</main></html>'''
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    return chemin
