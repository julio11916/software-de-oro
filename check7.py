import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'if\s*\(productName\s*===\s*"rh"\s*\)\s*\{[\s\S]*?(?=//|if)', text)
if m:
    print(m.group(0)[:1500])
