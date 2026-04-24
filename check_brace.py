import sys
text = open('static/js/usuario/orden_personalizada.js', encoding='utf-8').read()
with open('bracet.txt','w') as f:
    i, l, r = 1, 0, 0
    for line in text.split('\n'):
        l += line.count('{')
        r += line.count('}')
        f.write(f'{i}: {l} {r}\n')
        i += 1
