#!/usr/bin/env python3
"""Schémas conceptuels V7 — édition « Solen BI 22 h ».

Produit, pour chaque schéma, un SVG 1600 px (glyphes en contours, aucune police requise
à l'affichage) et un PNG 2400 px, dessinés à partir des mêmes coordonnées.
Contrôles automatiques à chaque génération :
  * texte jamais hors de son cadre (largeurs calculées depuis les métriques des polices) ;
  * aucun texte qui en chevauche un autre, ni traversé par une flèche ou un trait ;
  * contraste WCAG ≥ 4,5:1 entre chaque texte et le fond sur lequel il est posé ;
  * PNG d'au moins 2400 px de large.
Chiffres de chargement : lus dans authoring/generateurs/v7-data.json s'il existe,
sinon affichés « n » (aucun chiffre inventé).

Usage : python authoring/visuals/generate.py [--only v7-etoile v7-cles]
"""
from pathlib import Path
import argparse, hashlib, html, json, math

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/diagrams'
FONTS = ROOT / 'authoring/assets/fonts'
DATA_PATH = ROOT / 'authoring/generateurs/v7-data.json'

NAVY, DEEP, ORANGE = '#2B3180', '#07152F', '#FF9A3C'
PALE, INK, GREY, WHITE = '#F3F5FC', '#1A1F4D', '#5A6478', '#FFFFFF'
LINE = '#C9CEE3'  # traits secondaires (graduations), jamais porteurs de sens seuls

W, SCALE = 1600, 1.5          # 1600 px de viewBox → PNG 2400 px
MIN_TEXT = 26                 # plus petite taille de texte autorisée (px viewBox)
MIN_CONTRAST = 4.5

parser = argparse.ArgumentParser()
parser.add_argument('--only', nargs='+', help='Ne réécrire que ces schémas (le manifeste et la planche restent complets).')
args = parser.parse_args()
SELECTED = set(args.only or [])

FONT_FILES = {'body': 'Inter-400.ttf', 'bold': 'Inter-700.ttf', 'title': 'PlusJakartaSans-800.ttf'}
FONT = {k: TTFont(FONTS / v) for k, v in FONT_FILES.items()}
CMAP = {k: f.getBestCmap() for k, f in FONT.items()}
UPM = {k: f['head'].unitsPerEm for k, f in FONT.items()}
GLYPHS = {k: f.getGlyphSet() for k, f in FONT.items()}
_PIL_FONTS, _PATHS = {}, {}


def text_width(txt, size, weight='body'):
    cmap, hmtx = CMAP[weight], FONT[weight]['hmtx']
    missing = [ch for ch in txt if ord(ch) not in cmap]
    assert not missing, f'glyphe absent de {FONT_FILES[weight]} : {missing!r} dans {txt!r}'
    return sum(hmtx[cmap[ord(ch)]][0] for ch in txt) * size / UPM[weight]


def wrap(txt, size, weight, maxw):
    """Retour à la ligne sur les espaces ; échoue si un mot seul dépasse."""
    out = []
    for para in txt.split('\n'):
        cur = ''
        for word in para.split(' '):
            cand = (cur + ' ' + word) if cur else word
            if cur and text_width(cand, size, weight) > maxw:
                out.append(cur); cur = word
            else:
                cur = cand
        out.append(cur)
    for line in out:
        assert text_width(line, size, weight) <= maxw + 0.01, f'mot trop long pour {maxw:.0f}px : {line!r}'
    return out


def luminance(hexcol):
    rgb = [int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Canvas:
    def __init__(self, name, title, desc, height):
        self.name, self.title, self.desc, self.h, self.h0 = name, title, desc, height, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">'
                      f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>'
                      f'<rect width="{W}" height="{height}" fill="{WHITE}"/>']
        self.img = Image.new('RGB', (round(W * SCALE), round(height * SCALE)), WHITE)
        self.dr = ImageDraw.Draw(self.img)
        self.texts, self.rects, self.segments = [], [], []

    # --- primitives -------------------------------------------------------
    def _s(self, *v):
        return tuple(round(a * SCALE) for a in v)

    def rect(self, x, y, w, h, fill=PALE, stroke=None, r=18, sw=3, dash=False):
        box = self._s(x, y, x + w, y + h)
        if fill or stroke:
            self.dr.rounded_rectangle(box, radius=round(r * SCALE), fill=fill,
                                      outline=None if dash else stroke, width=round(sw * SCALE))
        if stroke and dash:  # contour pointillé (raster)
            pts = [(x + r, y), (x + w - r, y)], [(x + w, y + r), (x + w, y + h - r)], [(x + w - r, y + h), (x + r, y + h)], [(x, y + h - r), (x, y + r)]
            for (a, b) in pts:
                self._dash_raster(*a, *b, stroke, sw)
        attrs = f' fill="{fill or "none"}"'
        if stroke:
            attrs += f' stroke="{stroke}" stroke-width="{sw}"' + (' stroke-dasharray="12 9"' if dash else '')
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"{attrs}/>')
        self.rects.append((x, y, x + w, y + h, fill))

    def circle(self, cx, cy, rad, fill=ORANGE):
        self.dr.ellipse(self._s(cx - rad, cy - rad, cx + rad, cy + rad), fill=fill)
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{fill}"/>')
        self.rects.append((cx - rad, cy - rad, cx + rad, cy + rad, fill))

    def _dash_raster(self, x1, y1, x2, y2, color, width):
        L = math.hypot(x2 - x1, y2 - y1)
        if L == 0:
            return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        t = 0
        while t < L:
            e = min(t + 12, L)
            self.dr.line(self._s(x1 + ux * t, y1 + uy * t, x1 + ux * e, y1 + uy * e), fill=color, width=round(width * SCALE))
            t += 21

    def line(self, x1, y1, x2, y2, color=NAVY, width=4, dash=False, crosses_text=False):
        if dash:
            self._dash_raster(x1, y1, x2, y2, color, width)
        else:
            self.dr.line(self._s(x1, y1, x2, y2), fill=color, width=round(width * SCALE))
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"'
                          + (' stroke-dasharray="12 9"' if dash else '') + '/>')
        if not crosses_text:
            self.segments.append((x1, y1, x2, y2))

    def arrow(self, *pts, color=NAVY, width=4, dash=False, head=18, both=False):
        """Flèche (éventuellement coudée) : arrow((x1,y1),(x2,y2),...)."""
        pts = [tuple(p) for p in pts]
        segs = list(zip(pts, pts[1:]))
        for i, (a, b) in enumerate(segs):
            # raccourcir le dernier segment pour que le trait ne dépasse pas la pointe
            bx, by = b
            if i == len(segs) - 1:
                L = math.hypot(b[0] - a[0], b[1] - a[1]); k = (L - head * 0.6) / L
                bx, by = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
            ax, ay = a
            if both and i == 0:
                L = math.hypot(b[0] - a[0], b[1] - a[1]); k = head * 0.6 / L
                ax, ay = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
            self.line(ax, ay, bx, by, color, width, dash)
        self._head(segs[-1][0], segs[-1][1], color, head)
        if both:
            self._head(segs[0][1], segs[0][0], color, head)

    def _head(self, a, b, color, size):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p = [b, (b[0] - size * math.cos(ang - .45), b[1] - size * math.sin(ang - .45)),
             (b[0] - size * math.cos(ang + .45), b[1] - size * math.sin(ang + .45))]
        self.dr.polygon([self._s(*q) for q in p], fill=color)
        self.parts.append(f'<polygon fill="{color}" points="' + ' '.join(f'{q[0]:.1f},{q[1]:.1f}' for q in p) + '"/>')

    def text(self, x, y, txt, size=28, color=INK, weight='body', anchor='start'):
        assert size >= MIN_TEXT, (self.name, txt, size)
        w = text_width(txt, size, weight)
        x0 = x - w / 2 if anchor == 'middle' else x - w if anchor == 'end' else x
        self.texts.append((x0, y - 0.80 * size, x0 + w, y + 0.22 * size, txt, color))
        key = (weight, round(size * SCALE))
        if key not in _PIL_FONTS:
            _PIL_FONTS[key] = ImageFont.truetype(str(FONTS / FONT_FILES[weight]), key[1])
        pf, cmap, hmtx, sc = _PIL_FONTS[key], CMAP[weight], FONT[weight]['hmtx'], size / UPM[weight]
        cx = x0
        for ch in txt:  # même chasse que le SVG, caractère par caractère
            if ch != ' ':
                self.dr.text((round(cx * SCALE), round(y * SCALE)), ch, font=pf, fill=color, anchor='ls')
            cx += hmtx[cmap[ord(ch)]][0] * sc
        self.parts.append(f'<g aria-label="{html.escape(txt, quote=True)}" fill="{color}" transform="translate({x0:.2f},{y}) scale({sc:.7f},{-sc:.7f})">')
        cur = 0
        for ch in txt:
            g = cmap[ord(ch)]
            if (weight, g) not in _PATHS:
                pen = SVGPathPen(GLYPHS[weight]); GLYPHS[weight][g].draw(pen); _PATHS[(weight, g)] = pen.getCommands()
            if _PATHS[(weight, g)]:
                self.parts.append(f'<path transform="translate({cur},0)" d="{_PATHS[(weight, g)]}"/>')
            cur += hmtx[g][0]
        self.parts.append('</g>')
        return w

    def para(self, x, y, txt, size=28, color=INK, weight='body', maxw=600, gap=None, anchor='start'):
        gap = gap or round(size * 1.38)
        lines = wrap(txt, size, weight, maxw)
        for i, l in enumerate(lines):
            self.text(x, y + i * gap, l, size, color, weight, anchor)
        return y + (len(lines) - 1) * gap

    def heading(self, title, sub):
        self.rect(40, 32, 12, 70, ORANGE, r=6)
        assert text_width(title, 44, 'title') <= 1480, title
        self.text(76, 72, title, 44, DEEP, 'title')
        self.text(76, 122, sub, 29, GREY)

    # --- validation -------------------------------------------------------
    def validate(self):
        errs = []
        for t in self.texts:
            x0, y0, x1, y1, s, col = t
            if x0 < 20 or x1 > W - 20 or y0 < 10 or y1 > self.h - 10:
                errs.append(('hors canevas', s))
            # cadre : texte entièrement dedans ou entièrement dehors
            bg = WHITE
            for (rx0, ry0, rx1, ry1, fill) in self.rects:
                inter = not (x1 <= rx0 or x0 >= rx1 or y1 <= ry0 or y0 >= ry1)
                inside = x0 >= rx0 + 2 and x1 <= rx1 - 2 and y0 >= ry0 + 1 and y1 <= ry1 - 1
                if inter and not inside:
                    errs.append(('déborde du cadre', s, (rx0, ry0, rx1, ry1)))
                if inside and fill:
                    bg = fill
            cr = contrast(col, bg)
            if cr < MIN_CONTRAST:
                errs.append(('contraste %.2f' % cr, s, col, bg))
            for (ax, ay, bx, by) in self.segments:
                if seg_hits_box(ax, ay, bx, by, x0 + 1, y0 + 1, x1 - 1, y1 - 1):
                    errs.append(('trait sur texte', s))
        for i, a in enumerate(self.texts):
            for b in self.texts[i + 1:]:
                if not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3]):
                    errs.append(('chevauchement', a[4], b[4]))
        assert not errs, (self.name, errs)

    def finish(self):
        if self.h != self.h0:  # hauteur ajustée au contenu
            self.parts[0] = self.parts[0].replace(f'height="{self.h0}"', f'height="{self.h}"').replace(f'0 0 {W} {self.h0}', f'0 0 {W} {self.h}')
            self.img = self.img.crop((0, 0, self.img.width, round(self.h * SCALE)))
        self.validate()
        assert self.img.width >= 2400
        svg_path, png_path = OUT / f'{self.name}.svg', OUT / f'{self.name}.png'
        if not SELECTED or self.name in SELECTED:
            svg_path.write_text(''.join(self.parts) + '</svg>', encoding='utf-8')
            self.img.save(png_path, optimize=True)
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        return {'id': self.name, 'title': self.title, 'description': self.desc, 'alt': self.desc,
                'svg': f'docs/images/diagrams/{self.name}.svg', 'png': f'docs/images/diagrams/{self.name}.png',
                'viewbox': [W, self.h], 'png_pixels': [self.img.width, self.img.height],
                'text_min_px': min(round(t[3] - t[1]) for t in self.texts) and MIN_TEXT,
                'sha256': {'svg': sha(svg_path), 'png': sha(png_path)}}


def seg_hits_box(x1, y1, x2, y2, bx0, by0, bx1, by1):
    """Liang–Barsky : le segment coupe-t-il le rectangle ?"""
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


# --- composants ----------------------------------------------------------------
STYLES = {  # fond, contour, titre, corps
    'pale': (PALE, None, NAVY, INK),
    'dark': (DEEP, None, WHITE, WHITE),
    'navy': (NAVY, None, WHITE, WHITE),
    'white': (WHITE, NAVY, NAVY, INK),
    'warn': (WHITE, ORANGE, DEEP, INK),
    'orange': (ORANGE, None, DEEP, DEEP),
}


def box(c, x, y, w, h, title=None, body=(), style='pale', tsize=31, bsize=27, pad=24, align='start', dash=False, valign='top'):
    """Carte avec titre et corps ; vérifie que tout tient dans la hauteur."""
    fill, stroke, tcol, bcol = STYLES[style]
    c.rect(x, y, w, h, fill, stroke, dash=dash)
    maxw = w - 2 * pad
    items = []  # (ligne, taille, graisse, couleur, avance)
    if title:
        for l in wrap(title, tsize, 'bold', maxw):
            items.append((l, tsize, 'bold', tcol, round(tsize * 1.28)))
        items[-1] = items[-1][:4] + (round(tsize * 1.28) + round(bsize * 0.35),)
    for b in body:
        if isinstance(b, tuple):
            txt, weight = b
        else:
            txt, weight = b, 'body'
        col = tcol if weight == 'bold' else bcol
        lines = wrap(txt, bsize, weight, maxw)
        for i, l in enumerate(lines):
            items.append((l, bsize, weight, col, round(bsize * 1.36) + (round(bsize * 0.3) if i == len(lines) - 1 else 0)))
    if not items:
        return y
    total = sum(it[4] for it in items[:-1]) + items[-1][1] * 1.02
    first = items[0][1]
    if valign == 'middle':
        yy = y + (h - total) / 2 + first * 0.80
    else:
        yy = y + pad + first * 0.80
    assert yy - first * 0.8 + total <= y + h - pad * 0.55, (c.name, title, 'contenu trop haut', total, h)
    tx = x + w / 2 if align == 'middle' else x + pad
    for (l, s, wgt, col, adv) in items:
        c.text(tx, yy, l, s, col, wgt, 'middle' if align == 'middle' else 'start')
        yy += adv
    return yy


def badge(c, cx, cy, label, rad=26, size=27, fill=ORANGE, color=DEEP):
    c.circle(cx, cy, rad, fill)
    c.text(cx, cy + size * 0.36, label, size, color, 'bold', 'middle')


def pill(c, x, y, label, size=26, fill=ORANGE, color=DEEP, weight='bold', padx=16, h=None):
    h = h or round(size * 1.6)
    w = text_width(label, size, weight) + 2 * padx
    c.rect(x, y, w, h, fill, r=h / 2)
    c.text(x + padx, y + h / 2 + size * 0.36, label, size, color, weight)
    return w


def table(c, x, y, colw, header, rows, size=26, hsize=26, pad=14, styles=None, spans=None, gap=3, line=None):
    """Tableau sans grille : cellules pleines séparées par un liseré blanc.
    styles[(r, k)] = (fond, couleur, graisse) ; spans[(r, k)] = nombre de lignes fusionnées."""
    styles, spans = styles or {}, spans or {}
    line = line or round(size * 1.3)
    hl = [wrap(h, hsize, 'bold', cw - 2 * pad) for h, cw in zip(header, colw)]
    hh = max(len(l) for l in hl) * round(hsize * 1.3) + 2 * pad - round(hsize * 0.3)
    cells, heights = [], []
    covered = set()
    for r, row in enumerate(rows):
        cl, hmax = [], 0
        for k, (val, cw) in enumerate(zip(row, colw)):
            if (r, k) in covered or val is None:
                cl.append(None); continue
            wgt = styles.get((r, k), (None, None, 'body'))[2]
            lines = wrap(str(val), size, wgt, cw - 2 * pad)
            cl.append(lines)
            for s in range(1, spans.get((r, k), 1)):
                covered.add((r + s, k))
            if spans.get((r, k), 1) == 1:
                hmax = max(hmax, len(lines))
        cells.append(cl)
        heights.append(max(hmax, 1) * line + 2 * pad - round(size * 0.3))
    cx = [x + sum(colw[:k]) for k in range(len(colw))]
    for k, cw in enumerate(colw):
        c.rect(cx[k], y, cw - gap, hh - gap, NAVY, r=4)
        for i, l in enumerate(hl[k]):
            c.text(cx[k] + pad, y + pad + hsize * 0.8 + i * round(hsize * 1.3), l, hsize, WHITE, 'bold')
    ry = [y + hh + sum(heights[:r]) for r in range(len(rows))]
    for r, cl in enumerate(cells):
        for k, lines in enumerate(cl):
            if lines is None:
                continue
            span = spans.get((r, k), 1)
            hgt = sum(heights[r:r + span])
            fill, col, wgt = styles.get((r, k), (None, None, 'body'))
            fill = fill or (PALE if r % 2 == 0 else WHITE)
            col = col or INK
            c.rect(cx[k], ry[r], colw[k] - gap, hgt - gap, fill, r=4)
            block = (len(lines) - 1) * line + size
            top = ry[r] + pad if span == 1 else ry[r] + (hgt - block) / 2
            assert len(lines) * line <= hgt, (c.name, lines)
            for i, l in enumerate(lines):
                c.text(cx[k] + pad, top + size * 0.8 + i * line, l, size, col, wgt)
    return y + hh + sum(heights)


def note(c, y, txt, size=28, color=GREY, weight='body'):
    for i, l in enumerate(wrap(txt, size, weight, 1500)):
        c.text(W / 2, y + i * round(size * 1.38), l, size, color, weight, 'middle')


def band(c, y, h, txt, size=29, style='pale', weight='bold'):
    fill, stroke, tcol, bcol = STYLES[style]
    c.rect(40, y, 1520, h, fill, stroke)
    lines = wrap(txt, size, weight, 1460)
    gap = round(size * 1.36)
    yy = y + h / 2 - (len(lines) - 1) * gap / 2 + size * 0.34
    for i, l in enumerate(lines):
        c.text(W / 2, yy + i * gap, l, size, tcol if weight == 'bold' else bcol, weight, 'middle')


# --- données de chargement (facultatives) ---------------------------------------
DATA = json.loads(DATA_PATH.read_text(encoding='utf-8')) if DATA_PATH.exists() else None
PLACEHOLDERS = []


def _compteurs_reference():
    """Compteurs de chargement lus dans les fichiers de référence du tronc commun (oracle du générateur)."""
    ref = ROOT / 'modele-binome/tronc-commun/reference'
    try:
        l1 = json.loads((ref / 'attendu_lot1.json').read_text(encoding='utf-8'))
        l2 = json.loads((ref / 'attendu_lot2.json').read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    n1, n2 = l1['nettoyage']['ventes.csv'], l2['nettoyage']['ventes.csv']
    return {'lot1': {'lues': l1['sources']['ventes.csv']['lignes'], 'inserees': n1['lignes_acceptees_nouvelles'],
                     'rejets': l1['rejets']['total'], 'faits': l1['tables']['fact_vente']},
            'lot2': {'lues': l2['sources']['ventes.csv']['lignes'], 'nouvelles': l2['increment']['fact_vente_ajoutees'],
                     'deja_connues': n2['deja_charges'], 'rejets': l2['rejets']['total'], 'faits': l2['tables']['fact_vente']},
            'rejeu': {'lues': l2['sources']['ventes.csv']['lignes'], 'inserees': l2['rejeu']['lignes_ajoutees'], 'faits': l2['tables']['fact_vente']}}


COMPTEURS = _compteurs_reference()


def counter(*path, default='n'):
    """Valeur numérique depuis les fichiers de référence (clé <lot>.<compteur>), sinon « n »."""
    node = COMPTEURS
    for p in path:
        node = node.get(p) if isinstance(node, dict) else None
    if isinstance(node, bool) or not isinstance(node, int):
        PLACEHOLDERS.append('.'.join(path)) if default == 'n' else None
        return default
    return f'{node:,}'.replace(',', '\u202f')


ASSETS = []


def start(name, title, sub, h, desc):
    c = Canvas('v7-' + name, title, desc, h)
    c.heading(title, sub)
    return c


def save(c):
    ASSETS.append(c.finish())


OUT.mkdir(parents=True, exist_ok=True)

# 1 ─ direction → décision ---------------------------------------------------------
c = start('direction-decision', 'De la question de la direction à la décision',
          'Exemple Solen : « les ventes montent, mais où passe la marge ? »', 820,
          "Chaîne en cinq étapes : la direction pose une question, on la traduit en question métier, on choisit les données, "
          "on calcule un indicateur défini, puis la direction décide. Exemple Solen Digital : « les ventes montent, mais où passe la marge ? ».")
steps = [('Direction', ['Mme Ben Salah écrit : « les ventes montent, mais où passe la marge ? »'], 'dark'),
         ('Question métier', ['Quelles boutiques et quels produits perdent de la marge, et depuis quand ?'], 'pale'),
         ('Données', ['Tickets (CSV), catalogue (Excel), boutiques (JSON), retours (SQLite)'], 'pale'),
         ('Indicateur', ['Marge sur coût d’achat par boutique et par mois, en TND'], 'pale'),
         ('Décision', ['Revoir prix, stock ou retours là où la marge baisse'], 'navy')]
bw, gp = 268, 45
for i, (t, b, st) in enumerate(steps):
    x = 40 + i * (bw + gp)
    badge(c, x + bw / 2, 196, str(i + 1))
    box(c, x, 240, bw, 400, t, b, st, tsize=30, bsize=27, pad=22)
    if i < 4:
        c.arrow((x + bw + 4, 440), (x + bw + gp - 4, 440))
c.arrow((40 + 4 * (bw + gp) + bw / 2, 648), (40 + 4 * (bw + gp) + bw / 2, 690), (40 + bw + gp + bw / 2, 690), (40 + bw + gp + bw / 2, 648), dash=True)
c.text(800, 732, 'Si l’indicateur ne répond pas à la question, on revient à la question métier.', 28, NAVY, 'bold', 'middle')
note(c, 782, 'Chaque étape se justifie par la précédente : pas de graphique sans question, pas de décision sans indicateur défini.', 26)
save(c)

# 2 ─ Codex propose, l'étudiant contrôle ------------------------------------------------
c = start('codex-controle', 'Codex propose et les humains décident',
          'Aucun code tapé à la main ; chaque changement passe par trois regards avant main.', 800,
          "Quatre rôles en chaîne : Codex propose du code dans une branche ; l'étudiant contrôle en lisant le diff et en lançant les contrôles ; "
          "le binôme relit avec une revue Codex en lecture seule puis une revue humaine ; l'équipe livre après CI verte et approbation. "
          "Un écart renvoie à une demande plus précise.")
cols = [('CODEX', 'Codex propose', ['Code, tests et explication, dans une branche.'], 'pale'),
        ('ÉTUDIANT AUTEUR', 'L’étudiant contrôle', ['Lit le diff.', 'Lance verifier et pytest.', 'Compare à la référence.'], 'dark'),
        ('BINÔME', 'Le binôme relit', ['Revue Codex en lecture seule.', 'Puis revue humaine écrite.'], 'white'),
        ('ÉQUIPE', 'L’équipe livre', ['CI verte, approbation, fusion dans main.'], 'navy')]
bw, gp = 335, 60
for i, (role, t, b, st) in enumerate(cols):
    x = 40 + i * (bw + gp)
    c.text(x + 4, 196, role, 26, GREY, 'bold')
    box(c, x, 220, bw, 330, t, b, st, tsize=31, bsize=27)
    if i < 3:
        c.arrow((x + bw + 6, 385), (x + bw + gp - 6, 385))
x1c, x2c, x3c = 40 + bw / 2, 40 + (bw + gp) + bw / 2, 40 + 2 * (bw + gp) + bw / 2
c.arrow((x3c, 558), (x3c, 610), (x1c, 610), (x1c, 558), dash=True)
c.line(x2c, 558, x2c, 610, dash=True)
c.text(800, 652, 'Contrôle rouge ou écart trouvé : retour à Codex avec une demande plus précise.', 28, NAVY, 'bold', 'middle')
band(c, 690, 80, 'Codex écrit le code ; vous décidez de ce qui entre dans main, et vous savez l’expliquer.', 28)
save(c)

# 3 ─ trois emplacements -----------------------------------------------------------------
c = start('trois-emplacements', 'Trois emplacements pour un même dépôt',
          'Deux copies locales et une copie partagée : tout échange passe par GitHub.', 960,
          "Mon ordinateur et l'ordinateur du binôme ont chacun une copie locale du dépôt ; GitHub héberge le dépôt du binôme. "
          "commit enregistre localement, push envoie vers GitHub, pull récupère depuis GitHub, la pull request (PR) propose de fusionner une branche dans main.")
box(c, 540, 175, 520, 250, 'GitHub · dépôt du binôme', ['main + branches de travail', 'PR : proposer une branche pour main, la faire relire'], 'dark', tsize=31, bsize=27)
box(c, 40, 560, 420, 250, 'Mon ordinateur', ['Copie locale du dépôt', 'commit : enregistrer une étape ici'], 'pale')
box(c, 1140, 560, 420, 250, 'Ordinateur du binôme', ['Copie locale du dépôt', 'commit : enregistrer une étape ici'], 'pale')
# gauche : push monte, pull descend
c.arrow((170, 552), (170, 260), (532, 260))
c.text(190, 245, 'git push', 27, NAVY, 'bold')
c.arrow((532, 345), (300, 345), (300, 552))
c.text(320, 395, 'git pull', 27, NAVY, 'bold')
# droite (miroir)
c.arrow((1430, 552), (1430, 260), (1068, 260))
c.text(1410, 245, 'git push', 27, NAVY, 'bold', 'end')
c.arrow((1068, 345), (1300, 345), (1300, 552))
c.text(1280, 395, 'git pull', 27, NAVY, 'bold', 'end')
c.text(800, 640, 'Pas de lien direct', 27, GREY, 'bold', 'middle')
c.text(800, 680, 'entre les deux ordinateurs', 27, GREY, anchor='middle')
c.line(500, 720, 1100, 720, GREY, 3, dash=True)
pill(c, 655, 440, 'PR : revue puis fusion', 26, ORANGE, DEEP)
band(c, 845, 80, 'commit = enregistrer chez moi · push = envoyer · pull = récupérer · PR = proposer et faire relire', 27)
save(c)

# 4 ─ cycle PR ---------------------------------------------------------------------------
c = start('cycle-pr', 'Le cycle d’une pull request en boucle',
          'Quinze étapes ; auteur et partenaire échangent leurs rôles à chaque cycle.', 1150,
          "Boucle en quinze étapes : main à jour, branche, demande à Codex, contrôles, lecture du diff, commit, push, PR, "
          "revue Codex en lecture seule par le partenaire, revue humaine, correction, CI verte, approbation, merge, pull par les deux. "
          "Puis le cycle recommence avec les rôles inversés.")
P = [('main à jour', 'git switch main · git pull', 'a'), ('Branche', 'git switch -c', 'a'), ('Demande à Codex', 'petite et précise', 'a'),
     ('Contrôles', 'verifier + pytest', 'a'), ('Lire le diff', 'git diff', 'a'), ('Commit', 'git add · git commit', 'a'),
     ('Push', 'git push -u origin', 'a'), ('PR', 'ouverte sur GitHub', 'g'), ('Revue Codex', 'lecture seule', 'p'),
     ('Revue humaine', 'Files changed', 'p'), ('Correction', 'nouveau commit + push', 'a'), ('CI verte', 'controles.yml', 'g'),
     ('Approbation', 'Approve', 'p'), ('Merge', 'Merge pull request', 'g'), ('Pull', 'les deux : git pull', 'b')]
STY = {'a': 'pale', 'p': 'white', 'g': 'dark', 'b': 'orange'}
bw, bh, gx, x0 = 254, 158, 50, 70
rows_y = [185, 418, 651]
centers = []
for i, (t, sub, who) in enumerate(P):
    r, k = divmod(i, 5)
    col = k if r % 2 == 0 else 4 - k
    x, y = x0 + col * (bw + gx), rows_y[r]
    fill, stroke, tcol, bcol = STYLES[STY[who]]
    c.rect(x, y, bw, bh, fill, stroke)
    bf, bt = (DEEP, WHITE) if who in 'apb' else (ORANGE, DEEP)
    badge(c, x + 34, y + 36, str(i + 1), rad=21, size=26 if i < 9 else 26, fill=bf, color=bt)
    tl = wrap(t, 28, 'bold', bw - 74)
    for j, l in enumerate(tl):
        c.text(x + 64, y + 46 + j * 34, l, 28, tcol, 'bold')
    sl = wrap(sub, 26, 'body', bw - 36)
    yy = y + bh - 22 - (len(sl) - 1) * 33
    for j, l in enumerate(sl):
        c.text(x + 18, yy + j * 33, l, 26, bcol)
    centers.append((x, y))
for i in range(14):
    (xa, ya), (xb, yb) = centers[i], centers[i + 1]
    if ya == yb:
        if xb > xa:
            c.arrow((xa + bw + 5, ya + bh / 2), (xb - 5, yb + bh / 2))
        else:
            c.arrow((xa - 5, ya + bh / 2), (xb + bw + 5, yb + bh / 2))
    else:
        c.arrow((xa + bw / 2, ya + bh + 5), (xb + bw / 2, yb - 5))
xl, yl = centers[14]
xf, yf = centers[0]
c.arrow((xl + bw / 2, yl + bh + 5), (xl + bw / 2, 880), (40, 880), (40, yf + bh / 2), (xf - 5, yf + bh / 2), width=5)
c.text(800, 924, 'Cycle suivant : main à jour, et les rôles d’auteur et de partenaire s’inversent.', 28, NAVY, 'bold', 'middle')
lx = 150
for st, lab in (('pale', 'auteur'), ('white', 'partenaire'), ('dark', 'GitHub'), ('orange', 'les deux')):
    fill, stroke, *_ = STYLES[st]
    c.rect(lx, 972, 40, 40, fill, stroke or (GREY if fill == PALE else None), r=8)
    c.text(lx + 54, 1002, lab, 27, INK)
    lx += 54 + text_width(lab, 27) + 70
note(c, 1072, 'Une correction ajoute un commit sur la même branche ; la PR se met à jour et la CI repart.', 26)
save(c)

# 5 ─ postes WSL / Ubuntu ------------------------------------------------------------------
c = start('postes-wsl', 'Qui fait quoi et sur quel système ?',
          'Codex agit dans Ubuntu ; Power BI Desktop reste sur Windows.', 1060,
          "Parcours Windows : Windows porte l'application Codex, Power BI Desktop et PowerShell ; Ubuntu dans WSL2 contient le dossier ~/solen-bi, "
          "Python, Git et l'agent Codex ; GitHub héberge le dépôt du binôme. Variante Ubuntu natif : tout l'ETL sur Ubuntu, "
          "Power BI Desktop sur un poste Windows qui récupère le dépôt.")
c.rect(40, 165, 1520, 395, WHITE, NAVY)
c.text(70, 213, 'PARCOURS WINDOWS + WSL2', 28, NAVY, 'bold')
box(c, 70, 240, 410, 290, 'Windows', ['Vous : app Codex, Power BI Desktop', 'PowerShell : installer WSL'], 'dark', bsize=27)
box(c, 640, 240, 470, 290, 'Ubuntu dans WSL2', ['Codex agit ici : ~/solen-bi', 'Python 3.11+, .venv, Git', 'Agent Codex : lit, écrit, exécute'], 'pale', bsize=27)
box(c, 1240, 240, 290, 290, 'GitHub', ['Dépôt du binôme', 'PR, revue, CI'], 'white', bsize=27)
c.arrow((486, 350), (634, 350), both=True); c.text(560, 330, 'agent', 26, NAVY, 'bold', 'middle')
c.text(560, 395, 'WSL', 26, NAVY, 'bold', 'middle')
c.arrow((1116, 350), (1234, 350), both=True); c.text(1175, 330, 'push', 26, NAVY, 'bold', 'middle')
c.text(1175, 395, 'pull', 26, NAVY, 'bold', 'middle')
c.rect(40, 590, 1520, 360, WHITE, NAVY)
c.text(70, 638, 'VARIANTE UBUNTU NATIF (24.04 / 26.04)', 28, NAVY, 'bold')
box(c, 70, 665, 610, 255, 'Ubuntu', ['App Codex Linux (preview, .deb)', '~/solen-bi · Python · Git · agent'], 'pale', bsize=27)
box(c, 830, 665, 290, 255, 'GitHub', ['Dépôt du binôme'], 'white', bsize=27)
box(c, 1240, 665, 290, 255, 'Poste Windows', ['Power BI Desktop seulement'], 'dark', bsize=27)
c.arrow((686, 790), (824, 790), both=True); c.text(755, 770, 'push', 26, NAVY, 'bold', 'middle')
c.text(755, 835, 'pull', 26, NAVY, 'bold', 'middle')
c.arrow((1126, 790), (1234, 790)); c.text(1180, 770, 'pull', 26, NAVY, 'bold', 'middle')
note(c, 1010, 'Les fichiers du projet vivent dans Ubuntu (~/solen-bi), jamais dans un dossier Windows synchronisé.', 26)
save(c)

# 6 ─ pipeline -------------------------------------------------------------------------------
c = start('pipeline', 'Des quatre sources au rapport',
          'Les sources restent intactes ; l’ETL écrit l’entrepôt et les rejets.', 1020,
          "Quatre sources (base opérationnelle SQLite des retours, CSV des tickets, Excel du catalogue, JSON des boutiques) alimentent l'ETL : "
          "extraire, nettoyer, harmoniser, dédoublonner, charger les dimensions puis les faits. Les rejets vont dans rejets.csv avec un motif. "
          "L'entrepôt en étoile alimente la mini-application locale et Power BI Desktop.")
c.text(40, 192, 'SOURCES', 26, GREY, 'bold')
srcs = [('SQLite opérationnelle', 'retours'), ('CSV', 'tickets de vente'), ('Excel', 'catalogue, prix, coûts'), ('JSON', 'boutiques et zones')]
for i, (t, b) in enumerate(srcs):
    y = 215 + i * 140
    box(c, 40, y, 340, 118, t, [b], 'pale', tsize=28, bsize=26, pad=20)
    c.arrow((386, y + 59), (474, 285 + i * 120))
c.text(480, 192, 'ETL (code écrit par Codex, contrôlé par vous)', 26, GREY, 'bold')
c.rect(480, 215, 560, 560, DEEP)
etl = ['Extraire', 'Nettoyer', 'Harmoniser', 'Dédoublonner', 'Charger les dimensions', 'puis charger les faits']
for i, t in enumerate(etl):
    y = 240 + i * 86
    badge(c, 530, y + 30, str(i + 1), rad=22, size=26)
    c.text(572, y + 40, t, 29, WHITE, 'bold')
c.arrow((1046, 400), (1124, 400))
box(c, 1130, 215, 430, 330, 'Entrepôt en étoile', ['entrepot.sqlite', 'dim_date · dim_produit', 'dim_boutique (SCD2)', 'fact_vente · fact_retour'], 'white', bsize=27)
c.arrow((1250, 551), (1250, 609)); c.arrow((1440, 551), (1440, 609))
box(c, 1130, 615, 210, 160, 'App locale', ['index.html'], 'pale', tsize=28, bsize=26, pad=18)
box(c, 1360, 615, 200, 160, 'Power BI', ['Desktop'], 'navy', tsize=28, bsize=26, pad=18)
c.arrow((760, 781), (760, 829))
box(c, 480, 835, 560, 110, None, [('outputs/rejets.csv', 'bold'), 'une ligne rejetée = un motif'], 'warn', bsize=27, pad=20)
note(c, 990, 'Montants en millimes entiers dans l’entrepôt ; affichage en TND à 3 décimales.', 26)
save(c)

# 7 ─ étoile -----------------------------------------------------------------------------------
c = start('etoile', 'L’étoile de la mission 00',
          'Trois dimensions partagées, deux tables de faits ; chaque relation va de 1 vers plusieurs.', 1140,
          "Schéma en étoile : dim_date, dim_produit et dim_boutique (SCD2 : boutique_key, boutique_id, zone, valid_from, valid_to) au centre ; "
          "fact_vente (ligne_id, date_key, produit_key, boutique_key, quantite, prix_unitaire_millimes, montant_brut_millimes) à gauche ; "
          "fact_retour (retour_id, date_key, produit_key, boutique_key, quantite, montant_millimes) à droite. Chaque flèche va d'une dimension (1) vers les faits (plusieurs).")
fx, fw, dx, dw, rx = 40, 420, 620, 360, 1140
dims = [('dim_date', ['date_key', 'date · mois · année'], 190, 190),
        ('dim_produit', ['produit_key', 'produit_id · libellé', 'coût d’achat (millimes)'], 420, 230),
        ('dim_boutique · SCD2', ['boutique_key', 'boutique_id · zone', 'valid_from · valid_to'], 690, 230)]
for t, b, y, h in dims:
    box(c, dx, y, dw, h, t, b, 'pale', tsize=30, bsize=27)
box(c, fx, 190, fw, 730, 'fact_vente', ['grain : une ligne de ticket', ('ligne_id', 'bold'), 'date_key', 'produit_key', 'boutique_key', 'quantite',
                                       'prix_unitaire_millimes', 'montant_brut_millimes'], 'dark', tsize=32, bsize=27)
box(c, rx, 190, fw, 730, 'fact_retour', ['grain : une ligne de retour', ('retour_id', 'bold'), 'date_key', 'produit_key', 'boutique_key', 'quantite',
                                        'montant_millimes'], 'dark', tsize=32, bsize=27)
for t, b, y, h in dims:
    ay = y + h / 2
    c.arrow((dx - 6, ay), (fx + fw + 6, ay), width=4)
    c.arrow((dx + dw + 6, ay), (rx - 6, ay), width=4)
    c.text(dx - 22, ay - 14, '1', 28, NAVY, 'bold', 'end')
    c.text(fx + fw + 22, ay - 14, '*', 32, NAVY, 'bold')
    c.text(dx + dw + 22, ay - 14, '1', 28, NAVY, 'bold')
    c.text(rx - 22, ay - 14, '*', 32, NAVY, 'bold', 'end')
note(c, 990, '1 → * : une ligne de dimension décrit plusieurs lignes de fait ; la flèche suit le sens du filtre.', 27, NAVY, 'bold')
note(c, 1040, 'Chaque flèche relie la clé de même nom : date_key, produit_key, boutique_key.', 26)
note(c, 1088, 'Les dimensions sont chargées avant les faits ; les montants sont des millimes entiers.', 26)
save(c)

# 8 ─ clés -----------------------------------------------------------------------------------
c = start('cles', 'Clé métier et clé technique',
          'Une boutique, NBE ; deux versions, donc deux clés techniques.', 960,
          "La clé métier boutique_id = NBE identifie la boutique de Nabeul dans les sources. Dans dim_boutique, la clé technique boutique_key identifie une version : "
          "2 pour Cap Bon (du 2021-05-10 au 2026-07-15 exclu), 4 pour Nord-Est (depuis le 2026-07-15, valid_to NULL). Les faits pointent vers boutique_key.")
box(c, 40, 175, 730, 250, 'Clé métier · boutique_id', ['Vient des sources : NBE = Nabeul.', 'Texte, stable, identique pour toutes les versions.'], 'pale')
box(c, 830, 175, 730, 250, 'Clé technique · boutique_key', ['Créée par l’entrepôt : un entier par version.', 'Les faits pointent vers elle.'], 'dark')
c.text(40, 490, 'dim_boutique : deux lignes pour la même boutique', 28, NAVY, 'bold')
hl = (DEEP, WHITE, 'bold'); ml = (ORANGE, DEEP, 'bold')
end = table(c, 40, 515, [270, 270, 330, 325, 325], ['boutique_key', 'boutique_id', 'zone', 'valid_from', 'valid_to'],
            [['2', 'NBE', 'Cap Bon', '2021-05-10', '2026-07-15'], ['4', 'NBE', 'Nord-Est', '2026-07-15', 'NULL (en cours)']],
            size=29, hsize=27, pad=18, styles={(0, 0): hl, (1, 0): hl, (0, 1): ml, (1, 1): ml})
note(c, end + 50, '2 et 4 : deux versions de NBE · NBE : la même boutique dans les deux lignes', 27, NAVY, 'bold')
band(c, end + 95, 120, 'Une vente du 2026-07-14 porte boutique_key = 2 ; une vente du 2026-07-15 porte boutique_key = 4. Filtrer sur boutique_id = NBE réunit les deux.', 27, 'pale', 'body')
save(c)

# 9 ─ nettoyage -----------------------------------------------------------------------------------
c = start('nettoyage', 'Nettoyer sans toucher aux sources',
          'Six lignes lues : trois acceptées, un doublon ignoré, deux rejets justifiés.', 1500,
          "Avant : six lignes brutes du CSV avec un format décimal 12,500, un doublon exact, un identifiant manquant, un produit inconnu P99, "
          "une date 04/03/2026 et une boutique écrite ' tun '. Après : trois lignes acceptées en millimes entiers, dates ISO et codes en majuscules ; "
          "le doublon est ignoré ; rejets.csv contient deux lignes avec leur motif (id_manquant, cle_inconnue).")
c.text(40, 192, 'AVANT · ventes.csv (source intacte)', 27, NAVY, 'bold')
raw = [['1', 'L001', '2026-03-04', 'P01', 'TUN', '2', '"12,500"', 'virgule décimale'],
       ['2', 'L001', '2026-03-04', 'P01', 'TUN', '2', '"12,500"', 'doublon exact de 1'],
       ['3', '(vide)', '2026-03-04', 'P02', 'TUN', '1', '8.000', 'identifiant manquant'],
       ['4', 'L003', '2026-03-04', 'P99', 'NBE', '1', '5.000', 'produit inconnu'],
       ['5', 'L004', '04/03/2026', 'P02', 'NBE', '3', '8.000', 'date non ISO'],
       ['6', 'L005', '2026-03-05', 'P01', '"  tun "', '1', '12.500', 'espaces et casse']]
hot = {(0, 6), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 1), (3, 3), (4, 2), (5, 4)}
st = {k: (WHITE, DEEP, 'bold') for k in hot}
for r in range(6):
    st[(r, 7)] = (ORANGE, DEEP, 'bold')
end = table(c, 40, 212, [70, 150, 200, 140, 170, 150, 190, 450],
            ['#', 'ligne_id', 'date', 'produit', 'boutique', 'quantite', 'prix (TND)', 'ce qu’on remarque'], raw, size=26, hsize=26, pad=13, styles=st)
c.arrow((420, end + 14), (420, end + 74), width=5)
c.arrow((1300, end + 14), (1300, end + 74), width=5)
y2 = end + 125
c.text(40, y2 - 20, 'APRÈS · lignes acceptées', 27, NAVY, 'bold')
acc = [['L001', '2026-03-04', 'P01', 'TUN', '2', '12500'],
       ['L004', '2026-03-04', 'P02', 'NBE', '3', '8000'],
       ['L005', '2026-03-05', 'P01', 'TUN', '1', '12500']]
st2 = {(0, 5): (DEEP, WHITE, 'bold'), (1, 1): (DEEP, WHITE, 'bold'), (2, 3): (DEEP, WHITE, 'bold')}
end2 = table(c, 40, y2, [140, 200, 140, 160, 150, 210], ['ligne_id', 'date', 'produit', 'boutique', 'quantite', 'prix (millimes)'], acc, size=26, hsize=26, pad=13, styles=st2)
c.text(1060, y2 - 20, 'APRÈS · outputs/rejets.csv', 27, NAVY, 'bold')
rej = [['3', '(vide)', 'id_manquant'], ['4', 'L003', 'cle_inconnue']]
end3 = table(c, 1060, y2, [150, 150, 200], ['ligne', 'ligne_id', 'motif'], rej, size=26, hsize=26, pad=13,
             styles={(0, 2): (ORANGE, DEEP, 'bold'), (1, 2): (ORANGE, DEEP, 'bold')})
box(c, 1060, end3 + 20, 500, 135, None, ['Ligne 2 : doublon exact, une seule occurrence gardée (compté, pas rejeté).'], 'pale', bsize=26, pad=18)
yb = max(end2, end3 + 155) + 40
band(c, yb, 80, '6 lignes lues = 3 acceptées + 1 doublon ignoré + 2 rejets', 30, 'dark')
note(c, yb + 135, 'texte "12,500" → 12,500 TND → 12 500 millimes · 04/03/2026 → 2026-03-04 · "  tun " → TUN', 26)
c.h = yb + 175
save(c)

# 10 ─ chargements -----------------------------------------------------------------------------------
c = start('chargements', 'Charger · compléter · rejouer',
          'Un même entrepôt, trois passages ; le rejeu ne doit rien ajouter.', 940,
          "Chargement initial du lot 1, puis incrément du lot 2 (nouvelles lignes et des lignes déjà connues, ignorées), puis rejeu du lot 2 : "
          "0 insertion et des totaux identiques. Les compteurs viennent de v7-data.json quand il existe ; sinon ils sont notés n.")
L1 = dict(lues=counter('lot1', 'lues'), inserees=counter('lot1', 'inserees'), rejets=counter('lot1', 'rejets'), faits=counter('lot1', 'faits'))
L2 = dict(lues=counter('lot2', 'lues'), nouvelles=counter('lot2', 'nouvelles'), connues=counter('lot2', 'deja_connues'), faits=counter('lot2', 'faits'))
RJ = dict(lues=counter('rejeu', 'lues'), inserees=counter('rejeu', 'inserees', default='0'), faits=counter('rejeu', 'faits'))
cards = [('1 · Chargement initial', 'lot1', [f'{L1["lues"]} lignes lues', f'{L1["inserees"]} faits insérés', f'{L1["rejets"]} rejets'], f'{L1["faits"]} faits', 'pale'),
         ('2 · Incrément', 'lot2', [f'{L2["lues"]} lignes lues', f'{L2["nouvelles"]} nouvelles insérées', f'{L2["connues"]} déjà connues : ignorées'], f'{L2["faits"]} faits', 'dark'),
         ('3 · Rejeu', 'lot2, relancé', [f'{RJ["lues"]} lignes lues', f'{RJ["inserees"]} insertion', 'totaux identiques'], f'{RJ["faits"]} faits', 'white')]
bw, gp = 460, 70
for i, (t, lot, lines, tot, stl) in enumerate(cards):
    x = 40 + i * (bw + gp)
    fill, stroke, tcol, bcol = STYLES[stl]
    c.rect(x, 180, bw, 450, fill, stroke)
    c.text(x + 28, 236, t, 31, tcol, 'bold')
    pill(c, x + 28, 262, lot, 26, ORANGE, DEEP)
    for j, l in enumerate(lines):
        c.text(x + 28, 370 + j * 52, l, 28, bcol)
    c.line(x + 28, 532, x + bw - 28, 532, ORANGE, 3)
    c.text(x + 28, 592, 'dans fact_vente : ' + tot, 30, tcol, 'bold')
    if i < 2:
        c.arrow((x + bw + 8, 405), (x + bw + gp - 8, 405), width=5)
c.text(800, 700, 'faits après lot2 = faits après lot1 + nouvelles insérées', 29, NAVY, 'bold', 'middle')
c.text(800, 750, 'faits après rejeu = faits après lot2', 29, NAVY, 'bold', 'middle')
src = 'Compteurs : modele-binome/tronc-commun/reference/attendu_lot1.json et attendu_lot2.json' if COMPTEURS else 'n = valeur réelle à relever après exécution (aucun chiffre inventé).'
note(c, 815, src, 26)
note(c, 865, 'Clé métier du fait unique (ligne_id) : relancer un lot ne crée jamais de doublon.', 26)
save(c)

# 11 ─ SCD2 frise -----------------------------------------------------------------------------------
c = start('scd2-frise', 'NBE change de zone le 2026-07-15',
          'SCD2 : valid_from inclus, valid_to exclu ; chaque vente prend la version valable à sa date.', 1050,
          "Frise de la boutique NBE : version 1 (boutique_key 2, Cap Bon) sur [2021-05-10, 2026-07-15) ; version 2 (boutique_key 4, Nord-Est) sur [2026-07-15, NULL). "
          "Une vente du 2026-07-14 est rattachée à la version 1, une vente du 2026-07-15 à la version 2. La frontière du 2026-07-15 appartient à la nouvelle version.")
X0, XB, X1 = 70, 960, 1530
box(c, X0, 190, XB - X0 - 6, 150, 'Version 1 · Cap Bon', ['boutique_key = 2'], 'pale', tsize=31, bsize=28)
box(c, XB + 6, 190, X1 - XB - 6, 150, 'Version 2 · Nord-Est', ['boutique_key = 4'], 'dark', tsize=31, bsize=28)
c.line(X0, 430, X1 - 20, 430, NAVY, 5)
c._head((X1 - 40, 430), (X1, 430), NAVY, 20)
c.line(XB, 360, XB, 520, ORANGE, 9)
c.text(X0, 475, '2021-05-10', 28, INK, 'bold')
c.text(X0, 515, 'valid_from (inclus)', 26, GREY)
c.text(XB + 30, 563, '2026-07-15', 32, DEEP, 'bold')
c.text(XB + 30, 603, 'fin de v1 (exclue) = début de v2 (incluse)', 26, NAVY, 'bold')
c.text(X1, 475, 'NULL', 28, INK, 'bold', 'end')
c.text(X1, 515, 'en cours', 26, GREY, anchor='end')
c.text((X0 + XB) / 2, 395, '[2021-05-10, 2026-07-15)', 28, NAVY, 'bold', 'middle')
c.text((XB + X1) / 2, 395, '[2026-07-15, NULL)', 28, NAVY, 'bold', 'middle')
# ventes
sa, sb = XB - 70, XB + 0
c.circle(sa, 430, 13, DEEP); c.circle(XB, 430, 13, DEEP)
box(c, 250, 690, 670, 140, 'Vente du 2026-07-14', ['→ version 1 · Cap Bon · boutique_key 2'], 'white', tsize=29, bsize=27)
box(c, 960, 690, 570, 140, 'Vente du 2026-07-15', ['→ version 2 · Nord-Est · boutique_key 4'], 'white', tsize=29, bsize=27)
c.arrow((sa, 682), (sa, 650), (sa, 452), width=4)
c.arrow((XB, 682), (XB, 448), width=4)
band(c, 870, 90, 'Version valable si : valid_from ≤ date de la vente < valid_to (ou valid_to = NULL)', 29)
note(c, 1010, 'Frise non proportionnelle.', 26)
save(c)

# 12 ─ indicateur et contrôle ------------------------------------------------------------------------------
c = start('indicateur-controle', 'Un chiffre plausible n’est pas un chiffre juste',
          'Ventes nettes avant ou après dédoublonnage : seul un contrôle les distingue.', 940,
          "Deux calculs des ventes nettes : correct, après dédoublonnage ; erreur plausible, avant dédoublonnage, où un doublon compte deux fois et gonfle le total. "
          "Le contrôle qui tranche : le nombre de ligne_id distincts parmi les lignes acceptées doit être égal au nombre de lignes de fact_vente.")
box(c, 40, 180, 720, 300, 'Indicateur correct', ['Ventes nettes = brutes − retours,', 'calculées après dédoublonnage.', 'Chaque ligne de ticket compte une fois.'], 'pale')
box(c, 840, 180, 720, 300, 'Erreur plausible', ['Même formule, calculée avant dédoublonnage.', 'Un doublon compte deux fois : total un peu trop haut, mais crédible.'], 'warn')
c.arrow((400, 488), (400, 560), (640, 560), (640, 600), width=4)
c.arrow((1200, 488), (1200, 560), (960, 560), (960, 600), width=4)
box(c, 300, 606, 1000, 200, 'Le contrôle qui tranche', ['nombre de ligne_id distincts = nombre de lignes de fact_vente'], 'dark', tsize=31, bsize=28, align='middle')
c.text(420, 862, '✓ égalité : pas de doublon compté', 28, NAVY, 'bold', 'middle')
c.text(1180, 862, '✗ écart : des doublons sont comptés', 28, DEEP, 'bold', 'middle')
note(c, 912, 'Avant de croire un total, écrire le contrôle qui le prouverait faux.', 26)
save(c)

# 13 ─ tokens, contexte, effort, quota -------------------------------------------------------------------------
c = start('tokens-contexte', 'Tokens · contexte · effort · quota',
          'Une même demande à Codex, vue sous quatre angles différents.', 1120,
          "Une demande remplit la fenêtre de contexte avec des tokens (morceaux de texte) ; le modèle GPT-6 Luna réfléchit avec un effort choisi "
          "(Light, Medium, High, Extra High ; commencer High) ; chaque tâche consomme une part du quota du compte, à lire dans l'application.")
c.rect(40, 180, 640, 380, WHITE, NAVY)
badge(c, 82, 222, '2', rad=22, size=26)
c.text(116, 232, 'Taille du contexte', 30, NAVY, 'bold')
c.text(70, 280, 'Ce que l’agent garde en vue :', 26, INK)
badge(c, 82, 326, '1', rad=22, size=26)
c.text(116, 336, 'tokens = morceaux de texte', 26, INK, 'bold')
toks = [['les', ' ven', 'tes', ' mon', 'tent'], ['def', ' char', 'ger', '(', 'lot', ')'], ['AGENTS', '.md', ' diff', ' +12']]
for r, row in enumerate(toks):
    x = 70
    for t in row:
        x += pill(c, x, 352 + r * 54, t.strip() or t, 26, PALE, NAVY, 'bold', padx=12, h=44) + 8
c.text(70, 543, 'place restante → limitée', 26, GREY)
c.arrow((688, 370), (752, 370), width=5)
c.rect(760, 180, 470, 380, DEEP)
badge(c, 802, 222, '3', rad=22, size=26, fill=ORANGE)
c.text(836, 232, 'Effort', 30, WHITE, 'bold')
c.text(790, 280, 'Combien GPT-6 Luna réfléchit', 26, WHITE)
for i, (lab, wd) in enumerate([('Light', 150), ('Medium', 220), ('High', 290), ('Extra High', 370)]):
    y = 302 + i * 54
    fill, col = (ORANGE, DEEP) if lab == 'High' else (NAVY, WHITE)
    c.rect(790, y, wd, 44, fill, r=8)
    c.text(806, y + 32, lab, 26, col, 'bold')
c.text(790, 548, 'High : point de départ', 26, ORANGE, 'bold')
c.arrow((1238, 370), (1302, 370), width=5)
box(c, 1310, 180, 250, 380, 'Réponse', ['diff, explication, résultat'], 'pale', tsize=30, bsize=26, pad=22)
c.rect(40, 600, 1520, 150, WHITE, NAVY)
badge(c, 82, 642, '4', rad=22, size=26)
c.text(116, 652, 'Quota du compte : usage permis sur une période, affiché dans l’app', 28, NAVY, 'bold')
for i, wd in enumerate([300, 220, 380]):
    x = 70 + sum([300, 220, 380][:i]) + i * 6
    c.rect(x, 680, wd, 50, NAVY, r=6)
    c.text(x + 16, 714, f'tâche {i + 1}', 26, WHITE, 'bold')
c.rect(70 + 900 + 18, 680, 1530 - (70 + 900 + 18), 50, PALE, r=6)
c.text(1008, 714, 'restant : lire l’indicateur, ne pas deviner', 26, INK)
defs = [('1', 'Tokens', 'Unité de comptage du texte lu et écrit.'),
        ('2', 'Contexte', 'Quantité maximale de texte qu’une tâche garde en vue.'),
        ('3', 'Effort', 'Temps de réflexion choisi pour une demande.'),
        ('4', 'Quota', 'Limite d’usage du compte, indépendante des trois autres.')]
for i, (n, t, b) in enumerate(defs):
    x = 40 + i * 390
    c.rect(x, 790, 350, 230, PALE)
    badge(c, x + 42, 832, n, rad=22, size=26)
    c.text(x + 76, 842, t, 30, NAVY, 'bold')
    c.para(x + 24, 900, b, 26, INK, maxw=302)
note(c, 1075, 'Plus d’effort ou plus de contexte = plus lent et plus d’usage ; jamais une garantie de résultat juste.', 26)
save(c)

# 14 ─ tâche → modèle → effort ------------------------------------------------------------------------------
c = start('tache-modele-effort', 'Quel effort pour quelle tâche ?',
          'Compte Free : un seul modèle annoncé ; seul l’effort change. Commencer High.', 1500,
          "Tableau : pour comprendre, planifier, écrire une petite fonction, intégrer, déboguer et revoir, le modèle accessible est GPT-6 Luna, "
          "le seul annoncé pour Free. L'effort recommandé part de High ; Medium pour une petite fonction bien délimitée, Extra High si un débogage reste bloqué. "
          "Chaque ligne donne la raison et la preuve attendue.")
rows = [['Comprendre', 'GPT-6 Luna\n\nle seul modèle annoncé pour Free\n\n(application de bureau)', 'High', 'Relier plusieurs fichiers et notions', 'Vous l’expliquez sans regarder l’écran'],
        ['Planifier', None, 'High', 'Découper avant d’écrire', 'Plan court avec un contrôle par étape'],
        ['Petite fonction', None, 'Medium ou High', 'Changement petit et bien délimité', 'Diff lu + test qui passe'],
        ['Intégrer', None, 'High', 'Plusieurs modules touchés', 'verifier et pytest verts'],
        ['Déboguer', None, 'High, puis Extra High si bloqué', 'Chercher la cause, pas le symptôme', 'Erreur reproduite, puis disparue'],
        ['Revoir', None, 'High (lecture seule)', 'Trouver ce qui manque ou casse', 'Constats avec fichier et ligne']]
st = {(0, 1): (DEEP, WHITE, 'bold')}
for r in range(6):
    st[(r, 0)] = (PALE if r % 2 == 0 else WHITE, NAVY, 'bold')
    st[(r, 2)] = ((ORANGE, DEEP, 'bold') if rows[r][2] == 'High' else (PALE if r % 2 == 0 else WHITE, DEEP, 'bold'))
end = table(c, 40, 180, [250, 250, 290, 350, 380], ['Tâche', 'Modèle accessible', 'Effort', 'Raison', 'Preuve attendue'], rows,
            size=26, hsize=27, pad=16, styles=st, spans={(0, 1): 6})
band(c, end + 30, 120, 'Efforts visibles dans l’app : Light · Medium · High · Extra High. Light : questions très courtes. Standard est une vitesse, pas un effort.', 27, 'pale', 'body')
note(c, end + 205, 'Ne choisir que ce qui s’affiche sur votre compte Free ; un effort plus haut ne dispense pas de la preuve.', 26)
c.h = end + 245
save(c)

# 15 ─ séances -----------------------------------------------------------------------------------
c = start('seances', 'Cinq séances · une mission · une soutenance',
          'Durées estimées, à confirmer par un essai réel.', 1020,
          "Cinq séances de 4 h avec les épisodes Solen : S1 demande initiale et cadrage, S2 premier résultat faux, S3 anomalies et étoile, "
          "S4 changement de besoin et revue, S5 livraison ; environ 8 h de travail personnel sur la mission du catalogue ; soutenance de 2 h. "
          "22 h en présence, environ 30 h au total.")
S = [('S1', 'Demande initiale et cadrage', 'Preuve : premier cycle PR à deux'),
     ('S2', 'Premier résultat… faux', 'Preuve : rejets.csv conforme'),
     ('S3', 'Anomalies et étoile', 'Preuve : entrepôt + choix de mission'),
     ('S4', 'Changement de besoin et revue', 'Preuve : SCD2, rejeu, CI verte'),
     ('S5', 'Livraison', 'Preuve : app, Power BI, recommandation')]
bw, gp = 280, 30
for i, (s, t, p) in enumerate(S):
    x = 40 + i * (bw + gp)
    stl = 'dark' if i == 4 else 'pale'
    fill, stroke, tcol, bcol = STYLES[stl]
    c.rect(x, 180, bw, 400, fill, stroke)
    pill(c, x + 22, 202, f'{s} · 4 h', 26, ORANGE, DEEP)
    yy = c.para(x + 22, 302, t, 30, tcol, 'bold', maxw=bw - 44, gap=40)
    c.para(x + 22, 470, p, 26, bcol, maxw=bw - 44, gap=36)
box(c, 40, 620, 900, 180, 'Travail personnel ≈ 8 h', ['Lecture 1 h · mission du catalogue 5 h · finition et préparation orale 2 h'], 'white')
box(c, 980, 620, 580, 180, 'Soutenance · 2 h', ['Démo du binôme + questions individuelles'], 'navy')
px = 1520 / 30
x = 40
segs = [(f'S{i + 1}', 4, NAVY, WHITE) for i in range(5)] + [('perso ≈ 8 h', 8, PALE, INK), ('2 h', 2, DEEP, WHITE)]
for lab, hrs, fill, col in segs:
    w = hrs * px
    c.rect(x, 845, w - 4, 56, fill, r=4)
    c.text(x + (w - 4) / 2, 883, lab, 26, col, 'bold', 'middle')
    x += w
note(c, 950, '22 h en présence (5 × 4 h + 2 h) · ≈ 8 h personnel · ≈ 30 h de charge totale · barre à l’échelle des heures', 26)
save(c)

# 16 ─ soutenance -----------------------------------------------------------------------------------
c = start('soutenance', 'Soutenance : 120 minutes à partager',
          '10 min d’accueil + N passages de 100/N min + 10 min de délibération.', 1080,
          "Créneau de 120 minutes : 10 minutes d'accueil, 100 minutes partagées entre N binômes, 10 minutes de délibération. "
          "N = 5 : 20 minutes par binôme (6 démo, 2 × 6 questions individuelles, 2 transition). N = 8 : 12,5 minutes. "
          "N ≥ 11 : 100/11 ≈ 9,1 minutes ou moins, impossible sans second créneau ou deux jurys en parallèle.")
X0, X1 = 340, 1560
px = (X1 - X0) / 120
def tl(y, parts, label, sub, style='pale'):
    box(c, 40, y, 280, 110, label, [sub] if sub else [], style, tsize=30, bsize=26, pad=18, valign='middle')
    x = X0
    for lab, mins, fill, col in parts:
        w = mins * px
        c.rect(x, y + 20, w - 3, 70, fill, r=4)
        if lab:
            c.text(x + (w - 3) / 2, y + 66, lab, 26, col, 'bold', 'middle')
        x += w
tl(185, [('10 min', 10, DEEP, WHITE), ('100 min pour N binômes', 100, NAVY, WHITE), ('10 min', 10, DEEP, WHITE)], '120 min', 'créneau')
c.text(X0, 318, 'accueil', 26, GREY, 'bold')
c.text(X1, 318, 'délibération', 26, GREY, 'bold', 'end')
c.text(800, 375, 'durée par binôme = 100 / N', 34, NAVY, 'bold', 'middle')
def nrow(y, n, label, sub, warnrow=False):
    parts = [('', 10, PALE, INK)]
    for i in range(n):
        lab = ('' if warnrow else ('20 min' if n == 5 else '12,5'))
        parts.append((lab, 100 / n, ORANGE if warnrow else NAVY, DEEP if warnrow else WHITE))
    parts.append(('', 10, PALE, INK))
    tl(y, parts, label, sub, 'warn' if warnrow else 'pale')
nrow(420, 5, 'N = 5', '20 min')
c.text(X0 + 10 * px, 590, '20 min = 6 démo + 2 × 6 questions individuelles + 2 transition', 27, INK)
nrow(630, 8, 'N = 8', '12,5 min')
nrow(800, 11, 'N ≥ 11', '≈ 9 min ou moins', warnrow=True)
c.text(X0 + 10 * px, 968, '100 / 11 ≈ 9,1 min : impossible en un créneau', 28, DEEP, 'bold')
c.text(X0 + 10 * px, 1012, '→ second créneau ou deux jurys en parallèle ; signaler au professeur.', 27, INK)
save(c)

# --- manifeste + planche contact ---------------------------------------------------------------------
for old in list(OUT.glob('v6-*.png')) + list(OUT.glob('v6-*.svg')):
    old.unlink()
sheet_cols, tw, th, lab = 4, 600, 380, 44
rows_n = math.ceil(len(ASSETS) / sheet_cols)
sheet = Image.new('RGB', (sheet_cols * (tw + 20) + 20, rows_n * (th + lab + 20) + 20), '#DDE1ED')
sd = ImageDraw.Draw(sheet)
lf = ImageFont.truetype(str(FONTS / 'Inter-700.ttf'), 22)
for i, a in enumerate(ASSETS):
    im = Image.open(ROOT / a['png']).convert('RGB'); im.thumbnail((tw, th), Image.LANCZOS)
    x = 20 + (i % sheet_cols) * (tw + 20); y = 20 + (i // sheet_cols) * (th + lab + 20)
    sd.rectangle((x, y, x + tw, y + th), fill=WHITE)
    sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
    sd.text((x, y + th + 10), a['id'], font=lf, fill=INK)
sheet_path = OUT / 'v7-contact-sheet.png'
sheet.save(sheet_path, optimize=True)

manifest = {
    'version': 7, 'edition': 'Solen BI 22 h', 'language': 'fr', 'source': 'authoring/visuals/generate.py',
    'palette': {'navy': NAVY, 'deep': DEEP, 'orange': ORANGE, 'pale': PALE, 'ink': INK, 'grey': GREY},
    'fonts': {'Inter': 'authoring/assets/fonts/Inter-OFL.txt', 'Plus Jakarta Sans': 'authoring/assets/fonts/PlusJakartaSans-OFL.txt'},
    'checks': {'text_inside_frames': True, 'no_text_overlap': True, 'no_line_over_text': True,
               'min_contrast_wcag': MIN_CONTRAST, 'min_text_px_viewbox': MIN_TEXT, 'png_min_width': 2400},
    'load_counters': {'data_file': 'authoring/generateurs/v7-data.json', 'present': DATA is not None,
                      'sha256': hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() if DATA else None,
                      'placeholders_n': sorted(set(PLACEHOLDERS))},
    'contact_sheet': {'png': 'docs/images/diagrams/v7-contact-sheet.png', 'sha256': hashlib.sha256(sheet_path.read_bytes()).hexdigest()},
    'license': 'Schémas originaux ; aucune interface simulée, aucune capture, aucun logo tiers. Polices SIL OFL 1.1, glyphes en contours dans les SVG.',
    'assets': ASSETS,
}
(ROOT / 'authoring/visuals/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'{len(ASSETS)} schémas V7 (SVG + PNG 2400 px) + planche contact ; contrôles de texte, chevauchement et contraste passés.'
      + ('' if DATA else f' Compteurs en « n » : {", ".join(sorted(set(PLACEHOLDERS)))}.'))
