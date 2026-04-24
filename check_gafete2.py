with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('// GAFETE')
print("Match 1 getProductImage:", text[idx1:idx1+800])

idx2 = text.find('// GAFETE', idx1+100)
if idx2 != -1:
    print("Match 2 getProductColorImage:", text[idx2:idx2+800])
