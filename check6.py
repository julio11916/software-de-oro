import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function updatePreview(')
if idx != -1:
    print(text[idx:idx+1500])
else:
    idx2 = text.find('// Update Preview')
    if idx2 != -1:
        print(text[idx2:idx2+1500])
    else:
        print("updatePreview not found")
