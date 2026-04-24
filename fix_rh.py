import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") {
                return colorName === 'cafe' ? `/static/img/prendas/ejercito/Rh/rh_cafe.png` : `/static/img/prendas/ejercito/Rh/rh.verde.png`;
            }"""

replacement = """        // RH
        if (productName === "rh") {
            if (identidad === "ejercito") {
                const sign = state.modeloRh || "O+";
                const rhMap = {
                    "A+": "A+ verde.png",
                    "A-": "A- verde.png",
                    "AB+": "AB+ verde .png",
                    "AB-": "AB- verde.png",
                    "B+": "B+ verde .png",
                    "B-": "B- verde.png",
                    "O+": "O+ verde.png",
                    "O-": "O- verde.png"
                };
                return `/static/img/prendas/ejercito/Rh/${rhMap[sign] || 'O+ verde.png'}`;
            }"""

if target in text:
    print("Found!")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Not found")

