import sys
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# find updatePreview or similar
idx = text.find('function getProductImage')
print(text[idx:idx+1500])
