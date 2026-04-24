import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        if (productName === "gorra") {
            if (color === "blanco") return null; // Sin blanco
            if (identidad === "ejercito") return `/static/img/prendas/ejercito/gorras/gorra_${colorName === 'negro' ? 'negra' : colorName}.png`;"""

replacement = """        if (productName === "gorra") {
            if (color === "blanco") return null; // Sin blanco
            if (identidad === "ejercito") return isBack ? `/static/img/prendas/ejercito/gorras/gorra-detras.png` : `/static/img/prendas/ejercito/gorras/gorra-frente.png`;"""

if target in text:
    print("Replacing getProductColorImage for gorra ejercito")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Target pattern in getProductColorImage not found.")
