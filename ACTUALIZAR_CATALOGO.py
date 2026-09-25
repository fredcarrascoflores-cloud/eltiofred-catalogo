from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
OUT = ROOT / 'catalogo_items.js'
ASSETS.mkdir(parents=True, exist_ok=True)

EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
IGNORAR = {'logo.png','logo.jpg','logo.jpeg','banner.jpg','banner.jpeg','banner.png'}

CATEGORY_WORDS = {
    'tradeable':'Tradeable','tradeables':'Tradeable','trade':'Tradeable',
    'pedido':'A pedido','apedido':'A pedido','a pedido':'A pedido','a_pedido':'A pedido','a-pedido':'A pedido',
    'set':'Set','sets':'Set','oferta':'Oferta','ofertas':'Oferta'
}

def clean_name(s):
    s = re.sub(r'[_-]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s.title()

def category_from(text):
    t = text.lower().replace('_',' ')
    for key,label in CATEGORY_WORDS.items():
        if re.search(rf'(?<![a-z]){re.escape(key)}(?![a-z])', t):
            return label
    return 'Tradeable'

def parse_file(p):
    stem = p.stem.strip()

    # 1) NOMBRE__PRECIO__STOCK
    parts = [x.strip() for x in stem.split('__')]
    if len(parts) >= 3:
        name = parts[0]
        try: price = float(parts[1].replace('S/','').replace('s/','').replace(',','.'))
        except ValueError: price = None
        if price is not None:
            third = parts[2].lower()
            # If third part is numeric, it is STOCK.
            if re.fullmatch(r'\d+', third):
                stock = int(third)
                typ = category_from(stem)
                if float(price).is_integer(): price = int(price)
                return clean_name(name), price, typ, stock
            # Otherwise NOMBRE__PRECIO__CATEGORIA__STOCK
            typ = category_from(third)
            stock = 1
            if len(parts) >= 4 and re.search(r'\d+', parts[3]):
                stock = int(re.search(r'\d+', parts[3]).group())
            if float(price).is_integer(): price = int(price)
            return clean_name(name), price, typ, stock

    # 2) Flexible filename: find price, then optional stock token.
    m = re.search(r'(?<!\d)(?:s/?\s*)?(\d+(?:[.,]\d{1,2})?)(?!\d)', stem, re.I)
    if not m:
        return None
    price = float(m.group(1).replace(',','.'))
    before = stem[:m.start()].strip(' _-')
    after = stem[m.end():].strip(' _-')
    if not before:
        return None

    combined = before + ' ' + after
    sm = re.search(r'(?:stock|stk)[ _-]*(\d+)', combined, re.I)
    stock = int(sm.group(1)) if sm else 1
    typ = category_from(combined)
    if float(price).is_integer(): price = int(price)
    return clean_name(before), price, typ, stock

items=[]
for p in sorted(ASSETS.rglob('*'), key=lambda x: x.name.lower()):
    if not p.is_file() or p.suffix.lower() not in EXTS or p.name.lower() in IGNORAR:
        continue
    parsed=parse_file(p)
    if not parsed: continue
    name,price,typ,stock=parsed
    rel=p.relative_to(ROOT).as_posix()
    items.append({'name':name,'hero':'','price':price,'type':typ,'stock':stock,'image':rel})

OUT.write_text('window.catalogItems = ' + json.dumps(items,ensure_ascii=False,indent=2) + ';\n',encoding='utf-8')
print(f'Catálogo actualizado: {len(items)} items encontrados.')
print()
print('Formatos recomendados:')
print('  NOMBRE__PRECIO__STOCK.png')
print('  NOMBRE__PRECIO__CATEGORIA__STOCK.png')
print('Ejemplos:')
print('  INTERGALACTIC OBLITERATOR__315__10.jpeg')
print('  ARCANA WK__675__TRADEABLE__10.png')
print('  arcana_wk_675_stock_10.png')
print('  SET_JUGGERNAUT__120__5.jpg   <- incluye SET para clasificarlo como Set')
print('  ARCANA_PA__450__3__OFERTA.png   <- aparece en Ofertas')
print('  ARCANA_PA__450__A_PEDIDO__1.png   <- aparece en A pedido')
