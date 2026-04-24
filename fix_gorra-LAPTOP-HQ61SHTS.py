import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = '            } else if (identidad === "armada") {\n                return isBack\n                    ? "/static/img/prendas/armada/gorra/espaldar-armada.png"\n                    : "/static/img/prendas/armada/gorra/image.png";\n            if (identidad === "ejercito") {'
start = text.find('? "/static/img/prendas/armada/gorra/espaldar-armada.png"')

if start != -1:
    end = text.find('if (identidad === "ejercito") {', start)
    if text[start:end].find('PAOLETA') == -1 and text[end - 20:end].find('}') == -1:
        insert = '''? "/static/img/prendas/armada/gorra/espaldar-armada.png"
                    : "/static/img/prendas/armada/gorra/image.png";
            }
        }

        // PAOLETA
        if (productName === "paoleta" || productName === "panoleta" || productName === "pañolete" || productName === "pa\\u00f1oleta" || productName === "pañoleta") {
            '''
        text = text[:start] + insert + text[end:]
        with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Fixed!")
    else:
        print("Seems already fixed or different!")
        print(text[start:end])
else:
    print("Target not found")
