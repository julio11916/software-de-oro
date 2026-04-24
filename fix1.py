text = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = text.find('if (state.identidad === "policia" && (state.color === "azul-noche" || state.color === "negro"))')
print(text[idx-200:idx+200])