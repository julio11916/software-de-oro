import sys

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "const isPanoleta" in line:
        skip = True
        continue
    
    if skip:
        # Stop skipping if we hit the end of the block
        if "imgEl.src = escImgSrc;" in line and "}" in lines[i+1] and "}" in lines[i+2]:
            continue
        elif "imgEl.src = escImgSrc;" in lines[i-2]:
            skip = False
            continue
        continue
    
    new_lines.append(line)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
