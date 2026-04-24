import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = r'if \(productName === "camiseta" \|\| productName === "guerrera"\) \{([\s\S]*?\}'
m = re.search(target, text)
print(m.group(0))
