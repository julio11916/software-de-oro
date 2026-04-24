from PIL import Image
import json

results = {}
for name in ['estampado 1.png', 'estampado1.png']:
    try:
        img = Image.open('static/img/estampados/gaula/pañoleta/Escudos/' + name).resize((10,10)).convert('RGB')
        colors = img.getcolors(100)
        colors.sort(key=lambda x: x[0], reverse=True)
        results[name] = colors[:2]
    except Exception as e:
        results[name] = str(e)

with open('out_colors_gaula.txt', 'w') as f:
    f.write(str(results))