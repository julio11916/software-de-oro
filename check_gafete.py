import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'// GAFETE\n\s*if \(productName\.includes\("gafete"\)\)\s*\{([\s\S]*?)//', text)
if m:
    print(m.group(0))
