"""
Script para reparar los tipos de datos en la base de datos de usuarios
Soluciona el error: Invalid value for dtype 'float64'
"""
import pandas as pd
import os

def reparar_base_datos():
    print("\n" + "="*60)
    print("🔧 REPARANDO BASE DE DATOS")
    print("="*60 + "\n")
    
    ruta_archivo = 'bd/usuarios.xlsx'
    
    if not os.path.exists(ruta_archivo):
        print("❌ No se encontró el archivo bd/usuarios.xlsx")
        return False
    
    try:
        # Cargar usuarios
        print("📂 Cargando bd/usuarios.xlsx...")
        usuarios = pd.read_excel(ruta_archivo)
        print(f"✓ {len(usuarios)} usuarios encontrados")
        
        # Convertir columnas de verificación a tipo string
        if 'verification_code' in usuarios.columns:
            print("\n🔄 Convirtiendo 'verification_code' a tipo string...")
            usuarios['verification_code'] = usuarios['verification_code'].fillna('').astype(str)
            # Limpiar valores como 'nan'
            usuarios.loc[usuarios['verification_code'] == 'nan', 'verification_code'] = ''
            print("✓ Columna 'verification_code' reparada")
        
        if 'verification_code_expiry' in usuarios.columns:
            print("🔄 Convirtiendo 'verification_code_expiry' a tipo string...")
            usuarios['verification_code_expiry'] = usuarios['verification_code_expiry'].fillna('').astype(str)
            usuarios.loc[usuarios['verification_code_expiry'] == 'nan', 'verification_code_expiry'] = ''
            print("✓ Columna 'verification_code_expiry' reparada")
        
        if 'email_verified' in usuarios.columns:
            print("🔄 Convirtiendo 'email_verified' a tipo booleano...")
            usuarios['email_verified'] = usuarios['email_verified'].fillna(False).astype(bool)
            print("✓ Columna 'email_verified' reparada")
        
        # Guardar cambios
        print("\n💾 Guardando cambios...")
        usuarios.to_excel(ruta_archivo, index=False)
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS REPARADA EXITOSAMENTE")
        print("="*60)
        print("\n🎯 Ahora puedes:")
        print("   1. Reiniciar el servidor: python app.py")
        print("   2. Intentar enviar el código de nuevo")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al reparar: {str(e)}")
        return False

if __name__ == '__main__':
    reparar_base_datos()
    input("\nPresiona ENTER para salir...")
