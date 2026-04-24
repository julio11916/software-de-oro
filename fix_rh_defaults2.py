import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target_str = r'(\? "/static/img/prendas/ejercito/Rh/)rh_espaldar\.png"(\s*:\s*"/static/img/prendas/ejercito/Rh/)rh_defrente\.png";'
new_text = re.sub(target_str, r'\1espaldar.png"\2frende.png";', text)

if text != new_text:
    print("Replaced!")
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(new_text)
else:
    print("Not replaced!")
