import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        if (productName === "rh") {
            if (identidad === "ejercito") {
                return isBack
                    ? "/static/img/prendas/ejercito/Rh/rh_espaldar.png"
                    : "/static/img/prendas/ejercito/Rh/rh_defrente.png";"""

replacement = """        if (productName === "rh") {
            if (identidad === "ejercito") {
                return isBack
                    ? "/static/img/prendas/ejercito/Rh/espaldar.png"
                    : "/static/img/prendas/ejercito/Rh/frende.png";"""

if target in text:
    print("Found! Replacing defaults.")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Target not found.")
