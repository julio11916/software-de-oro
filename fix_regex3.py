import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# use regex to find, but .replace to swap out the whole matched string
match_nombre = re.search(r'/[^/]+?test\(inputNombre\.value\.trim\(\)\)', c)
if match_nombre:
    c = c.replace(match_nombre.group(0), '/^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+$/.test(inputNombre.value.trim())')

match_rango = re.search(r'/[^/]+?test\(inputRango\.value\.trim\(\)\)', c)
if match_rango:
    c = c.replace(match_rango.group(0), '/^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+$/.test(inputRango.value.trim())')

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    h = f.read()
    
# replace the HTML pattern exactly
h = re.sub(r'pattern="[^"]+?"', 'pattern="[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+"', h)
with open('templates/Usuarios/orden_personalizada/orden.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("done")
