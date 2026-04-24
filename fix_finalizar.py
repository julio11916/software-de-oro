import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = '''function finalizarOrden() {
            updateSummary();
            alert("? Personalizacin completada. Resumen:\\n\\nNombre: " + state.nombre + "\\nRango: " + state.rango + "\\nDireccin: " + state.direccion + "\\nCorreo: " + state.correo + "\\nTelfono: " + state.telefono + "\\nAo contingencia: " + state.anoContingencia + "\\n\\nIdentidad: " + formatLabel(state.identidad) + "\\nTcnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresion") + "\\nProducto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\\nColor: " + formatLabel(state.color) + "\\nEstampado: " + (state.estampado ? formatLabel(state.estampado) : "Ninguno") + "\\nTalla: " + (state.talla || "No aplica"));
        }'''

new_func = '''function finalizarOrden() {
            updateSummary();
            
            // Organize and format the summary data nicely
            let summaryText = "✅ ¡Personalización Completada!\n\n";
            
            summaryText += "--- DATOS DEL CLIENTE ---\n";
            summaryText += "• Nombre: " + (state.nombre || "No especificado") + "\n";
            summaryText += "• Correo: " + (state.correo || "No especificado") + "\n";
            summaryText += "• Teléfono: " + (state.telefono || "No especificado") + "\n";
            summaryText += "• Dirección: " + (state.direccion || "No especificada") + "\n";
            
            summaryText += "\n--- INFORMACIÓN INSTITUCIONAL ---\n";
            summaryText += "• Identidad/Fuerza: " + formatLabel(state.identidad) + "\n";
            if (state.rango) {
                summaryText += "• Rango: " + state.rango + "\n";
            }
            if (state.anoContingencia) {
                summaryText += "• Año Contingencia: " + state.anoContingencia + "\n";
            }
            
            summaryText += "\n--- DETALLES DEL PRODUCTO ---\n";
            summaryText += "• Producto: " + (productLabels[state.producto] || formatLabel(state.producto)) + "\n";
            if (state.color) {
                summaryText += "• Color: " + formatLabel(state.color) + "\n";
            }
            if (state.talla) {
                summaryText += "• Talla: " + state.talla + "\n";
            }
            if (state.tecnica) {
                summaryText += "• Técnica: " + (state.tecnica === "bordado" ? "Bordado" : "Impresión") + "\n";
            }
            if (state.estampado) {
                summaryText += "• Estampado: " + formatLabel(state.estampado) + "\n";
            }
            
            alert(summaryText);
        }'''

text = text.replace(old_func, new_func)

# Fix encoding issue if there was any missing character matching
idx = text.find('function finalizarOrden() {')
if idx == -1:
    print("Could not match the function. Trying regex...")
    text = re.sub(r'function finalizarOrden\(\)\s*\{\s*updateSummary\(\);\s*alert\(.*?\);\s*\}', new_func, text, flags=re.DOTALL)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Updated finalizarOrden")
