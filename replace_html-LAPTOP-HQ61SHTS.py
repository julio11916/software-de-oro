import re

with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Make sure contingency container is visible
h = re.sub(r'<div id="container-contingencia"\s*style="display:\s*none;">', r'<div id="container-contingencia">', h)

# Make sure talla container is visible
h = re.sub(r'<div id="container-talla"\s*style="display:\s*none;">', r'<div id="container-talla">', h)

with open('templates/Usuarios/orden_personalizada/orden.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("done html")
