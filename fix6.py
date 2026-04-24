import re
t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
text = re.sub(r'/\*.*?\*/', '', t, flags=re.DOTALL)
text = re.sub(r'//.*', '', text)
text = re.sub(r'\"(\\.|[^\"])*\"', '\"\"', text)
text = re.sub(r'\'(\\.|[^\'])*\'', '\'\'', text)
text = re.sub(r'\`(\\.|[^\`])*\`', '\`\`', text)
idx = text.find('function updateSummary()')
end = text.find('function updateStepIndicators()')

sub = text[idx:end]
lines = sub.split('\n')
b = 0
for i, line in enumerate(lines):
    b += line.count('{') - line.count('}')
    print(f"{i}: {b} | {line.strip()}")