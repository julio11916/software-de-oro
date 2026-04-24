import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function getProductColorImage')
if idx != -1:
    print(text[idx:idx+2500])
else:
    print("Not found")
