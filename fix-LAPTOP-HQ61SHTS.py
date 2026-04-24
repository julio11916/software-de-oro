import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    content = f.read()
import sys
content = re.sub(r'// Mostrar/ocultar.*?containerTalla\.style\.display = \"block\";\n\s*\}\n\s*\}', '', content, flags=re.DOTALL)
with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(content)
