import re

with open('static/js/usuario/orden_personalizada.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the color matrix so "gafete del nombre o apellido" is included

old_ejercito = '''                "gafete": ["dorado", "verde-claro"],'''
new_ejercito = '''                "gafete": ["dorado", "verde-claro"],
                "gafete del nombre o apellido": ["dorado", "verde-claro"],'''

old_gaula = '''                "gafete": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],'''
new_gaula = '''                "gafete": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],
                "gafete del nombre o apellido": ["blanco", "negro", "verde-claro", "beiches", "dorado", "cafe", "azul-noche"],'''

text = text.replace(old_ejercito, new_ejercito)
text = text.replace(old_gaula, new_gaula)

# Wait! Did I make "Rango" optional in paso 1 for "Ejército" "Gafete"?
# No, because Step 1 happens BEFORE they select "Ejército" and "Gafete del nombre o apellido".
# So they MUST type something in Rango if they use Step 1.
# I will change the prompt to NOT require Rango if it's left empty?
# Wait! Does the user say "aplica la imagen de frente en el gafete y solo el nombre no implementes el rango es este gafete del ejercito"?
# The user wants NO RANGO on the Gafete.
# If they leave "Rango" empty in Step 1, they CANNOT ADVANCE.
# Let's MAKE RANGO COMPLETELY OPTIONAL in Step 1!!!
# That's the only way they can gracefully skip it!

old_rango_valido = '''        // Validar rango: solo letras y espacios (incluye acentos y eñes)       
        const rangoValido = inputRango && /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputRango.value.trim());
        if (!rangoValido) { valid = false; mensajeAlerta += "- Rango (solo letras).\\n"; }'''

new_rango_valido = '''        // Validar rango: opcional, pero si lo ingresa, debe ser solo letras
        let rangoValido = true;
        if (inputRango && inputRango.value.trim() !== '') {
            rangoValido = /^[A-Za-z\u00C0-\u017F\s]+$/.test(inputRango.value.trim());
        }
        if (!rangoValido) { valid = false; mensajeAlerta += "- Rango (solo letras).\\n"; }'''

text = text.replace(old_rango_valido, new_rango_valido)

with open('static/js/usuario/orden_personalizada.js', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Updated matrix and step 1 validation!")
