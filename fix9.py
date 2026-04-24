t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = t.find('if (isRh && state.vistaPrenda !== "trasera") {')
end = t.find('else if (isGafete && state.vistaPrenda !== "trasera") {', idx)
print(t[idx:end])