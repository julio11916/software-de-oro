
import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# basic brace matching
lines = text.split('\n')
stack = []
for i, l in enumerate(lines):
    line = l.strip()
    if line.startswith('//'):
        continue
    for j, c in enumerate(l):
        if c == '{':
            stack.append( (i+1, j) )
        elif c == '}':
            if len(stack) > 0:
                stack.pop()
            else:
                print(f"Extra close brace on line {i+1} at col {j}")
                
if len(stack) > 0:
    print(f"Unclosed open brace: {stack[-1]}")
