t = open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8').read()
idx = t.find('function getProductColorImage')
end = t.find('function updateTabsByProduct')
print(t[idx+2000:end].encode('ascii', 'replace').decode('ascii'))