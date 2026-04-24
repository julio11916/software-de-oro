import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

correct_func = r"""function finalizarOrden() {
            updateSummary();
            
            // Organize and format the summary data nicely
            let summaryText = "✅ ¡Personalización Completada!\\n\\n";
            
            summaryText += "--- DATOS DEL CLIENTE ---\\n";
            summaryText += "• Nombre: " + (state.nombre || "No especificado") + "\\n";
            summaryText += "• Correo: " + (state.correo || "No especificado") + "\\n";
            summaryText += "• Teléfono: " + (state.telefono || "No especificado") + "\\n";
            summaryText += "• Dirección: " + (state.direccion || "No especificada") + "\\n";
            
            summaryText += "\\n--- INFORMACIÓN INSTITUCIONAL ---\\n";
            summaryText += "• Identidad/Fuerza: " + formatLabel(state.identidad) + "\\n";
            if (state.rango) {
                summaryText += "• Rango: " + state.rango + "\\n";
            }
            if (state.anoContingencia) {
                summaryText += "• Año Contingencia: " + state.anoContingencia + "\\n";
            }
            
            summaryText += "\\n--- DETALLES DEL PRODUCTO ---\\n";
            summaryText += "• Producto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\\n";
            if (state.color) {
                summaryText += "• Color: " + formatLabel(state.color) + "\\n";
            }
            if (state.talla) {
                summaryText += "• Talla: " + state.talla + "\\n";
            }
            if (state.tecnica) {
                summaryText += "• Técnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresión") + "\\n";
            }
            if (state.estampado) {
                summaryText += "• Estampado: " + formatLabel(state.estampado) + "\\n";
            }
            
            alert(summaryText);
        }"""

# The exact match might fail due to newline types.
idx = text.find('function finalizarOrden() {')
if idx != -1:
    end_idx = text.find('}', idx)
    text = text[:idx] + correct_func + text[end_idx+1:]
    print("Fixed syntax error")
else:
    print("Could not find function")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
