import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                        if (identId === "policia" && !rangoFormat.includes("azul") && (state.color === "azul-noche" || state.color === "negro" || !state.color)) {
                            rangoFormat += " azul";
                        }"""

replacement = """                        if (identId === "policia" && !rangoFormat.includes("azul") && !rangoFormat.includes("verde")) {
                            if (state.color === "azul-noche" || state.color === "negro" || !state.color) {
                                rangoFormat += " azul";
                            } else if (state.color === "verde-claro") {
                                rangoFormat += " verde";
                            }
                        }"""

if target in text:
    print("Found target!")
    text = text.replace(target, replacement)
    with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("Target NOT found!")
