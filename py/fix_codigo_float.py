"""
Script para limpiar códigos con .0 en la base de datos
"""
import pandas as pd
import os

DB_PATH = 'bd/usuarios.xlsx'

def fix_verification_codes():
    """Limpia los códigos de verificación que tienen .0"""
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encuentra {DB_PATH}")
        return
    
    print("🔧 Limpiando códigos de verificación...")
    
    # Cargar base de datos
    df = pd.read_excel(DB_PATH)
    
    # Convertir verification_code a string y limpiar
    if 'verification_code' in df.columns:
        df['verification_code'] = df['verification_code'].astype(str)
        df['verification_code'] = df['verification_code'].replace('nan', '')
        df['verification_code'] = df['verification_code'].str.replace('.0', '', regex=False)
        
        print(f"✅ Códigos limpiados")
        print("\nCódigos actuales:")
        for idx, row in df.iterrows():
            code = str(row['verification_code'])
            if code and code != '' and code != 'nan':
                print(f"   {row['email']}: '{code}' (longitud: {len(code)})")
    
    # Guardar
    df.to_excel(DB_PATH, index=False)
    print(f"\n✅ Base de datos actualizada: {DB_PATH}")

if __name__ == '__main__':
    fix_verification_codes()
