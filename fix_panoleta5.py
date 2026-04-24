import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

block = """
        // Escudos en pañoletas
        const isPanoleta = ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase());
        if (isPanoleta && state.estampado && state.estampado.toLowerCase() === 'escudos') {
            const identId = state.identidad ? state.identidad.toLowerCase().trim() : 'policia';
            let escImgSrc = '';
            if (identId === 'ejercito') escImgSrc = '/static/img/estampados/ejercito/pañoleta/Escudos/ejercito.png';
            if (identId === 'gaula') escImgSrc = '/static/img/estampados/gaula/pañoleta/Escudos/gaula.png';
            if (identId === 'policia') escImgSrc = state.color === 'azul-noche' ? '/static/img/estampados/policia/pañoleta/Escudos/pañoleta azul.png' : '/static/img/estampados/policia/pañoleta/Escudos/pañoleta verde.png';
            
            if (escImgSrc) {
                imgEl.src = escImgSrc;
                imgEl.style.mixBlendMode = "multiply";
            }
        }
"""

lines.insert(748, block)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("done")