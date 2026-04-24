import re

with open(r'c:\Users\asus\OneDrive\Escritorio\software-de-oro\templates\Usuarios\orden_personalizada\orden.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

text = re.sub(r'\{\{.*?\}\}', 'orden_personalizada.js', text)
text = re.sub(r'\{%.*?%\}', '', text)

err_handler = '<script>window.onerror = function(m, u, l, c, e) { document.documentElement.innerHTML = "<h1 style=\\"color:red\\">ERR: " + m + " line " + l + "</h1>"; };</script>\n'
text = err_handler + text

with open(r'c:\Users\asus\OneDrive\Escritorio\software-de-oro\static\js\usuario\test_full.html', 'w', encoding='utf-8') as f:
    f.write(text)