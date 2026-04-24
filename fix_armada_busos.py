import re
with open("static/js/usuario/orden_personalizada.js", "r", encoding="utf-8") as f:
    text = f.read()

# Buso
text = text.replace('if (identidad === "gaula") return `/static/img/prendas/gaula/buso/buso_${colorName}.png`;', 'if (identidad === "gaula") return `/static/img/prendas/gaula/buso/buso_${colorName}.png`;\n            if (identidad === "armada") return `/static/img/prendas/armada/buso/buso_${colorName.replace("-claro","")}.png`;')

# Buso manga larga
text = text.replace('if (identidad === "gaula") return `/static/img/prendas/gaula/buso_manga_larga/buso_manga_larga_${colorName}.png`;', 'if (identidad === "gaula") return `/static/img/prendas/gaula/buso_manga_larga/buso_manga_larga_${colorName}.png`;\n            if (identidad === "armada") return `/static/img/prendas/armada/buso-manga-larga/buso_manga_larga_${colorName.replace("-claro","")}.png`;')

# Buso tactico
text = text.replace('if (identidad === "gaula") return `/static/img/prendas/gaula/buso_tactico/camisa_${colorName}.png`;', 'if (identidad === "gaula") return `/static/img/prendas/gaula/buso_tactico/camisa_${colorName}.png`;\n            if (identidad === "armada") return `/static/img/prendas/armada/buso-tactico/buso tactico ${colorName.replace("-claro","")}.png`;')

with open("static/js/usuario/orden_personalizada.js", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")