import re, base64

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Base64 for: const nombreValido = inputNombre && /^[A-Za-z·ÈÌÛ˙¡…Õ”⁄Ò—\s]+$/.test(inputNombre.value.trim());
# is: Y29uc3Qgbm9tYnJlVmFsaWRvID0gaW5wdXROb21icmUgJiYgL15bQS1aYS16w6HDocOtw7PDusOBw4nDjTDDmsOxw5Fcc10rJC8udGVzdChpbnB1dE5vbWJyZS52YWx1ZS50cmltKCkpOw==
repl_n = base64.b64decode('Y29uc3Qgbm9tYnJlVmFsaWRvID0gaW5wdXROb21icmUgJiYgL15bQS1aYS16w6HDocOtw7PDusOBw4nDjcOTw5rDsTDDkVxzbStkLy50ZXN0KGlucHV0Tm9tYnJlLnZhbHVlLnRyaW0oKSk7').decode('utf-8')

m_n = re.search(r'const nombreValido = inputNombre && .*?test\(inputNombre\.value\.trim\(\)\);', c)
if m_n:
    c = c.replace(m_n.group(0), 'const nombreValido = inputNombre && /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputNombre.value.trim());')

m_r = re.search(r'const rangoValido = inputRango && .*?test\(inputRango\.value\.trim\(\)\);', c)
if m_r:
    c = c.replace(m_r.group(0), 'const rangoValido = inputRango && /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputRango.value.trim());')

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    h = f.read()

m_h_n = re.search(r'id=\"input-nombre\".*?pattern=\"(.*?)\"', h, re.DOTALL)
if m_h_n:
    h = h.replace('pattern="' + m_h_n.group(1) + '"', 'pattern="[A-Za-z\u00C0-\u017F\s]+"')

m_h_r = re.search(r'id=\"input-rango\".*?pattern=\"(.*?)\"', h, re.DOTALL)
if m_h_r:
    h = h.replace('pattern="' + m_h_r.group(1) + '"', 'pattern="[A-Za-z\u00C0-\u017F\s]+"')

with open('templates/Usuarios/orden_personalizada/orden.html', 'w', encoding='utf-8') as f:
    f.write(h)

print("done")
