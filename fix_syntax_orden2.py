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

pattern = r'function finalizarOrden\(\) \{.*?\n        \}(?:\n            if .*?alert\(summaryText\);\n        \})?'
# wait, the simplest is to just use a regular expression that replaces everything from `function finalizarOrden() {` down to `alert(summaryText);\n        }` exactly.

idx_start = text.find('function finalizarOrden() {')
idx_end = text.find('alert(summaryText);', idx_start)
idx_end = text.find('}', idx_end) + 1

if idx_start != -1 and idx_end != -1:
    text = text[:idx_start] + correct_func + text[idx_end:]
    print("Replaced successfully")
else:
    print("Failed to replace")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
