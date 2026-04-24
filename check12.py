with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('// RH\n        if (productName === "rh") {')
print(text[idx:idx+1500])
