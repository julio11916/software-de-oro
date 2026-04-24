import sys
with open('templates/Usuarios/orden_personalizada/orden.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'id="paso1"' in l:
        print("FOUND PASO1 at line:", i)
        for j in range(i, i+150):
            if j < len(lines):
                print(str(j) + ": " + lines[j].strip())
        break
