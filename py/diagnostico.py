"""
Script de diagnóstico rápido
Verifica que el código de verificación se guarde y compare correctamente
"""
import pandas as pd
import os

print("\n" + "="*60)
print("🔍 DIAGNÓSTICO DEL SISTEMA DE VERIFICACIÓN")
print("="*60 + "\n")

# Verificar archivo
if not os.path.exists('bd/usuarios.xlsx'):
    print("❌ Error: No existe bd/usuarios.xlsx")
    exit()

# Cargar usuarios
usuarios = pd.read_excel('bd/usuarios.xlsx')

# Verificar columnas
print("📋 Columnas encontradas:")
for col in usuarios.columns:
    print(f"   - {col} ({usuarios[col].dtype})")

# Verificar datos de verificación
print("\n📧 Usuarios con códigos de verificación:")
if 'verification_code' in usuarios.columns:
    usuarios_con_codigo = usuarios[usuarios['verification_code'].notna() & (usuarios['verification_code'] != '')]
    if len(usuarios_con_codigo) > 0:
        for idx, user in usuarios_con_codigo.iterrows():
            print(f"\n   Usuario: {user['email']}")
            print(f"   Código: '{user['verification_code']}' (tipo: {type(user['verification_code'])})")
            print(f"   Longitud: {len(str(user['verification_code']))}")
            print(f"   Expira: {user.get('verification_code_expiry', 'N/A')}")
            print(f"   Verificado: {user.get('email_verified', 'N/A')}")
    else:
        print("   ℹ️ No hay códigos activos en este momento")
else:
    print("   ❌ Columna 'verification_code' no existe")

print("\n" + "="*60)
print("✅ Diagnóstico completado")
print("="*60 + "\n")
