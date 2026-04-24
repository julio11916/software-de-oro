import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'// Ajuste proporcional de tamaños[\s\S]*?divRango\.style\.fontSize = baseRangoSize \+ "px";\n\s*\}', text)
if m:
    print(m.group(0))
