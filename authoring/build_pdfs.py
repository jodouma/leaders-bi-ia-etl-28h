"""Rebuild the four student books from their editable JSON sources.

Python 3.10+, reportlab and Pillow. No university skill installation needed.
Run from any folder: python authoring/build_pdfs.py
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ASSETS = HERE / 'assets'
W, H = 595.276, 841.89
LEFT, RIGHT, BOTTOM = 45, 550.276, 62
WIDTH = RIGHT - LEFT
NAVY = colors.HexColor('#2B3180')
DEEP = colors.HexColor('#07152F')
ORANGE = colors.HexColor('#FF9A3C')
PALE = colors.HexColor('#F3F5FC')
INK = colors.HexColor('#1A1F4D')
MUTED = colors.HexColor('#52607B')

for face, filename in [('Inter', 'Inter-400.ttf'), ('InterBold', 'Inter-700.ttf'),
                       ('Jakarta', 'PlusJakartaSans-800.ttf')]:
    pdfmetrics.registerFont(TTFont(face, str(ASSETS / 'fonts' / filename)))
pdfmetrics.registerFontFamily('Inter', normal='Inter', bold='InterBold')

BODY = ParagraphStyle('body', fontName='Inter', fontSize=10.5, leading=14.6,
                      textColor=INK, spaceAfter=0)
SMALL = ParagraphStyle('small', parent=BODY, fontSize=9.5, leading=12.2)
TITLE = ParagraphStyle('title', fontName='Jakarta', fontSize=24, leading=29,
                       textColor=DEEP)
SECTION = ParagraphStyle('section', fontName='InterBold', fontSize=13,
                         leading=17, textColor=NAVY)
WHITE = ParagraphStyle('white', parent=SMALL, textColor=colors.white)


def marked(text):
    """Limited, predictable inline markup, keeping all source text escaped."""
    text = html.escape(str(text))
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    text = re.sub(r'(https?://[^\s<>]+)', r'<link href="\1" color="#2B3180">\1</link>', text)
    return text.replace('\n', '<br/>')


def paragraph(text, style=BODY):
    return Paragraph(marked(text), style)


def measure(block):
    kind = block['type']
    if kind in ('section', 'text'):
        p = paragraph(block['text'], SECTION if kind == 'section' else BODY)
        _, h = p.wrap(WIDTH, 2000)
        return h + (9 if kind == 'section' else 8), p
    if kind == 'bullets':
        items = [paragraph('• ' + str(item)) for item in block['items']]
        return sum(p.wrap(WIDTH-10, 2000)[1] + 5 for p in items) + 3, items
    if kind == 'callout':
        label = paragraph(block.get('label', 'Repère'), SECTION)
        p = paragraph(block['text'])
        height = label.wrap(WIDTH-28, 2000)[1] + p.wrap(WIDTH-28, 2000)[1] + 27
        return height + 9, (label, p, height)
    if kind == 'code':
        text = block['text'].rstrip('\n')
        for line in text.splitlines():
            if pdfmetrics.stringWidth(line, 'Courier', 9.1) > WIDTH-26:
                raise ValueError('Code too wide: ' + line)
        label = block.get('label', block.get('source', 'Python · exemple'))
        height = len(text.splitlines())*12.5 + 43
        return height + 12, (text, label, height)
    if kind == 'table':
        weights = block.get('widths', [1]*len(block['headers']))
        widths = [WIDTH*w/sum(weights) for w in weights]
        values = [[paragraph(v, WHITE) for v in block['headers']]]
        values += [[paragraph(v, SMALL) for v in row] for row in block['rows']]
        t = Table(values, colWidths=widths, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, PALE]),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 9),
            ('RIGHTPADDING', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,-1), (-1,-1), .5, colors.HexColor('#DADEEF')),
        ]))
        _, h = t.wrap(WIDTH, 2000)
        return h + 10, t
    if kind == 'diagram':
        return 96, block['nodes']
    if kind == 'star':
        return 323, None
    if kind in ('figure','image'):
        height = block.get('height', 170)
        return height + 38, block
    raise ValueError('Unsupported block: ' + kind)


def draw_block(c, block, obj, y, height):
    kind = block['type']
    if kind in ('section', 'text'):
        h = obj.wrap(WIDTH, 2000)[1]
        obj.drawOn(c, LEFT, y-h)
    elif kind == 'bullets':
        for p in obj:
            h = p.wrap(WIDTH-10, 2000)[1]
            p.drawOn(c, LEFT+4, y-h)
            y -= h+5
    elif kind == 'callout':
        label, p, boxh = obj
        c.setFillColor(PALE)
        c.roundRect(LEFT, y-boxh, WIDTH, boxh, 11, fill=1, stroke=0)
        h = label.wrap(WIDTH-28, 2000)[1]
        label.drawOn(c, LEFT+14, y-12-h)
        ph = p.wrap(WIDTH-28, 2000)[1]
        p.drawOn(c, LEFT+14, y-18-h-ph)
    elif kind == 'code':
        text, label, boxh = obj
        c.setFillColor(DEEP)
        c.roundRect(LEFT, y-boxh, WIDTH, boxh, 9, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.setFont('InterBold', 8.4)
        c.drawString(LEFT+13, y-16, label)
        t = c.beginText(LEFT+13, y-35)
        t.setFont('Courier', 9.1)
        t.setFillColor(colors.white)
        t.setLeading(12.5)
        for line in text.splitlines():
            t.textLine(line)
        c.drawText(t)
    elif kind == 'table':
        h = obj.wrap(WIDTH, 2000)[1]
        obj.drawOn(c, LEFT, y-h)
    elif kind == 'diagram':
        n = len(obj)
        gap = 15
        boxw = (WIDTH-gap*(n-1))/n
        for i, text in enumerate(obj):
            x = LEFT+i*(boxw+gap)
            c.setFillColor(PALE)
            c.roundRect(x, y-84, boxw, 73, 10, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.circle(x+16,y-15,10,fill=1,stroke=0)
            c.setFillColor(colors.white)
            c.setFont('InterBold',8.8)
            c.drawCentredString(x+16,y-18,str(i+1))
            p = paragraph(text, SMALL)
            h = p.wrap(boxw-16, 2000)[1]
            if h > 51:
                raise ValueError('Diagram label too long: '+text)
            p.drawOn(c,x+8,y-33-h)
            if i<n-1:
                c.setStrokeColor(ORANGE)
                c.setLineWidth(1.5)
                c.line(x+boxw+2,y-50,x+boxw+12,y-50)
                c.line(x+boxw+9,y-47,x+boxw+12,y-50)
                c.line(x+boxw+9,y-53,x+boxw+12,y-50)
    elif kind in ('figure','image'):
        path = HERE/obj['path']
        from PIL import Image
        with Image.open(path) as im:
            iw,ih = im.size
        scale=min(WIDTH/iw, obj.get('height',170)/ih)
        c.drawImage(str(path), LEFT+(WIDTH-iw*scale)/2,y-ih*scale,
                    width=iw*scale,height=ih*scale,mask='auto')
        p=paragraph(obj.get('caption',''),SMALL)
        ph=p.wrap(WIDTH,2000)[1]
        p.drawOn(c,LEFT,y-ih*scale-8-ph)
    elif kind == 'star':
        def card(x, top, width, height, title, lines, dark=False):
            c.setFillColor(DEEP if dark else PALE)
            c.roundRect(x,top-height,width,height,10,fill=1,stroke=0)
            c.setFillColor(ORANGE if dark else NAVY)
            c.setFont('InterBold',10)
            c.drawString(x+11,top-20,title)
            c.setFillColor(colors.white if dark else INK)
            c.setFont('Inter',8.8)
            for i,line in enumerate(lines):
                c.drawString(x+11,top-39-i*13,line)
        # Connectors are drawn first, so they never cover table labels.
        c.setStrokeColor(ORANGE)
        c.setLineWidth(1.5)
        for x1,y1,x2,y2 in [(LEFT+252,y-86,LEFT+252,y-126),
                            (LEFT+142,y-176,LEFT+170,y-176),
                            (LEFT+335,y-176,LEFT+363,y-176)]:
            c.line(x1,y1,x2,y2)
        card(LEFT+170,y-4,165,82,'dim_date',
             ['date_key  [clé]','full_date','year · month · day'])
        card(LEFT,y-126,142,104,'dim_product',
             ['product_key  [clé]','product_id : P01','product_name : Carnet'])
        card(LEFT+363,y-126,142,104,'dim_shop',
             ['shop_key  [clé]','shop_id : NBE','shop_name : Nabeul'])
        card(LEFT+170,y-126,165,156,'fact_sales',
             ['sale_id  [clé]','date_key  [lien]','product_key  [lien]',
              'shop_key  [lien]','quantity','unit_price_millimes',
              'amount_millimes'],True)
        c.setFont('InterBold',8.5)
        c.setFillColor(NAVY)
        for x,dy,value in [(240,97,'1'),(240,119,'N'),
                            (145,165,'1'),(160,165,'N'),
                            (339,165,'N'),(355,165,'1')]:
            c.drawString(LEFT+x,y-dy,value)
        p=paragraph('1 → N : une ligne de dimension peut décrire plusieurs ventes. '
                    'Chaque vente retrouve un seul produit, une seule boutique et une seule date.',SMALL)
        ph=p.wrap(WIDTH,2000)[1]
        p.drawOn(c,LEFT,y-294-ph)


def cover(c, data, label):
    c.setFillColor(DEEP)
    c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(NAVY)
    c.circle(W+45,H-130,260,fill=1,stroke=0)
    c.drawImage(str(ASSETS/'leaders-logo.jpeg'), W-157,H-157,112,112)
    c.setFillColor(ORANGE)
    c.setFont('InterBold',11)
    c.drawString(LEFT,H-70,'LEADERS UNIVERSITY  /  LICENCE BI')
    title = data.get('cover_title', data['title'])
    style = ParagraphStyle('cover',fontName='Jakarta',fontSize=34,
                           leading=41,textColor=colors.white)
    p=paragraph(title,style)
    _,h=p.wrap(WIDTH-40,500)
    p.drawOn(c,LEFT,H-208-h)
    p=paragraph(data.get('subtitle','Du fichier brut à une décision expliquée.'),
                ParagraphStyle('sub',parent=BODY,fontSize=13,leading=19,textColor=colors.white))
    _,sh=p.wrap(WIDTH-45,300)
    p.drawOn(c,LEFT,H-230-h-sh)
    for i,(large,small) in enumerate([('28 h','PARCOURS GUIDÉ'),('70 %','PRATIQUE'),('0','PRÉREQUIS IT')]):
        x=LEFT+i*173
        c.setFillColor(colors.HexColor('#142443'))
        c.roundRect(x,250,158,80,12,fill=1,stroke=0)
        c.setFillColor(ORANGE)
        c.setFont('Jakarta',25)
        c.drawString(x+14,291,large)
        c.setFillColor(colors.white)
        c.setFont('InterBold',8)
        c.drawString(x+14,271,small)
    c.setFillColor(colors.white)
    c.setFont('InterBold',13)
    c.drawString(LEFT,204,'ATLAS PAPETERIE')
    c.setFont('Inter',11)
    c.drawString(LEFT,180,'Fichiers de ventes   →   ETL   →   Entrepôt   →   Rapport')
    c.setFillColor(colors.HexColor('#C9D4EE'))
    c.setFont('Inter',10)
    c.drawString(LEFT,108,label)
    c.drawString(LEFT,87,data.get('author','Youssef Douma'))
    c.setFont('Inter',8.5)
    c.drawString(LEFT,49,'Édition pédagogique · 26 octobre 2026 · données fictives')
    c.showPage()


def header(c, data, page, num, continued=False):
    c.setFillColor(NAVY)
    c.setFont('InterBold',8.2)
    c.drawString(LEFT,H-35,'ATLAS  /  PYTHON · ETL · ENTREPÔTS')
    c.setFillColor(MUTED)
    c.setFont('Inter',8)
    c.drawRightString(RIGHT,H-35,'Leaders University')
    kicker=page.get('kicker','APPRENDRE EN CONSTRUISANT')
    c.setFillColor(ORANGE)
    c.setFont('InterBold',8.5)
    c.drawString(LEFT,H-74,kicker.upper())
    title=page['title']+(' · suite' if continued else '')
    p=paragraph(title,TITLE)
    h=p.wrap(WIDTH,300)[1]
    p.drawOn(c,LEFT,H-91-h)
    c.setFont('Inter',8)
    c.setFillColor(MUTED)
    c.drawString(LEFT,35,'Youssef Douma · Licence BI · Atlas Papeterie')
    c.drawRightString(RIGHT,35,str(num))
    return H-102-h


def build(source, output, label):
    data=json.loads(source.read_text(encoding='utf-8'))
    output.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(output),pagesize=(W,H),pageCompression=1)
    c.setTitle(data['title'])
    c.setAuthor(data.get('author','Youssef Douma'))
    c.setSubject('Licence BI · Python, ETL et entrepôts de données · 28 heures')
    cover(c,data,label)
    num=2
    report=[]
    for idx,page in enumerate(data['pages']):
        y=header(c,data,page,num)
        c.bookmarkPage('p'+str(idx))
        c.addOutlineEntry(page['title'],'p'+str(idx),0,False)
        bounds=[]
        for block in page['blocks']:
            height,obj=measure(block)
            if height>H-210-BOTTOM:
                raise ValueError(f'Single block too tall in {source.name}: {page["title"]}')
            if y-height<BOTTOM:
                report.append({'page':num,'title':page['title'],'body_bottom':round(y,1),'blocks':bounds})
                c.showPage();num+=1
                y=header(c,data,page,num,continued=True)
                bounds=[]
            draw_block(c,block,obj,y,height)
            bounds.append({'type':block['type'],'top':round(y,1),'bottom':round(y-height,1)})
            y-=height
        report.append({'page':num,'title':page['title'],'body_bottom':round(y,1),'blocks':bounds})
        c.showPage();num+=1
    c.save()
    label = str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else output.name
    return {'pdf':label,'pages':num-1,
            'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'layout':report}


def main():
    books=[('start.json','01_demarrer_windows.pdf','01 / DÉMARRER SUR WINDOWS'),
           ('course.json','02_cours_atlas.pdf','02 / LE COURS ET LES MISSIONS'),
           ('reference.json','03_reperes_et_depannage.pdf','03 / REPÈRES ET DÉPANNAGE'),
           ('solutions.json','04_indices_et_corriges.pdf','04 / INDICES ET CORRIGÉS')]
    reports=[]
    for src,dest,label in books:
        reports.append(build(HERE/src,ROOT/'pdf'/dest,label))
    (HERE/'pdf_layout_report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k!='layout'} for r in reports],ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
