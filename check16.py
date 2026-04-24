import sys
import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# remove multiline comments
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
# remove single line comments
text = re.sub(r'//.*', '', text)
# remove strings
text = re.sub(r'\"(\\.|[^\"])*\"', '\"\"', text)
text = re.sub(r'\'(\\.|[^\'])*\'', '\'\'', text)
text = re.sub(r'\`(\\.|[^\`])*\`', '\`\`', text)

b = 0
for i, c in enumerate(text):
    if c == '{':
        b += 1
    elif c == '}':
        b -= 1
        if b < 0:
            print('Extra close brace at global character offset', i)
            # Find line number
            lines = text[:i].split('\n')
            print(f'Line number: {len(lines)}')
            break
if b > 0:
    print('Missing close braces:', b)
if b == 0:
    print('Balanced!')