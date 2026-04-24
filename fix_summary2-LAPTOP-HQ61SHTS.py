import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Clean up any bad isEspecial and ensure we use the right logic
c = re.sub(r'const isEspecial = \[.*?\].includes\(\(state\.producto \|\| \"\"\)\.toLowerCase\(\)\);', 
           r'const isEspecial = ["rh", "presillas", "gafete", "gafete del nombre o apellido", "paoleta", "panoleta", "pa\\u00f1oleta", "gorra"].includes((state.producto || "").toLowerCase());', 
           c)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("done script2")
