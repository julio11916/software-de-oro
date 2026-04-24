import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

def replacer_js(match):
    return r'/^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+$/.test(' + match.group(1) + ')'

c = re.sub(r'/[^/]+?test\((inputNombre\.value\.trim\(\)|inputRango\.value\.trim\(\))\)', replacer_js, c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    h = f.read()

def replacer_html(match):
    return r'pattern="[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+"'

h = re.sub(r'pattern="\[A-Za-z[^"]+?\\s\]\+"', replacer_html, h)

with open('templates/Usuarios/orden_personalizada/orden.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("done")
