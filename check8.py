import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'if\s*\(productName\s*===\s*"rh"\s*\)\s*\{([\s\S]*?)\}\n\s*//', text)
if m:
    print(m.group(0))
