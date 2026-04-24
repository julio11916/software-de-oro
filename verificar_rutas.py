#!/usr/bin/env python3
import os

base_path = r"c:\Users\asus\OneDrive\Escritorio\software-de-oro\static\img\prendas"

# Rutas que debe verificar
rutas_esperadas = [
    # BUSO
    "ejercito/buso/Buso_de_espalda_-removebg-preview.png",
    "ejercito/buso/Buso_de_frente-removebg-preview.png",
    "gaula/buso/espalda_gaula.png",
    "gaula/buso/defrente_gaula.png",
    "Policia/buso/espalda_policia.png",
    "Policia/buso/defrente_policia.png",
    # CAMISETA
    "ejercito/camisetas/Camisa_de_espalda-removebg-preview.png",
    "ejercito/camisetas/Camisa_de_frente-removebg-preview.png",
    "gaula/camiseta/camisa_de_espalda_gaula.png",
    "gaula/camiseta/Camisa_de_frente-gaula.png",
    "Policia/camisetas/camisa_de_espalda_policia.png",
    "Policia/camisetas/Camisa_de_frente-policia.png",
    # GORRA
    "ejercito/gorras/gorra_de_espalda-removebg-preview.png",
    "ejercito/gorras/gorra_de_frente-removebg-preview.png",
    "gaula/gorras/gorra_de_espalda-gaula.png",
    "gaula/gorras/gorra_de_frente-rgaula.png",
    "Policia/gorras/gorra_de_espalda-gaula.png",
    "Policia/gorras/gorra_de_frente-rgaula.png",
    # PAÑOLETA
    "ejercito/pañoletas/panoleta_espalda.png",
    "ejercito/pañoletas/panoleta_frente.png",
    "Policia/Pañoletas/panoleta_espalda_gaula.png",
    "Policia/Pañoletas/panoleta_frente_gaula.png",
]

print("✓ Verificando rutas de imágenes...\n")

encontradas = 0
no_encontradas = []

for ruta in rutas_esperadas:
    full_path = os.path.join(base_path, ruta)
    exists = os.path.exists(full_path)
    status = "✓" if exists else "✗"
    print(f"{status} {ruta}")
    
    if exists:
        encontradas += 1
    else:
        no_encontradas.append(ruta)

print(f"\n{'='*60}")
print(f"Total: {encontradas}/{len(rutas_esperadas)} archivos encontrados")

if no_encontradas:
    print(f"\n❌ Archivos NO encontrados ({len(no_encontradas)}):")
    for ruta in no_encontradas:
        print(f"  - {ruta}")
else:
    print("\n✓ ¡TODAS las imágenes están presentes!")
