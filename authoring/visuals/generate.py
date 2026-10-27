#!/usr/bin/env python3
"""Six schémas pédagogiques Atlas. SVG vectoriels (polices en contours) + PNG.
Exécuter depuis n'importe quel dossier avec Python, Pillow et fonttools.
Les valeurs quantitatives sont calculées à partir des CSV publics inchangés.
"""
from pathlib import Path
from decimal import Decimal
from datetime import date
import csv, hashlib, json, html, argparse
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageOps, ImageDraw

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
        return {'id':self.name,'title':self.title,'description':self.desc,'svg':f'docs/images/diagrams/{self.name}.svg','png':f'docs/images/diagrams/{self.name}.png','viewbox':[1600,self.height],'png_pixels':[2400,int(self.height*1.5)],'alt':self.desc,'text_min_px':28}

def load(name):
    with (ROOT/'projet/data'/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def validated(rows):
    products={r['product_id'] for r in load('produits.csv')};shops={r['shop_id'] for r in load('boutiques.csv')}
    accepted={};rejected=[];dupes=[]
    for r in rows:
        try:
            v={k:s.strip() for k,s in r.items()}
            for k in ['sale_id','shop_id','product_id']:v[k]=v[k].upper()
            date.fromisoformat(v['date']); q=int(v['quantity']); price=Decimal(v['unit_price_tnd'])*1000
            assert v['sale_id'] and q>0 and price>0 and price==int(price) and v['shop_id'] in shops and v['product_id'] in products
            v['quantity']=q;v['amount_millimes']=q*int(price)
            if v['sale_id'] in accepted:
                assert accepted[v['sale_id']]==v;dupes.append(v)
            else:accepted[v['sale_id']]=v
        except (ValueError,AssertionError):rejected.append(r)
    return list(accepted.values()),rejected,dupes
initial=load('ventes_initiales.csv');added=load('ventes_ajout.csv')
base,rejected,dupes=validated(initial);addition,_,_=validated(added)
all_by_id={v['sale_id']:v for v in base}
for v in addition:
    if v['sale_id'] in all_by_id:assert v==all_by_id[v['sale_id']]
    all_by_id[v['sale_id']]=v
final=list(all_by_id.values())
# Rejouer le même lot : chaque identifiant doit déjà exister avec le même contenu.
replay_inserted=0;replay_existing=0
for v in addition:
    if v['sale_id'] in all_by_id:
        assert v == all_by_id[v['sale_id']]
        replay_existing+=1
    else:
        all_by_id[v['sale_id']]=v;replay_inserted+=1
replay_total=sum(v['amount_millimes'] for v in all_by_id.values())
assert (replay_inserted,replay_existing,replay_total)==(0,3,115500)
base_total=sum(v['amount_millimes'] for v in base);final_total=sum(v['amount_millimes'] for v in final)
assert (len(initial),len(base),len(rejected),len(dupes),sum(v['quantity'] for v in base),base_total)==(16,12,3,1,32,99000)
assert (len(final),sum(v['quantity'] for v in final),final_total)==(14,35,115500)
assert (min(v['date'] for v in base),max(v['date'] for v in base),max(v['date'] for v in final))==('2026-01-05','2026-01-07','2026-01-08')
assets=[]

c=Canvas('parcours-a-e','Un projet, cinq étapes','A Comprendre le projet ; B Préparer son poste ; C Construire avec l’IA ; D Contrôler le rapport ; E Réaliser le défi.',540)
c.heading('De fichiers CSV à une décision','Atlas Papeterie • construire, vérifier et expliquer son propre rapport')
steps=[('A','Comprendre','le projet','Une question','et des données'),('B','Préparer','son poste','Un dossier','et des outils'),('C','Construire','avec l’IA','Une fonction','à la fois'),('D','Contrôler','le rapport','Des preuves','et des totaux'),('E','Réaliser','le défi','Réutiliser','la méthode')]
for i,(letter,l1,l2,s1,s2) in enumerate(steps):
    x=40+i*311;c.rect(x,173,275,290,DEEP if i==4 else PALE)
    col=WHITE if i==4 else INK;c.rect(x+22,195,55,55,ORANGE,r=27)
    c.text(x+49,236,letter,36,DEEP,'title','middle');c.lines(x+22,298,[l1,l2],32,col,'bold',43);c.lines(x+22,396,[s1,s2],29,col,gap=39)
    if i<4:c.arrow(x+280,313,x+302,313)
assets.append(c.finish())

c=Canvas('trois-espaces','Trois espaces de travail','Dans l’éditeur on écrit et enregistre le code. Dans le terminal on lance une commande. Dans le navigateur on consulte le rapport HTML. Les trois travaillent avec le même dossier.',700)
c.heading('Où faire chaque action ?','Trois espaces, un même dossier de projet')
cards=[(40,'1','ÉDITEUR',['Écrire le code Python.','Enregistrer le fichier.'],'projet/calcul.py',['Le fichier est du texte.','Il attend d’être exécuté.']),
       (567,'2','TERMINAL',['Lancer une commande.','Lire le résultat affiché.'],'Commande de votre route',['La commande agit dans','le dossier courant.']),
       (1094,'3','NAVIGATEUR',['Ouvrir le rapport HTML.','Observer les indicateurs.'],'outputs/rapport_atlas.html',['Afficher le résultat','pour le contrôler.'])]
for x,n,title,lines,example,foot in cards:
    c.rect(x,178,466,440);c.rect(x+24,199,52,52,ORANGE,r=26);c.text(x+50,238,n,32,DEEP,'bold','middle')
    c.text(x+25,300,title,33,NAVY,'bold');c.lines(x+25,353,lines,30,gap=45)
    c.rect(x+24,431,418,65,DEEP,r=12);c.text(x+44,472,example,28,WHITE,'bold')
    c.lines(x+25,546,foot,29,GREY,gap=40)
c.text(800,668,'Fichier = un document enregistré • dossier = un ensemble de fichiers',30,INK,anchor='middle')
assets.append(c.finish())

c=Canvas('poste-docker','Le poste et le conteneur','L’éditeur et le navigateur restent sur le PC. Docker exécute Python dans un conteneur. Un montage relie le dossier projet du PC au dossier /workspace du conteneur : ce sont les mêmes fichiers. Le rapport HTML écrit dans outputs est ouvert dans le navigateur du PC. L’assistant IA reste sur le PC ou dans le chat web.',820)
c.heading('Docker : où sont le code et les résultats ?','Le conteneur exécute Python ; les fichiers restent dans votre dossier de projet.')
c.rect(40,167,1520,607,PALE,stroke=NAVY,r=26);c.text(70,216,'VOTRE PC',33,NAVY,'bold')
c.rect(1045,186,484,61,WHITE,r=15);c.text(1287,227,'Chat IA web / assistant sur le PC',28,INK,'bold','middle')
c.rect(80,282,525,289,WHITE,stroke=NAVY);c.text(110,329,'Dossier projet/',37,NAVY,'bold')
c.lines(110,382,['calcul.py  •  data/','outputs/rapport_atlas.html'],32,gap=52)
c.rect(110,482,463,60,PALE,r=12);c.text(341,523,'ÉDITEUR : lire et enregistrer',28,INK,'bold','middle')
c.rect(825,282,690,289,DEEP);c.text(1170,329,'CONTENEUR DOCKER',36,WHITE,'bold','middle')
c.text(1170,388,'Python exécute le code',34,WHITE,'bold','middle')
c.lines(1170,451,['/workspace/projet/','calcul.py  •  data/  •  outputs/'],30,WHITE,gap=45,anchor='middle')
c.arrow(613,401,813,401);c.text(714,369,'montage',29,NAVY,'bold','middle');c.lines(714,456,['mêmes','fichiers'],28,INK,gap=37,anchor='middle')
c.arrow(1180,581,1180,625);c.rect(825,635,690,90,WHITE,stroke=NAVY);c.text(1170,675,'NAVIGATEUR DU PC',31,NAVY,'bold','middle');c.text(1170,711,'ouvre outputs/rapport_atlas.html',30,INK,anchor='middle')
c.lines(85,633,['TERMINAL DU PC','lance la commande Docker','puis affiche les messages.'],31,INK,gap=43)
assets.append(c.finish())

c=Canvas('boucle-ia','Une petite boucle avec l’IA','Spécifier le besoin et le résultat attendu, demander une petite fonction, exécuter le fichier, contrôler avec une preuve puis expliquer le résultat. Si la preuve échoue, revenir au besoin et corriger une seule chose.',620)
c.heading('L’IA propose ; vous gardez la main','Une petite fonction, une exécution réelle, une preuve compréhensible.')
steps=[('1','Spécifier',['Une entrée,','un résultat.']),('2','Fonction',['Une tâche,','un fichier.']),('3','Exécuter',['Une commande,','un résultat réel.']),('4','Contrôler',['Comparer avec','la valeur prévue.']),('5','Expliquer',['Dire pourquoi','c’est correct.'])]
for i,(n,title,lines) in enumerate(steps):
    x=40+i*311;c.rect(x,185,275,245,DEEP if i==3 else PALE)
    col=WHITE if i==3 else INK;c.text(x+22,230,n,32,ORANGE,'bold');c.text(x+22,283,title,33,col,'bold');c.lines(x+22,341,lines,28,col,gap=40)
    if i<4:c.arrow(x+280,304,x+302,304)
c.line(1459,448,1459,492);c.line(1459,492,178,492);c.arrow(178,492,178,449)
c.text(800,552,'Si un contrôle échoue : décrire l’écart, corriger une chose, relancer.',31,NAVY,'bold','middle')
assets.append(c.finish())

c=Canvas('etl-qualite','Un lot, trois issues, un grain','Le lot initial contient 16 lignes : 12 ventes retenues, 1 doublon identique et 3 rejets. Le doublon est S003. Les rejets portent sur une quantité nulle, un produit inconnu et une date impossible. Une ligne retenue représente une vente élémentaire ; deux carnets à 4500 millimes donnent 9000 millimes, soit 9,000 TND.',780)
c.heading('Nettoyer sans perdre la trace','Une ligne retenue = une vente élémentaire identifiée par sale_id.')
c.rect(40,178,320,245,DEEP);c.text(200,246,'16',70,WHITE,'title','middle');c.lines(200,303,['lignes CSV','avant contrôle'],32,WHITE,gap=44,anchor='middle')
c.arrow(374,296,449,296)
for x,num,title,lines,fill in [(474,'12','retenues',['Ventes valides','et distinctes'],PALE),(842,'1','doublon',['S003 répété','à l’identique'],PALE),(1210,'3','rejets',['Quantité, produit','ou date invalide'],PALE)]:
    c.rect(x,178,350,245,fill);c.text(x+175,247,num,66,NAVY,'title','middle');c.text(x+175,299,title,34,NAVY,'bold','middle');c.lines(x+175,351,lines,28,INK,gap=38,anchor='middle')
c.text(658,470,'16 = 12 + 1 + 3',38,NAVY,'bold','middle');c.text(1240,470,'Chaque issue a sa trace.',29,GREY,anchor='middle')
c.rect(40,512,1520,218,PALE);c.text(73,562,'GRAIN : une ligne décrit une vente, pas une boutique ou une journée.',31,NAVY,'bold')
c.text(73,619,'S001 • le 5 janvier 2026 • Nabeul • Carnet • quantité : 2',31,INK)
c.text(73,682,'2 × 4 500 millimes = 9 000 millimes = 9,000 TND',38,DEEP,'bold')
assets.append(c.finish())

c=Canvas('ca-ajout-rejeu','Un ajout, puis un rejeu sans double comptage','Le chiffre d’affaires chargé passe de 99,000 TND pour 12 ventes du 5 au 7 janvier 2026 à 115,500 TND pour 14 ventes du 5 au 8 janvier 2026. Le rejeu conserve 115,500 TND et 14 ventes. Ces cumuls de périodes différentes ne mesurent pas une performance.',780)
c.heading('Ajouter une fois, rejouer sans compter deux fois','Chiffre d’affaires chargé • montants calculés depuis les CSV du projet')
left,bottom,top=165,535,205
c.text(56,184,'TND',28,GREY,'bold')
for tick in [0,30,60,90,120]:
    y=bottom-(bottom-top)*tick/120;c.line(left,y,1540,y,'#DDE1ED',2);c.text(left-24,y+10,str(tick),28,GREY,anchor='end')
for x,val,color,label in [(286,base_total/1000,NAVY,'Initial'),(732,final_total/1000,ORANGE,'Après ajout'),(1178,replay_total/1000,NAVY,'Après rejeu')]:
    h=(bottom-top)*val/120;c.rect(x,bottom-h,200,h,color,r=6)
    c.text(x+100,bottom-h-17,f'{val:.3f}'.replace('.',','),38,DEEP,'bold','middle')
    c.text(x+100,588,label,34,NAVY,'bold','middle')
    c.lines(x+100,631,['5–7 janvier 2026' if label=='Initial' else '5–8 janvier 2026','12 ventes' if label=='Initial' else '14 ventes'],30,INK,gap=41,anchor='middle')
c.text(800,736,'Période étendue par l’ajout ; rejeu identique. Ces totaux ne mesurent pas une performance.',29,GREY,anchor='middle')
assets.append(c.finish())

source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'projet/data').glob('*.csv')}
manifest={'version':1,'language':'fr','palette':{'navy':NAVY,'deep':DEEP,'orange':ORANGE},'source':'authoring/visuals/generate.py','generated_from_csv':source_hashes,'quantitative_assertions':{'initial_rows':16,'accepted':12,'duplicates':1,'rejected':3,'base_millimes':base_total,'final_millimes':final_total,'replay_millimes':replay_total,'replay_inserted':replay_inserted,'replay_existing':replay_existing,'base_period':['2026-01-05','2026-01-07'],'final_period':['2026-01-05','2026-01-08']},'fonts':{'Inter':'authoring/assets/fonts/Inter-OFL.txt','Plus Jakarta Sans':'authoring/assets/fonts/PlusJakartaSans-OFL.txt'},'license':'Original diagrams authored for the course; no third-party screenshots or logos. Fonts: SIL OFL 1.1. SVG glyphs are paths.','assets':assets}
(ROOT/'authoring/visuals/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Contact sheet is a QA aid, emitted only when requested outside public directories.
if args.contact_sheet:
    sheet=Image.new('RGB',(1600,1800),'#DDE1ED');draw=ImageDraw.Draw(sheet)
    for i,a in enumerate(assets):
        im=Image.open(ROOT/a['png']).convert('RGB');im.thumbnail((775,540));x=15+(i%2)*800;y=20+(i//2)*590
        sheet.paste(im,(x,y));draw.text((x,y+545),a['id'],fill='black')
    args.contact_sheet.parent.mkdir(parents=True,exist_ok=True);sheet.save(args.contact_sheet)
print(f'{len(selected) if selected else len(assets)} SVG + PNG créés ; CSV inchangés ; montants vérifiés : {base_total}, {final_total} millimes.')
