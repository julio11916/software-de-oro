import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update ejercito.rh to be only ["verde-claro"]
text = re.sub(r'("rh"\s*:\s*\[)\s*"verde-claro"\s*,\s*"cafe"\s*(\])', r'\1"verde-claro"\2', text)
text = re.sub(r'("rh"\s*:\s*\[)\s*"cafe"\s*,\s*"verde-claro"\s*(\])', r'\1"verde-claro"\2', text)

# 2. Update ejercito.panoleta to be only ["verde-claro"] (for ejercito only)
ejercito_block_match = re.search(r'("ejercito"\s*:\s*\{)(.*?)(\}\s*,\s*"policia")', text, re.DOTALL)
if ejercito_block_match:
    ej_block = ejercito_block_match.group(2)
    ej_block = re.sub(r'("paoleta"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    ej_block = re.sub(r'("panoleta"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    ej_block = re.sub(r'("pañoleta"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    ej_block = re.sub(r'("gorra"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    
    # "guerrera" en ejercito? Let's add it if missing, or correct if exists
    if '"guerrera"' in ej_block:
        ej_block = re.sub(r'("guerrera"\s*:\s*\[)[^\]]*(\])', r'\1"verde-claro"\2', ej_block)
    else:
        # Add it right after gorra
        ej_block = ej_block.replace('"gorra": ["verde-claro"],', '"gorra": ["verde-claro"],\n                "guerrera": ["verde-claro"],')
    
    new_text = text[:ejercito_block_match.start(2)] + ej_block + text[ejercito_block_match.end(2):]
    text = new_text

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Colors updated.")
