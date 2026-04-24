import re
with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'function changeStep\([\s\S]*?// function updatePanelLayout', text, re.DOTALL)
if m:
    print(m.group(0)[:1500])
