with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('if (isRh && state.vistaPrenda !== "trasera") {')
print(text[idx:idx+1500])
