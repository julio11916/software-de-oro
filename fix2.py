import re
t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = t.find('            } else {\n                if (rangoOverlayImg) rangoOverlayImg.style.display = "none";')
if idx != -1:
    print(t[idx-200:idx+400])
