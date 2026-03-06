"""
Script para agregar columnas de verificación de email a la tabla de usuarios
"""
import pandas as pd
import os

def actualizar_estructura_usuarios():
    """Agrega las columnas necesarias para la verificación de email"""
    
    ruta_archivo = 'bd/usuarios.xlsx'
    
    if os.path.exists(ruta_archivo):
        # Cargar usuarios existentes
        usuarios = pd.read_excel(ruta_archivo)
        
        # Agregar nuevas columnas si no existen
        if 'email_verified' not in usuarios.columns:
            usuarios['email_verified'] = False
            print("✓ Columna 'email_verified' agregada")
        
        if 'verification_code' not in usuarios.columns:
            usuarios['verification_code'] = ''
            print("✓ Columna 'verification_code' agregada")
        
        if 'verification_code_expiry' not in usuarios.columns:
            usuarios['verification_code_expiry'] = ''
            print("✓ Columna 'verification_code_expiry' agregada")
        
        # Guardar cambios
        usuarios.to_excel(ruta_archivo, index=False)
        print("\n✓ Estructura de la base de datos actualizada correctamente")
        print(f"Total de usuarios: {len(usuarios)}")
        
    else:
        print(f"❌ Error: No se encontró el archivo {ruta_archivo}")

if __name__ == '__main__':
    actualizar_estructura_usuarios()
