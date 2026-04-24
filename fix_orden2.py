import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Instead of relying on exact string match which could fail on newlines
# Let's use regex substitution

pattern = re.compile(r'divRango\.textContent = rangoFinal;\s*divNombre\.textContent = nombreFinal;')

new_overlay = '''                if (identId === 'ejercito') {
                    divRango.style.display = 'none';
                    divNombre.style.marginBottom = '2px'; // adjust spacing
                } else {
                    divRango.style.display = 'block';
                    divRango.textContent = rangoFinal;
                }
                divNombre.textContent = nombreFinal;'''

if pattern.search(text):
    text = pattern.sub(new_overlay, text)
    print("Successfully replaced text elements")
else:
    print("Could not find pattern to replace")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
