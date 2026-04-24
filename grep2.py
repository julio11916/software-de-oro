t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
lines = t.split('\n')
for i, line in enumerate(lines):
    if 'addEventListener' in line and (('btn-siguiente' in line) or ('paso' in line) or ('Atr' in line) or ('changeStep' in line)):
        for j in range(i-2, i+5):
            if 0 <= j < len(lines): print(f"{j}: {lines[j]}")
        print("-----")
