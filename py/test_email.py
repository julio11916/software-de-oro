"""
Script de Prueba - Envío de Correo Electrónico
Este script te ayuda a verificar que tu configuración de Gmail funciona correctamente
"""
import py.config_email as config_email
from py.email_service import mail, enviar_codigo_verificacion
from flask import Flask

# Crear una app de prueba
app = Flask(__name__)
app.config['MAIL_SERVER'] = config_email.MAIL_SERVER
app.config['MAIL_PORT'] = config_email.MAIL_PORT
app.config['MAIL_USE_TLS'] = config_email.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config_email.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config_email.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config_email.MAIL_DEFAULT_SENDER

mail.init_app(app)

def test_email():
    """Prueba el envío de un correo de prueba"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CONFIGURACIÓN DE EMAIL")
    print("="*60 + "\n")
    
    # Verificar configuración
    print("📋 Configuración actual:")
    print(f"   Servidor: {config_email.MAIL_SERVER}:{config_email.MAIL_PORT}")
    print(f"   Usuario:  {config_email.MAIL_USERNAME}")
    print(f"   TLS:      {config_email.MAIL_USE_TLS}")
    print()
    
    # Verificar si la configuración está completa
    if config_email.MAIL_USERNAME == 'tu_correo@gmail.com':
        print("❌ ERROR: Debes configurar tu correo en config_email.py")
        print("   Edita el archivo y cambia 'tu_correo@gmail.com' por tu correo real")
        return False
    
    if 'xxxx' in config_email.MAIL_PASSWORD:
        print("❌ ERROR: Debes configurar la contraseña de aplicación en config_email.py")
        print("   Sigue las instrucciones en INSTRUCCIONES_GMAIL.md")
        return False
    
    # Solicitar correo de destino
    print("Por favor, ingresa el correo donde quieres recibir la prueba:")
    email_destino = input("Correo: ").strip()
    
    if not email_destino or '@' not in email_destino:
        print("❌ ERROR: Correo inválido")
        return False
    
    print(f"\n📧 Enviando correo de prueba a: {email_destino}")
    print("⏳ Por favor espera...")
    
    with app.app_context():
        try:
            # Generar código de prueba
            codigo = "123456"
            
            # Intentar enviar
            resultado = enviar_codigo_verificacion(email_destino, codigo)
            
            if resultado:
                print("\n✅ ¡CORREO ENVIADO EXITOSAMENTE!")
                print(f"   Revisa la bandeja de entrada de: {email_destino}")
                print("   (también revisa la carpeta de Spam)")
                print(f"\n   El código de prueba es: {codigo}")
                print("\n🎉 Tu configuración de Gmail está funcionando correctamente")
                return True
            else:
                print("\n❌ ERROR: No se pudo enviar el correo")
                print("   Revisa los mensajes de error arriba")
                print("\n💡 Posibles soluciones:")
                print("   1. Verifica que la contraseña de aplicación sea correcta")
                print("   2. Asegúrate de que la verificación en dos pasos esté activada")
                print("   3. Genera una nueva contraseña de aplicación")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("\n💡 Posibles causas:")
            print("   - Contraseña de aplicación incorrecta")
            print("   - Verificación en dos pasos no activada en Gmail")
            print("   - Problemas de conexión a Internet")
            print("   - Firewall bloqueando el puerto 587")
            return False

if __name__ == '__main__':
    print("\n🚀 Iniciando prueba de configuración de email...\n")
    test_email()
    input("\n\nPresiona ENTER para salir...")
