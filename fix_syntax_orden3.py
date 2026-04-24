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

# Find the end of document or next function. Wait, the `finalizarOrden` was literally the last function in this script or is there something else below it?
last_alert = text.rfind('alert(summaryText);')
last_bracket = text.find('}', last_alert)

start_idx = text.find('function finalizarOrden() {')

if start_idx != -1 and last_bracket != -1:
    text = text[:start_idx] + correct_func + text[last_bracket+1:]
    print("Replaced completely!")
else:
    print("Failed")

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
