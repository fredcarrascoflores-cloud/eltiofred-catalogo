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

VARIANT_WORDS = {'pack':'Pack', 'abierto':'Abierto'}

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

def variant_from(text):
    t = text.lower().replace('_',' ')
    for key,label in VARIANT_WORDS.items():
        if re.search(rf'(?<![a-z]){re.escape(key)}(?![a-z])', t):
            return label
    return ''

def parse_price(raw):
    raw = raw.strip()
    currency = '$' if '$' in raw else 'S/'
    m = re.search(r'\d+(?:[.,]\d{1,2})?', raw)
    if not m:
        return None, currency
    price = float(m.group(0).replace(',','.'))
    if price.is_integer():
        price = int(price)
    return price, currency

def parse_file(p):
    stem = p.stem.strip()

    # 1) NOMBRE__PRECIO__STOCK / NOMBRE__PRECIO__CATEGORIA__STOCK
    parts = [x.strip() for x in stem.split('__')]
    if len(parts) >= 3:
        name = parts[0]
        price, currency = parse_price(parts[1])
        if price is not None:
            third = parts[2].strip()
            variant = variant_from(third)

            # If third part is numeric, it is STOCK.
            if re.fullmatch(r'\d+', third):
                stock = int(third)
                typ = category_from(stem)
            else:
                typ = category_from(stem)
                stock = 1
                # PACK/ABIERTO is a variant, not a category.
                if len(parts) >= 4 and re.search(r'\d+', parts[3]):
                    stock = int(re.search(r'\d+', parts[3]).group())
                elif len(parts) >= 4 and not variant:
                    # Compatibility: allow CATEGORY__STOCK.
                    stock = 1

            # A set remains a Set even when PACK/ABIERTO appears in the filename.
            if re.search(r'(?<![a-z])sets?(?![a-z])', stem, re.I):
                typ = 'Set'

            return clean_name(name), price, currency, typ, stock, variant

    # 2) Flexible filename: find price, then optional stock/variant/category tokens.
    m = re.search(r'(?<!\d)(?:s\/?\s*)?\$?\s*(\d+(?:[.,]\d{1,2})?)(?!\d)', stem, re.I)
    if not m:
        return None
    raw_price = stem[max(0, m.start()-2):m.end()]
    currency = '$' if '$' in raw_price else 'S/'
    price = float(m.group(1).replace(',','.'))
    if price.is_integer():
        price = int(price)

    before = stem[:m.start()].strip(' _-')
    after = stem[m.end():].strip(' _-')
    if not before:
        return None

    # Remove a trailing currency marker from the visible name.
    before = re.sub(r'\s*[$]\s*$', '', before).strip()

    combined = before + ' ' + after
    sm = re.search(r'(?:stock|stk)[ _-]*(\d+)', combined, re.I)
    stock = int(sm.group(1)) if sm else 1
    variant = variant_from(combined)
    typ = category_from(combined)
    if re.search(r'(?<![a-z])sets?(?![a-z])', combined, re.I):
        typ = 'Set'
    return clean_name(before), price, currency, typ, stock, variant

items=[]
for p in sorted(ASSETS.rglob('*'), key=lambda x: x.name.lower()):
    if not p.is_file() or p.suffix.lower() not in EXTS or p.name.lower() in IGNORAR:
        continue
    parsed=parse_file(p)
    if not parsed: continue
    name,price,currency,typ,stock,variant=parsed
    rel=p.relative_to(ROOT).as_posix()
    items.append({
        'name':name, 'hero':'', 'price':price, 'currency':currency,
        'type':typ, 'stock':stock, 'variant':variant, 'image':rel
    })

OUT.write_text('window.catalogItems = ' + json.dumps(items,ensure_ascii=False,indent=2) + ';\n',encoding='utf-8')
print(f'Catálogo actualizado: {len(items)} items encontrados.')
print()
print('Formatos recomendados:')
print('  NOMBRE__PRECIO__STOCK.png                 -> sin símbolo = soles')
print('  NOMBRE__$PRECIO__STOCK.png                -> $ = dólares')
print('  NOMBRE__PRECIO__PACK__STOCK.png            -> Pack')
print('  NOMBRE__PRECIO__ABIERTO__STOCK.png         -> Abierto')
print('Ejemplos:')
print('  SET_MONKEY__40__10.jpg')
print('  SET_MONKEY__$40__10.jpg')
print('  SET_MONKEY__40__PACK__10.jpg')
print('  SET_MONKEY__$30__ABIERTO__10.jpg')
