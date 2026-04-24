import json

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# I will write a script to carefully update the `colorMatriz` logic for 'ejercito'

import re
match = re.search(r'const colorMatriz = (\{.*?\});\n\nconst estampadosPorProducto', text, re.DOTALL)
if match:
    pass
