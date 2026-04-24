import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "if (rangoOverlayImg) rangoOverlayImg.style.display = \"none\";" in line and "}" in lines[i+1]:
        # Add our custom logic after this line
        code = """
        const isPanoleta = ['pañoleta', 'panoleta', 'paoleta'].includes((state.producto || '').toLowerCase());
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
        new_lines.append(code)
        
with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
