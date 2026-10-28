#!/usr/bin/env python3
"""Ajoute les photos réelles du traiteur + emplacements prêts pour les photos générées.
Usage : python3 ajout_photos.py <dossier_depot> <dossier_uploads>
Chaque .ph porte data-img ; si le fichier existe il s'affiche, sinon le cadre « Photo à venir » reste."""
import sys, os, re, json
from PIL import Image
D, U = sys.argv[1], sys.argv[2]
os.makedirs(f'{D}/images', exist_ok=True)
SRC = {  # préfixe de l'upload -> nom final
 '733699f9':'mariage-salle','8d140351':'mariage-service','0441f918':'cocktail-pieces',
 'ecf8a3c9':'broche-cochon','db891c91':'plancha-brochettes','c07af391':'atelier-crepes',
 '4fffe942':'equipe','75321d0a':'boutique-facade'}
for p, n in SRC.items():
    f = [x for x in os.listdir(U) if x.startswith(p)][0]
    im = Image.open(f'{U}/{f}').convert('RGB')
    if im.width > 1400: im = im.resize((1400, round(im.height*1400/im.width)), Image.LANCZOS)
    im.save(f'{D}/images/{n}.jpg', quality=82, optimize=True, progressive=True)

POS = {'mariage-salle':'50% 70%','mariage-service':'72% 40%','cocktail-pieces':'50% 65%','broche-cochon':'55% 55%',
       'plancha-brochettes':'50% 70%','atelier-crepes':'30% 40%','equipe':'50% 45%','boutique-facade':'50% 40%'}
ALT = {'mariage-salle':'Salle de réception de mariage aux tables dressées','mariage-service':'Un cuisinier de Saveurs & des Lys dresse une table sous chapiteau',
 'cocktail-pieces':'Buffet de pièces cocktail dans un jardin fleuri','broche-cochon':'Cochon à la broche au feu de bois','plancha-brochettes':'Brochettes grillées à la plancha lors d\'une réception en plein air',
 'atelier-crepes':'Atelier galettes et crêpes préparé sur place','equipe':'L\'équipe de Saveurs & des Lys en tenue de service','boutique-facade':'Façade de la boutique Saveurs & des Lys à Brinon-sur-Beuvron',
 'buffet-chaud':'Buffet chaud de plats mijotés','buffet-froid':'Buffet froid de charcuteries et pièces froides','buffet-salades':'Salades composées de saison','buffet-desserts':'Desserts de saison',
 'menu-des-lys':'Assiette dressée du Menu des Lys','cocktail-verrines':'Verrines et cuillères cocktail','broche-tablee':'Tablée conviviale autour d\'une prestation à la broche',
 'plats-emporter':'Plats à emporter cuisinés maison','epicerie-locale':'Épicerie et produits locaux'}
def ph(name, label=None, extra=''):
    a = f'<div class="ph"{extra}>' if False else None
def attrs(n): return f' data-img="images/{n}.jpg" data-pos="{POS.get(n,"center")}" data-alt="{ALT[n]}"'
def rep(s, old, new, f):
    assert s.count(old) == 1, f'{f}: cible introuvable ou multiple: {old[:90]}'
    return s.replace(old, new)
def label(s, f, lab, n):
    old = f'<div class="ph"><span class="ph-label">{lab}</span></div>'
    return rep(s, old, f'<div class="ph"{attrs(n)}><span class="ph-label">{lab}</span></div>', f)
def lab_open(s, f, lab, n):  # ph contenant d'autres éléments (pas fermé juste après le label)
    old = f'<div class="ph"><span class="ph-label">{lab}</span>'
    return rep(s, old, f'<div class="ph"{attrs(n)}><span class="ph-label">{lab}</span>', f)

LOADER = """<script>
(function(){
  function ld(el){var u=el.getAttribute('data-img');if(!u||el.classList.contains('ok'))return;
    var i=new Image();i.onload=function(){el.style.setProperty('--img','url("'+u+'")');el.style.setProperty('--pos',el.getAttribute('data-pos')||'center');
      el.classList.add('ok');var a=el.getAttribute('data-alt');if(a){el.setAttribute('role','img');el.setAttribute('aria-label',a)}};i.src=u}
  window.ldPh=ld;document.querySelectorAll('.ph[data-img]').forEach(ld);
})();
</script>
"""
CSS = """
/* photos réelles : data-img chargé par script, sinon cadre « Photo à venir » */
.ph.ok{background:var(--img) var(--pos,center)/cover no-repeat}
.ph.ok .ph-label,.ph.ok + .ph-label{display:none}
"""
def edit(f, fn):
    p = f'{D}/{f}'; s = open(p, encoding='utf-8').read()
    s = fn(s, f)
    if '/* photos réelles' not in s:
        s = rep(s, '</style>', CSS + '</style>', f)
    if 'window.ldPh' not in s:
        s = rep(s, '</body>', LOADER + '</body>', f)
    open(p, 'w', encoding='utf-8').write(s)

def accueil(s, f):
    for h, n in [('mariages','mariage-salle'),('buffets-chauds','buffet-chaud'),('buffets-froids','buffet-froid'),('cocktails','cocktail-pieces'),('broche','broche-cochon')]:
        old = f'<a href="prestations.html#{h}" class="carte"><div class="ph"></div>'
        s = rep(s, old, f'<a href="prestations.html#{h}" class="carte"><div class="ph"{attrs(n)}></div>', f)
    return s
def prestations(s, f):
    for h, n in [('mariages','mariage-salle'),('buffets-chauds','buffet-chaud'),('buffets-froids','buffet-froid'),('cocktails','cocktail-pieces'),('broche','broche-cochon')]:
        old = f'<a href="#{h}" class="sv"><div class="ph"><span class="ph-label">Photo à venir</span></div>'
        s = rep(s, old, f'<a href="#{h}" class="sv"><div class="ph"{attrs(n)}><span class="ph-label">Photo à venir</span></div>', f)
    for lab, n in [('mariage','mariage-salle'),('buffet chaud','buffet-chaud'),('buffet froid','buffet-froid'),('cocktail','cocktail-pieces'),('broche / feu de bois','broche-cochon')]:
        s = label(s, f, f'Photo à venir : {lab}', n)
    return s
def menus(s, f):
    s = label(s, f, 'Photo à venir : assiette Menu des Lys', 'menu-des-lys')
    for i, n in enumerate(['cocktail-pieces','plancha-brochettes','atelier-crepes','cocktail-verrines'], 1):
        s = label(s, f, f'Photo à venir {i}/4', n)
    s = label(s, f, 'Photo à venir : le feu', 'broche-cochon')
    s = label(s, f, 'Photo à venir : convivialité', 'broche-tablee')
    for i, n in enumerate(['buffet-chaud','buffet-froid','buffet-salades','buffet-desserts'], 1):
        s = label(s, f, f'Photo {i}', n)
    return s
def boutique(s, f):
    s = lab_open(s, f, 'Photo à venir : boutique / vitrine', 'boutique-facade')
    s = label(s, f, 'Photo à venir : plats à emporter', 'plats-emporter')
    s = label(s, f, 'Photo à venir : épicerie', 'epicerie-locale')
    return s
def histoire(s, f):
    s = label(s, f, "Photo à venir : portrait d'Antoine en cuisine", 'mariage-service')
    old = '<h3>En cuisine et en salle</h3>'
    s = rep(s, old, f'<div class="ph"{attrs("equipe")} style="aspect-ratio:4/3;margin:0 0 16px"></div>' + old, f)
    s = rep(s, ', prénoms à citer ou non, photo d\'équipe.', ', prénoms à citer ou non.', f)
    return s
def galerie(s, f):
    items = [('mariages','mariage-salle'),('cocktails','cocktail-pieces'),('broche','broche-cochon'),
             ('cuisine','atelier-crepes'),('mariages','mariage-service'),('buffets','buffet-chaud'),
             ('cocktails','plancha-brochettes'),('cuisine','equipe'),('buffets','buffet-froid')]
    i0 = s.index('var cats=[')
    i1 = s.index("var btns=[].slice.call(mur.children)")
    js = ("var noms={mariages:'Mariages',buffets:'Buffets',cocktails:'Cocktails',broche:'Broche',cuisine:'En cuisine'},\n"
          "      mur=document.getElementById('mur'),\n"
          "      alts=" + json.dumps({n: ALT[n] for _, n in items}, ensure_ascii=False) + ",\n"
          "      pos=" + json.dumps({n: POS.get(n, 'center') for _, n in items}) + ",\n"
          "      items=" + json.dumps(items) + ";\n"
          "  items.forEach(function(it,i){mur.insertAdjacentHTML('beforeend','<button type=\"button\" data-c=\"'+it[0]+'\" data-f=\"'+it[1]+'\"><div class=\"ph\" data-img=\"images/'+it[1]+'.jpg\" data-pos=\"'+pos[it[1]]+'\" data-alt=\"'+alts[it[1]].replace(/\"/g,'&quot;')+'\"><span class=\"ph-label\">'+noms[it[0]]+' · photo '+(i+1)+'</span></div></button>');});\n"
          "  ")
    s = s[:i0] + js + s[i1:]
    # lightbox : affiche l'image si chargée
    old = "function montre(n){var v=visibles();cur=(n+v.length)%v.length;lab.textContent=v[cur].textContent+' (agrandie)'}"
    new = ("function montre(n){var v=visibles();cur=(n+v.length)%v.length;var p=v[cur].querySelector('.ph'),b=boite.querySelector('.ph');"
           "if(p.classList.contains('ok')){b.classList.add('ok');b.style.setProperty('--img',p.style.getPropertyValue('--img'));b.style.setProperty('--pos','center');b.style.backgroundSize='contain';lab.textContent=''}"
           "else{b.classList.remove('ok');b.style.removeProperty('--img');b.style.backgroundSize='';lab.textContent=v[cur].textContent+' (agrandie)'}}")
    s = rep(s, old, new, f)
    return s
for f, fn in [('index.html',accueil),('prestations.html',prestations),('menus.html',menus),('boutique.html',boutique),('histoire.html',histoire),('galerie.html',galerie)]:
    edit(f, fn)
print('ok')
