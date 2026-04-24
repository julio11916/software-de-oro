import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update colorMatriz for ejercito gorra to only have verde-claro
text = re.sub(r'("ejercito":\s*\{[\s\S]*?"gorra"\s*:\s*\[)"[^\]]*"(\])', r'\1"verde-claro"\2', text)

# 2. Add gorra to prendasTerminanPaso3 for ejercito, or modify the logic to check product and force 
# Note: Currently `prendasTerminanPaso3` is an array: ["rh", "gafete del nombre o apellido", "gafete", "presillas", "buso", "buso-manga-larga"]
# Wait, the user said "en las gorras del ejercito solo deja... y que finalice en el paso 3".
# In changeStep and bindNavigation, the logic for finishing at step 3 is based just on `productoActual`.

# Let's inspect `changeStep` and `bindNavigation` to see how to make "gorra" finish on step 3 specifically for "ejercito".

with open('check_gorra_ejercito.py', 'w') as f2:
    f2.write("print('Checking changeStep & bindNavigation')")

