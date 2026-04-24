import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = r'if \(identidad === "ejercito"\) return `/static/img/prendas/ejercito/guerreras/guerrera_\$\{colorName\}\.png`;'
replacement = """if (identidad === "ejercito") return isBack ? `/static/img/prendas/ejercito/guerreras/guerrera-detras.png` : `/static/img/prendas/ejercito/guerreras/guerrera-frente.png`;"""

new_text = re.sub(target, replacement, text)

if text != new_text:
    print("Replaced!")
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(new_text)
else:
    print("Not replaced!")
