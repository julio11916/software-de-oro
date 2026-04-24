text = open('static/js/usuario/orden_personalizada.js', encoding='utf-8').read()
l, r, diffs = 0, 0, []
for i, line in enumerate(text.split('\n'), 1):
    l += line.count('{')
    r += line.count('}')
    diffs.append((i, l-r))
for i, diff in reversed(diffs):
    if diff == 0:
        print(f'Last 0 at line {i}')
        break
