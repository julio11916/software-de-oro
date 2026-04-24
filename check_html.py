import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'gafete-overlay' in line or 'overlay-rango' in line or 'overlay-nombre' in line:
        print(f"{i}: {line.strip()}")
