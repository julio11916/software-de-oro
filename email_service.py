import random
import string
from flask_mail import Mail, Message
from datetime import datetime, timedelta

mail = Mail()

def generar_codigo_verificacion():
    """Genera un código de verificación de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def enviar_codigo_verificacion(email, codigo):
    """
    Envía un código de verificación al correo del usuario
    
    Args:
        email: Dirección de correo del destinatario
        codigo: Código de verificación de 6 dígitos
    
    Returns:
        True si se envió correctamente, False en caso contrario
    """
    try:
        msg = Message(
            subject='Código de Autenticación - Nachoher',
            sender='noreply@nachoher.com',
            recipients=[email]
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #3483fa 0%, #2968c8 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .code-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    text-align: center;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 30px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }}
                .message {{
                    color: #333;
                    line-height: 1.6;
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🔐</div>
                    <h1>Código de Autenticación</h1>
                </div>
                <div class="content">
                    <p class="message">
                        Hola,<br><br>
                        Has solicitado un código de autenticación para tu cuenta en <strong>Nachoher</strong>. 
                        Para continuar, ingresa el siguiente código:
                    </p>
                    
                    <div class="code-box">
                        {codigo}
                    </div>
                    
                    <p class="message">
                        Este código es válido por <strong>10 minutos</strong>. 
                        Si no solicitaste este código, puedes ignorar este correo de forma segura.
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong> Nunca compartas este código con nadie. 
                        Nuestro equipo nunca te pedirá este código por teléfono o correo.
                    </div>
                </div>
                <div class="footer">
                    <p>© 2026 Nachoher. Todos los derechos reservados.</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False
