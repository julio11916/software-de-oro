import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

m_n = re.search(r'const nombreValido = inputNombre && .*?test\(inputNombre\.value\.trim\(\)\);', c)
if m_n:
    c = c.replace(m_n.group(0), 'const nombreValido = inputNombre && /^[A-Za-z\\\\u00e1\\\\u00e9\\\\u00ed\\\\u00f3\\\\u00fa\\\\u00c1\\\\u00c9\\\\u00cd\\\\u00d3\\\\u00da\\\\u00f1\\\\u00d1\\\\s]+$/.test(inputNombre.value.trim());')

m_r = re.search(r'const rangoValido = inputRango && .*?test\(inputRango\.value\.trim\(\)\);', c)
if m_r:
    c = c.replace(m_r.group(0), 'const rangoValido = inputRango && /^[A-Za-z\\\\u00e1\\\\u00e9\\\\u00ed\\\\u00f3\\\\u00fa\\\\u00c1\\\\u00c9\\\\u00cd\\\\u00d3\\\\u00da\\\\u00f1\\\\u00d1\\\\s]+$/.test(inputRango.value.trim());')

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Replace any garbled pattern string carefully
m_h_n = re.search(r'id=\"input-nombre\".*?pattern=\"(.*?)\"', h, re.DOTALL)
if m_h_n:
    h = h.replace('pattern="' + m_h_n.group(1) + '"', 'pattern="[A-Za-z\\\\u00e1\\\\u00e9\\\\u00ed\\\\u00f3\\\\u00fa\\\\u00c1\\\\u00c9\\\\u00cd\\\\u00d3\\\\u00da\\\\u00f1\\\\u00d1\\\\s]+"')

m_h_r = re.search(r'id=\"input-rango\".*?pattern=\"(.*?)\"', h, re.DOTALL)
if m_h_r:
    h = h.replace('pattern="' + m_h_r.group(1) + '"', 'pattern="[A-Za-z\\\\u00e1\\\\u00e9\\\\u00ed\\\\u00f3\\\\u00fa\\\\u00c1\\\\u00c9\\\\u00cd\\\\u00d3\\\\u00da\\\\u00f1\\\\u00d1\\\\s]+"')

with open('templates/Usuarios/orden_personalizada/orden.html', 'w', encoding='utf-8') as f:
    f.write(h)
