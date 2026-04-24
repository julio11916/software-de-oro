import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'function validarPaso1Realtime\((?:.*?)\) \{(.*?)\} \/\/ End validarPaso1Realtime|if \(!state\.identidad\)', text, re.DOTALL)
val_body = text[text.find('function validarPaso1Realtime(mostrarAlerta = false) {'):text.find('function validarPaso2Realtime() {')]
print(val_body)
