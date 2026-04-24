import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Re-write the validation lines cleanly
c = re.sub(r'const nombreValido = inputNombre && .*?test\(inputNombre\.value\.trim\(\)\);', r'const nombreValido = inputNombre && /^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+$/.test(inputNombre.value.trim());', c)
c = re.sub(r'const rangoValido = inputRango && .*?test\(inputRango\.value\.trim\(\)\);', r'const rangoValido = inputRango && /^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\s]+$/.test(inputRango.value.trim());', c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)
