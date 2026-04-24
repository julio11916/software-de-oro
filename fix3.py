t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = t.find('Escudos en pañoletas')
print(t[idx-300:idx+300])