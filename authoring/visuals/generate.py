#!/usr/bin/env python3
"""Schémas V6 du cours Atlas BI de 15 h. SVG vectoriels (polices en contours) + PNG.
Exécuter depuis n'importe quel dossier avec Python, Pillow et fonttools.
Les chiffres sont les valeurs attendues du contrat V6 local, validées par assertions.
"""
from pathlib import Path
import hashlib, json, html, argparse
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/diagrams'
FONTS = ROOT / 'authoring/assets/fonts'
NAVY, DEEP, ORANGE = '#2B3180', '#07152F', '#FF9A3C'
PALE, INK, GREY = '#F3F5FC', '#1A1F4D', '#5A6478'
WHITE = '#FFFFFF'
parser=argparse.ArgumentParser()
parser.add_argument('--contact-sheet',type=Path)
parser.add_argument('--only',nargs='+',help='Régénérer uniquement ces assets, sans toucher aux autres fichiers image.')
args=parser.parse_args()
selected=set(args.only or [])
FONT = {k: TTFont(FONTS / v) for k,v in {
    'body':'Inter-400.ttf','bold':'Inter-700.ttf','title':'PlusJakartaSans-800.ttf'}.items()}

class Canvas:
    def __init__(self, name, title, desc, height=720):
        self.name, self.title, self.desc, self.height = name,title,desc,height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>', '<rect width="1600" height="100%" fill="white"/>']
        self.bounds=[]
        self.raster=Image.new('RGB',(2400,int(height*1.5)),WHITE)
        self.draw=ImageDraw.Draw(self.raster)
        self.s=1.5
    def rect(self,x,y,w,h,fill=PALE,stroke=None,r=20):
        raster_box=tuple(round(v*self.s) for v in (x,y,x+w,y+h))
        if w == h and r >= w/2-2:
            self.draw.ellipse(raster_box,fill=fill,outline=stroke,width=round(3*self.s))
        elif stroke:
            self.draw.rounded_rectangle(raster_box,radius=round(r*self.s),fill=fill,outline=stroke,width=round(3*self.s))
        else:
            self.draw.rounded_rectangle(raster_box,radius=round(r*self.s),fill=fill)
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="3"' if stroke else '')+'/>')
    def line(self,x1,y1,x2,y2,color=ORANGE,width=5,dash=False):
        self.draw.line(tuple(round(v*self.s) for v in (x1,y1,x2,y2)),fill=color,width=round(width*self.s))
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="12 9"' if dash else '')+'/>')
    def arrow(self,x1,y1,x2,y2,color=ORANGE,width=5):
        import math
        self.line(x1,y1,x2,y2,color,width)
        angle=math.atan2(y2-y1,x2-x1); size=16
        points=[(x2,y2),(x2-size*math.cos(angle-.5),y2-size*math.sin(angle-.5)),(x2-size*math.cos(angle+.5),y2-size*math.sin(angle+.5))]
        self.draw.polygon([(round(x*self.s),round(y*self.s)) for x,y in points],fill=color)
        self.parts.append('<polygon fill="'+color+'" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+'"/>')
    def text(self,x,y,txt,size=34,color=INK,weight='body',anchor='start'):
        font=FONT[weight]; glyphs=font.getGlyphSet(); cmap=font.getBestCmap(); scale=size/font['head'].unitsPerEm
        width=sum(font['hmtx'][cmap[ord(c)]][0] for c in txt)*scale
        x0=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
        self.bounds.append((x0,y-size,x0+width,y+size*.25,txt))
        from PIL import ImageFont
        pf=ImageFont.truetype(str(FONTS / {'body':'Inter-400.ttf','bold':'Inter-700.ttf','title':'PlusJakartaSans-800.ttf'}[weight]),round(size*self.s))
        raster_x=x0
        for ch in txt:
            self.draw.text((round(raster_x*self.s),round(y*self.s)),ch,font=pf,fill=color,anchor='ls')
            raster_x+=font['hmtx'][cmap[ord(ch)]][0]*scale
        self.parts.append(f'<g aria-label="{html.escape(txt,quote=True)}" fill="{color}" transform="translate({x0:.3f},{y}) scale({scale:.8f},{-scale:.8f})">')
        cursor=0
        for char in txt:
            glyph=cmap[ord(char)]; pen=SVGPathPen(glyphs); glyphs[glyph].draw(pen)
            self.parts.append(f'<path transform="translate({cursor},0)" d="{pen.getCommands()}"/>')
            cursor+=font['hmtx'][glyph][0]
        self.parts.append('</g>')
    def lines(self,x,y,lines,size=34,color=INK,weight='body',gap=47,anchor='start'):
        for i,s in enumerate(lines): self.text(x,y+i*gap,s,size,color,weight,anchor)
    def heading(self,title,sub):
        self.rect(40,30,13,66,ORANGE,r=6)
        self.text(77,69,title,44,DEEP,'title')
        self.text(77,119,sub,30,GREY)
    def finish(self):
        bad=[b for b in self.bounds if b[0]<18 or b[2]>1582 or b[1]<10 or b[3]>self.height-10]
        assert not bad,(self.name,bad)
        svg=''.join(self.parts)+'</svg>'
        if not selected or self.name in selected:
            (OUT/(self.name+'.svg')).write_text(svg,encoding='utf-8')
            self.raster.save(OUT/(self.name+'.png'))
        return {'id':self.name,'title':self.title,'description':self.desc,'svg':f'docs/images/diagrams/{self.name}.svg','png':f'docs/images/diagrams/{self.name}.png','viewbox':[1600,self.height],'png_pixels':[2400,int(self.height*1.5)],'alt':self.desc,'text_min_px':26}

OUT.mkdir(parents=True,exist_ok=True)
# Public expected-data snapshot: frozen contract, not a claim of executed Power BI evidence.
DATA_PATH=ROOT/'authoring/visuals/v6-data.json'
D=json.loads(DATA_PATH.read_text())
E=D['expected']; S=D['scd2']; divisor=D['money']['tnd_divisor']
assert divisor==1000
assert (E['final']['facts'],E['final']['quantity'],E['final']['amount_millimes'])==(14,35,115500)
assert sum(E['zone_amounts_millimes'].values())==E['final']['amount_millimes']
assert sum(E['shop_version_amounts_millimes'].values())==E['final']['amount_millimes']
assert E['shop_version_amounts_millimes']['NBE@2026-01-05']==E['zone_amounts_millimes']['Cap Bon']==43500
assert E['shop_version_amounts_millimes']['NBE@2026-01-08']+E['shop_version_amounts_millimes']['TUN@2026-01-05']==E['zone_amounts_millimes']['Grand Tunis']==72000
assert S['effective_date']=='2026-01-08' and S['final_versions'][0][3]==S['final_versions'][1][2]
assert E['initial']['raw']==E['initial']['accepted']+E['initial']['duplicate']+E['initial']['rejected']
assert E['initial']['facts']+E['increment']['inserted']==E['final']['facts']==E['replay']['facts']
assert E['final']['amount_millimes']==E['replay']['amount_millimes']
assets=[]
def start(name,title,sub,h=800,desc=None):
    c=Canvas('v6-'+name,title,desc or sub,h); c.heading(title,sub); return c
def save(c): assets.append(c.finish())
def box(c,x,y,w,h,title,body=(),dark=False,size=32):
    c.rect(x,y,w,h,DEEP if dark else PALE)
    def wrapped(txt,fontsize,weight):
        font=FONT[weight]; cmap=font.getBestCmap()
        def width(t): return sum(font['hmtx'][cmap[ord(ch)]][0] for ch in t)*fontsize/font['head'].unitsPerEm
        result=[]; current=''
        for word in txt.split():
            candidate=(current+' '+word).strip()
            if current and width(candidate)>w-52: result.append(current); current=word
            else: current=candidate
        if current: result.append(current)
        assert all(width(t)<=w-52 for t in result),(title,result,w)
        return result
    titlelines=wrapped(title,size,'bold')
    c.lines(x+26,y+48,titlelines,size,WHITE if dark else NAVY,'bold',gap=42)
    bodylines=[line for text in body for line in wrapped(text,30,'body')]
    bodyy=y+101+42*(len(titlelines)-1)
    assert not bodylines or bodyy+(len(bodylines)-1)*43+8<y+h,(title,bodylines,h)
    c.lines(x+26,bodyy,bodylines,30,WHITE if dark else INK,gap=43)
def note(c,y,text):c.text(800,y,text,29,GREY,anchor='middle')

c=start('pipeline','Toute la chaîne, un même projet','Question : quelles ventes sont fiables, et dans quelle zone commerciale ?',800)
box(c,40,180,310,200,'1 · Lire',('CSV initial','+ vrai SELECT SQLite'))
box(c,450,180,310,200,'2 · Nettoyer',('Dates et quantités','Prix, rejets, doublons'))
box(c,860,180,310,200,'3 · Charger',('Entrepôt SQLite','3 dimensions + ventes'),True)
for x in [360,770]:c.arrow(x,265,x+75,265)
c.arrow(1170,265,1410,265);c.arrow(1410,265,1410,417)
box(c,860,430,700,200,'4 · Livrer quatre CSV',('dim_product · dim_shop · dim_date · fact_sales','Le manifeste accompagne les fichiers.'))
c.arrow(844,530,755,530)
box(c,40,430,700,200,'5 · Power BI sur Windows',('Relier les tables, calculer le CA, filtrer.','Comparer le rapport aux contrôles SQL.'),True)
note(c,703,'Une vente = une ligne de fact_sales. Les montants restent en millimes entiers.')
save(c)

c=start('postes-wsl','Sur quel système travaille chaque outil ?','Deux parcours ETL ; le rapport Power BI Desktop se fait sur Windows.',940)
c.rect(40,171,1520,330,PALE,stroke=NAVY);c.text(70,218,'PARCOURS WINDOWS',32,NAVY,'bold')
box(c,70,244,510,200,'Hôte Windows',('Application Codex','Power BI Desktop'),True)
box(c,825,244,705,200,'Ubuntu dans WSL 2',('Agent et terminal : python3','Projet : ~/cours-bi · SQLite · outputs/'))
c.arrow(592,300,812,300);c.text(701,279,'mode WSL',28,NAVY,'bold','middle')
c.arrow(812,395,592,395);c.text(701,370,'4 CSV + manifeste',26,NAVY,'bold','middle')
c.rect(40,535,1520,275,PALE,stroke=NAVY);c.text(70,583,'PARCOURS UBUNTU NATIF',32,NAVY,'bold')
box(c,70,607,650,160,'Ubuntu pris en charge',('App Codex + agent + Python + fichiers',),False,31)
box(c,1010,607,520,160,'Vrai poste Windows',('Power BI Desktop',),True,31)
c.arrow(734,695,995,695);c.text(862,662,'transférer le paquet',27,NAVY,'bold','middle')
note(c,874,'Un HTML local aide à vérifier l’ETL ; il ne prouve pas une manipulation dans Power BI.')
save(c)

c=start('codex-boucle','Construire avec Codex, puis vérifier','Une petite demande ; une modification que vous pouvez lire et expliquer.',720)
steps=[('1','Planifier',['Entrée, sortie,','preuve attendue.']),('2','Modifier',['Une fonction,','un petit changement.']),('3','Tester localement',['python3','Lire le résultat réel.']),('4','Revoir',['Comparer au besoin.','Repérer un écart.'])]
for i,(n,t,b) in enumerate(steps):
 x=40+i*389;box(c,x,194,353,230,t,b,i==2,31);c.rect(x+23,448,48,48,ORANGE,r=24);c.text(x+47,484,n,29,DEEP,'bold','middle')
 if i<3:c.arrow(x+357,300,x+382,300)
c.line(1430,510,1430,565);c.line(1430,565,214,565);c.arrow(214,565,214,510)
c.text(800,623,'Si un contrôle échoue : décrire l’écart → corriger → refaire le contrôle.',30,NAVY,'bold','middle')
save(c)

c=start('dossiers','Un dossier distribué, puis votre copie de travail','Dans Ubuntu ou WSL : ~/cours-bi · le jalon 01 crée atelier/.',850)
box(c,40,181,620,550,'~/cours-bi · dossier distribué',('README.md · AGENTS.md','projet/     → modèle de départ','outils/      → commandes de jalon','tests/       → contrôles fournis','defi/         → mission finale','solutions/ → corrigés'),True,31)
c.arrow(675,349,758,349)
box(c,775,181,785,310,'atelier/ · créé par le jalon 01',('Fichiers Python : vos petits changements.','data/ : les sources de cette copie.','outputs/ : ses résultats générés.'))
box(c,775,526,785,205,'Avant de modifier',('Lisez le fichier et gardez un état fonctionnel.','Comparez les sorties aux contrôles attendus.'))
note(c,800,'Création : python3 outils/jalon.py 01 atelier · aucune donnée à la racine du cours.')
save(c)

c=start('etoile','L’étoile : décrire chaque vente','Trois relations actives 1 → plusieurs, de la dimension vers les ventes.',990)
# Lines first, then cards: keys are repeated next to the endpoints to avoid ambiguity.
c.arrow(395,440,600,440,NAVY);c.text(427,416,'1',34,NAVY,'bold');c.text(558,416,'*',38,NAVY,'bold')
c.arrow(1200,440,995,440,NAVY);c.text(1156,416,'1',34,NAVY,'bold');c.text(1025,416,'*',38,NAVY,'bold')
c.arrow(800,310,800,367,NAVY);c.text(818,333,'1',32,NAVY,'bold');c.text(818,368,'*',34,NAVY,'bold')
box(c,534,165,532,145,'dim_date',('date_key · full_date',))
box(c,40,370,355,260,'dim_product',('product_key','product_id','product_name'))
box(c,600,378,395,374,'fact_sales',('sale_id','date_key · product_key','shop_key','quantity','unit_price_millimes','amount_millimes'),True,34)
box(c,1200,370,360,337,'dim_shop',('shop_key','shop_id · shop_name','commercial_zone','valid_from · valid_to'))
c.text(800,814,'shop_id = NBE identifie la boutique ; shop_key identifie une version.',31,NAVY,'bold','middle')
note(c,873,'Relier dim_shop.shop_key à fact_sales.shop_key préserve l’histoire.')
note(c,927,'Une flèche = le sens du filtre ; 1 et * = une clé de dimension pour plusieurs ventes.')
save(c)

c=start('scd2','Nabeul change de zone, ses ventes gardent leur histoire','SCD2 : une nouvelle version de la boutique, sans réécrire les anciennes ventes.',850)
c.text(75,211,'Même identifiant métier : shop_id = NBE',33,NAVY,'bold')
box(c,40,249,705,222,'Ancienne version · Cap Bon',('Du 05/01/2026 au 08/01/2026 exclu','shop_key ancien','Vente du 07 janvier → cette version'),True,32)
box(c,855,249,705,222,'Nouvelle version · Grand Tunis',('Dès le 08/01/2026 inclus','shop_key nouveau','Vente du 08 janvier → cette version'),False,32)
c.line(100,552,1500,552,NAVY,6);c.line(800,505,800,610,ORANGE,7)
c.text(800,653,'08 janvier 2026',36,NAVY,'bold','middle');c.text(262,593,'Avant : Cap Bon',31,INK,'bold','middle');c.text(1280,593,'Dès ce jour : Grand Tunis',31,INK,'bold','middle')
c.rect(40,704,1520,90,PALE);c.text(800,760,'Ancienne vente → ancienne clé conservée ; nouvelle vente → clé de la bonne période.',30,INK,'bold','middle')
save(c)

c=start('chiffres-zones','Le CA par zone commerciale historique','Après le lot du 8 janvier 2026 · axe et valeurs en TND · valeurs attendues du contrat.',900)
# Geometrically exact stacked lengths, derived from expected millimes.
x0=310;plotw=1140;scale=plotw/(80000/divisor)
for tick in [0,20,40,60,80]:
 x=x0+tick*scale;c.line(x,227,x,576,'#DDE1ED',2);c.text(x,624,str(tick),28,GREY,anchor='middle')
c.text(1479,624,'TND',28,GREY,'bold')
for y,zone,segments in [(280,'Cap Bon',[(43500,NAVY)]),(467,'Grand Tunis',[(67500,NAVY),(4500,ORANGE)])]:
 c.text(270,y+18,zone,32,NAVY,'bold','end');x=x0
 for amount,col in segments:
  w=(amount/divisor)*scale;c.rect(x,y-48,w,85,col,r=0);x+=w
 c.text(x+18,y+12,f"{E['zone_amounts_millimes'][zone]/divisor:.3f}".replace('.',','),34,DEEP,'bold')
c.text(310,399,'NBE avant le 8 janvier : 43,500',30,INK)
c.text(310,572,'TUN : 67,500 + NBE dès le 8 janvier : 4,500',30,INK)
c.rect(40,688,1520,142,PALE);c.text(800,741,'43,500 + 72,000 = 115,500 TND',40,NAVY,'bold','middle')
c.text(800,792,'14 lignes de vente · 35 unités · 115 500 millimes',31,INK,anchor='middle')
save(c)

c=start('millimes','Compter les montants sans perdre de précision','Une unité claire dans les données ; une conversion lisible dans le rapport.',690)
box(c,40,185,700,230,'Dans l’entrepôt : des entiers',('1 TND = 1 000 millimes','2 × 4 500 = 9 000 millimes'),True)
box(c,860,185,700,230,'Dans le rapport : des TND',('9 000 ÷ 1 000 = 9,000 TND','115 500 ÷ 1 000 = 115,500 TND'))
c.arrow(755,302,845,302)
c.rect(40,473,1520,127,PALE);c.text(800,522,'CA TND = DIVIDE(SUM(fact_sales[amount_millimes]), 1000)',30,NAVY,'bold','middle');c.text(800,570,'Sommer les millimes, puis diviser par 1 000.',30,INK,anchor='middle')
save(c)

c=start('contexte-quota','Contexte et limite d’usage : deux idées différentes','Lire seulement les indicateurs réellement affichés dans votre client.',750)
box(c,40,185,735,350,'Contexte : ce que l’agent peut lire',('Messages, consignes et fichiers utiles.','Les tokens sont des morceaux de texte.','Un fichier long occupe plus de contexte ;','le nombre de lignes ne compte pas les tokens.'),False,31)
box(c,825,185,735,350,'Usage : ce que le compte autorise',('Le service peut limiter l’utilisation.','L’indicateur dépend du client et du compte.','Relever la valeur visible, ou « non affiché ».','Aucun prix API à déduire du quota Free.'),True,31)
c.rect(40,580,1520,110,PALE);c.text(800,625,'Avant de reprendre : garder un état court du projet.',32,NAVY,'bold','middle');c.text(800,668,'Fait · preuve · problème · prochaine action',31,INK,anchor='middle')
save(c)

c=start('modele-effort','Modèle, effort et vitesse : lire les bons choix','Utiliser les options visibles sur le poste ; ne pas supposer leur disponibilité sur Free.',770)
for x,t,b in [(40,'Modèle',['Quel modèle répond ?','Relever son nom affiché.']), (557,'Effort de raisonnement',['Quel niveau de réflexion ?','Viser un besoin précis.']), (1074,'Vitesse de service',['Quel mode de service ?','Standard : vitesse de service.'])]:
 box(c,x,185,486,280,t,b,False,30)
c.rect(40,510,1520,175,DEEP);c.text(800,563,'Chemin Free documenté : GPT-6 Luna + Standard dans Desktop.',31,WHITE,'bold','middle');c.text(800,614,'Vérifier le déploiement et les choix réellement affichés sur le compte.',30,WHITE,anchor='middle');c.text(800,660,'Un réglage plus exigeant ne dispense jamais de tester le résultat.',30,WHITE,anchor='middle')
save(c)

c=start('revue','Deux revues indépendantes, un seul auteur','Au plus deux lecteurs sur des cibles distinctes ; personne ne modifie en parallèle.',810)
box(c,40,188,660,225,'Lecteur A · qualité des lignes',('Lire le nettoyage et les rejets.','Rendre un constat avec une preuve.'))
box(c,900,188,660,225,'Lecteur B · histoire et relations',('Lire SCD2 et le modèle en étoile.','Rendre un constat avec une preuve.'))
c.arrow(370,426,670,509);c.arrow(1230,426,930,509)
box(c,520,518,560,156,'Un auteur corrige',('Puis relance le contrôle et la revue.',),True,33)
note(c,752,'Si la fonction manque sur Free : deux passes séparées, ou deux revues humaines.')
save(c)

c=start('parcours','Cinq séances, cinq victoires visibles','5 × 3 h = 15 h, pauses comprises · un seul projet Atlas Papeterie.',760)
steps=[('S1','Ouvrir la mission',['Poste + dossier','Premier contrôle']),('S2','Fiabiliser les ventes',['Nettoyage + SQL','Une vente =','une ligne']),('S3','Charger et historiser',['Ajout + rejeu','SCD2 de Nabeul']),('S4','Construire le rapport',['4 CSV + Power BI','Relations + revue']),('S5','Prouver les chiffres',['Défi en groupe','Rapport +','explication'])]
for i,(n,t,b) in enumerate(steps):
 x=40+i*309;c.rect(x,187,284,380,DEEP if i==4 else PALE);col=WHITE if i==4 else INK;c.rect(x+22,210,66,66,ORANGE,r=33);c.text(x+55,255,n,30,DEEP,'bold','middle')
 # Intentionally two-line titles sized for an A4 full-width figure.
 titlelines={'S1':['Ouvrir','la mission'],'S2':['Fiabiliser','les ventes'],'S3':['Charger et','historiser'],'S4':['Construire','le rapport'],'S5':['Prouver','les chiffres']}[n]
 c.lines(x+22,332,titlelines,31,col,'bold',42);c.lines(x+22,454,b,28,col,gap=41)
 if i<4:c.arrow(x+287,382,x+302,382)
c.text(800,647,'Chaque semaine : demander petit → exécuter → vérifier → expliquer.',31,NAVY,'bold','middle')
save(c)

c=start('qualite','Une ligne lue a une issue explicite','Lot initial · chiffres attendus du contrat · les sources restent intactes.',760)
values=[('16','lignes lues',['Le fichier initial.']),('12','ventes retenues',['Valides et distinctes.']),('1','doublon identique',['Déjà vu, même contenu.']),('3','lignes rejetées',['Quantité, produit','ou date invalide.'])]
for i,(n,t,b) in enumerate(values):
 x=40+i*389;c.rect(x,192,353,265,DEEP if i==0 else PALE);col=WHITE if i==0 else INK;c.text(x+25,269,n,65,ORANGE if i==0 else NAVY,'title');c.text(x+25,335,t,30,col,'bold');c.lines(x+25,399,b,27,col,gap=39)
c.text(800,545,'16 = 12 + 1 + 3',45,NAVY,'bold','middle')
note(c,617,'Un doublon différent portant le même sale_id est un conflit : on arrête et on explique.')
note(c,674,'Après chargement initial : 12 faits · 32 unités · 99 000 millimes.')
save(c)

c=start('ajout-rejeu','Ajouter une fois ; rejouer sans doubler les ventes','Une nouvelle livraison étend la période ; le rejeu conserve les clés et les valeurs.',760)
for x,title,n,lines in [(40,'Initial','12 faits',['32 unités','99 000 millimes']), (565,'Après le lot SQL','14 faits',['35 unités','115 500 millimes']), (1090,'Après rejeu','14 faits',['35 unités','115 500 millimes'])]:
 box(c,x,190,470,303,title,(),x==565,32);c.text(x+26,319,n,52,WHITE if x==565 else NAVY,'title');c.lines(x+26,387,lines,32,WHITE if x==565 else INK,gap=48)
for x in [519,1044]:c.arrow(x,332,x+31,332)
c.text(800,573,'Lot SQL : 3 ventes lues = 2 nouvelles + 1 déjà connue.',33,NAVY,'bold','middle')
note(c,638,'Rejouer le lot : 0 nouvelle vente, 0 nouvelle version de boutique.')
note(c,693,'Un même sale_id avec un contenu différent provoque un refus, sans écrasement.')
save(c)

manifest={'version':6,'language':'fr','source':'authoring/visuals/generate.py','data_source':'authoring/visuals/v6-data.json','data_sha256':hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),'quantitative_assertions':E,'provenance':D['provenance'],'palette':{'navy':NAVY,'deep':DEEP,'orange':ORANGE},'fonts':{'Inter':'authoring/assets/fonts/Inter-OFL.txt','Plus Jakarta Sans':'authoring/assets/fonts/PlusJakartaSans-OFL.txt'},'license':'Original course diagrams; no simulated UI, no third-party screenshots/logos. Fonts SIL OFL 1.1; SVG glyphs are outlined paths.','assets':assets}
(ROOT/'authoring/visuals/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if args.contact_sheet:
 import math
 rows=math.ceil(len(assets)/3);sheet=Image.new('RGB',(1800,rows*440),'#DDE1ED');dr=ImageDraw.Draw(sheet)
 for i,a in enumerate(assets):
  im=Image.open(ROOT/a['png']).convert('RGB');im.thumbnail((570,395));x=15+(i%3)*600;y=15+(i//3)*440;sheet.paste(im,(x,y));dr.text((x,y+402),a['id'],fill='black')
 args.contact_sheet.parent.mkdir(parents=True,exist_ok=True);sheet.save(args.contact_sheet)
print(f'{len(assets)} SVG + PNG V6 ; contract assertions passed: 14 facts, 35 units, 115500 millimes.')
