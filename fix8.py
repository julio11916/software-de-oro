import re
t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
new_txt = re.sub(r'(\}\s+else\s*\{\s*if\s*\(rangoOverlayImg\)\s*rangoOverlayImg\.style\.display\s*=\s*"none";\s*)\}\s*\}', r'\1}', t)
open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8').write(new_txt)
print("Regex replace applied")
