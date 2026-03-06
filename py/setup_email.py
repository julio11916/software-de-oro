"""
Script para configurar rápidamente tu email de Gmail
Ejecuta este script y te guiará paso a paso
"""

import os

def configurar_email():
    print("\n" + "="*70)
    print("🔧 ASISTENTE DE CONFIGURACIÓN DE EMAIL")
    print("="*70 + "\n")
    
    print("Este asistente te ayudará a configurar Gmail para el envío de códigos.\n")
    
    # Paso 1
    print("📋 PASO 1: Tu correo de Gmail")
    print("-" * 70)
    email = input("Ingresa tu correo de Gmail: ").strip()
    
    if not email or '@gmail.com' not in email:
        print("❌ Error: Debe ser un correo de Gmail válido")
        return False
    
    # Paso 2
    print("\n📋 PASO 2: Contraseña de Aplicación")
    print("-" * 70)
    print("\n⚠️  IMPORTANTE: NO es tu contraseña normal de Gmail")
    print("Es una 'Contraseña de Aplicación' que debes generar en:")
    print("→ https://myaccount.google.com/apppasswords\n")
    
    print("Si no la tienes aún:")
    print("1. Ve al enlace de arriba")
    print("2. Activa 'Verificación en dos pasos' si no lo está")
    print("3. Crea una contraseña de aplicación: Correo → Otro → 'Nachoher'")
    print("4. Google te dará una contraseña como: abcd efgh ijkl mnop")
    print("5. Cópiala y pégala aquí\n")
    
    password = input("Pega aquí tu contraseña de aplicación (16 caracteres): ").strip()
    
    if not password or len(password) < 10:
        print("❌ Error: La contraseña parece incorrecta")
        return False
    
    # Confirmar
    print("\n" + "="*70)
    print("📝 RESUMEN DE CONFIGURACIÓN:")
    print("="*70)
    print(f"Correo:     {email}")
    print(f"Password:   {password[:4]}{'*' * (len(password)-4)}")
    print()
    
    confirmar = input("¿Es correcto? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("❌ Configuración cancelada")
        return False
    
    # Escribir archivo
    contenido = f"""# Configuración de Correo Electrónico
# Generado automáticamente por setup_email.py

# Configuración de Gmail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True

# Credenciales configuradas
MAIL_USERNAME = '{email}'
MAIL_PASSWORD = '{password}'
MAIL_DEFAULT_SENDER = '{email}'
"""
    
    try:
        with open('config_email.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("\n✅ ¡Configuración guardada exitosamente en config_email.py!")
        print("\n🎯 SIGUIENTE PASO:")
        print("   Ejecuta: python test_email.py")
        print("   Para probar que el correo funciona correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al guardar: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        configurar_email()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
    
    input("\n\nPresiona ENTER para salir...")
