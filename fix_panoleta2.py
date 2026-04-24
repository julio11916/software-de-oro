import sys
import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Only keep the first block and remove subsequent identical blocks
block = """        const isPanoleta = ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase());
        if (isPanoleta && state.estampado && state.estampado.toLowerCase() === 'escudos') {
            const identId = state.identidad ? state.identidad.toLowerCase().trim() : 'policia';
            let escImgSrc = '';
            if (identId === 'ejercito') escImgSrc = '/static/img/estampados/ejercito/pañoleta/Escudos/ejercito.png';
            if (identId === 'gaula') escImgSrc = '/static/img/estampados/gaula/pañoleta/Escudos/gaula.png';
            if (identId === 'policia') escImgSrc = state.color === 'azul-noche' ? '/static/img/estampados/policia/pañoleta/Escudos/pañoleta azul.png' : '/static/img/estampados/policia/pañoleta/Escudos/pañoleta verde.png';
            
            if (escImgSrc) {
                imgEl.src = escImgSrc;
            }
        }
"""
index = text.find("const isPanoleta")
if index != -1:
    before = text[:index]
    after = text[index:]
    # Remove all subsequent occurrences
    after = after.replace(block, "")
    text = before + block + after

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("done")
