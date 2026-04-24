import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const rangoFinal(.*)let baseNombreSize = 7\.5;', text, re.DOTALL)
if m:
    print(m.group(0))
