# Configuración de Gmail para Autenticación por Email

Este documento explica cómo configurar Gmail para que funcione el sistema de autenticación por código de correo electrónico.

## 🔐 Características del Sistema

✅ **Autent}
icación permanente**: Funciona siempre, incluso si el email ya está verificado
✅ **Código de 6 dígitos**: Generado aleatoriamente cada vez
✅ **Validez de 10 minutos**: Los códigos expiran automáticamente
✅ **Email profesional**: Con diseño responsive y seguro
✅ **Interfaz intuitiva**: Modal con dos pasos claramente diferenciados
✅ **Reenvío de código**: Opción para solicitar un nuevo código

## Paso 1: Crear una Contraseña de Aplicación de Gmail

Para que Flask-Mail pueda enviar correos desde tu cuenta de Gmail, necesitas crear una "Contraseña de aplicación":

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú izquierdo, selecciona "Seguridad"
3. En la sección "Acceso a Google", activa la "Verificación en dos pasos" (si no está activada)
4. Una vez activada, busca "Contraseñas de aplicaciones"
5. Selecciona:
   - Aplicación: "Correo"
   - Dispositivo: "Otro (nombre personalizado)" → escribe "Flask App"
6. Google generará una contraseña de 16 caracteres

## Paso 2: Configurar app.py

Abre el archivo `app.py` y actualiza las siguientes líneas (aproximadamente líneas 14-17):

```python
# Configuración de Flask-Mail para Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com'  # ← CAMBIAR: Tu correo de Gmail
app.config['MAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx'  # ← CAMBIAR: La contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'tu_correo@gmail.com'  # ← CAMBIAR: Tu correo de Gmail
```

### Ejemplo:
```python
app.config['MAIL_USERNAME'] = 'nachoher.shop@gmail.com'
app.config['MAIL_PASSWORD'] = 'abcd efgh ijkl mnop'  # Contraseña generada por Google
app.config['MAIL_DEFAULT_SENDER'] = 'nachoher.shop@gmail.com'
```

## Paso 3: Actualizar la Base de Datos

Ejecuta el script para agregar las columnas necesarias a la tabla de usuarios:

```bash
python update_db_verification.py
```

Este script agregará las columnas:
- `email_verified`: Estado de verificación del correo
- `verification_code`: Código de verificación temporal
- `verification_code_expiry`: Fecha de expiración del código

## Paso 4: Instalar Dependencias

Instala Flask-Mail:

```bash
pip install Flask-Mail
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

## Paso 5: Probar el Sistema

1. Inicia el servidor Flask:
   ```bash
   python app.py
   ```

2. Ve a tu perfil de usuario: http://localhost:5000/user/profile

3. Verás un botón que dice:
   - **"Validar"** si tu email aún no está verificado
   - **"Autenticar"** si tu email ya está verificado

4. El sistema:
   - Enviará un código de 6 dígitos a tu correo
   - Te pedirá que ingreses el código
   - Verificará el código y te autenticará
   - **FUNCIONA SIEMPRE**: No importa si ya verificaste tu email antes

## Usos del Sistema

Este sistema de autenticación por código sirve para:
- ✅ Verificar inicialmente la dirección de email
- ✅ Autenticación adicional cuando el usuario lo necesite
- ✅ Confirmar acciones importantes (puede extenderse)
- ✅ Validar la identidad del usuario en cualquier momento

## Solución de Problemas

### Error: "Username and Password not accepted"
- Verifica que la verificación en dos pasos esté activada
- Asegúrate de usar una "Contraseña de aplicación", no tu contraseña normal de Gmail
- Verifica que el correo en MAIL_USERNAME sea correcto

### No llega el correo
- Revisa la carpeta de Spam
- Verifica que el correo del remitente esté configurado correctamente
- Revisa los logs de la consola para ver si hay errores

### Error: "SMTPAuthenticationError"
- La contraseña de aplicación es incorrecta
- La verificación en dos pasos no está activada

## Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas el archivo `app.py` con tus credenciales a un repositorio público
- Considera usar variables de entorno para almacenar las credenciales:
  ```python
  import os
  app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
  app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
  ```

## Características Implementadas

✅ Generación de código de 6 dígitos aleatorio
✅ Envío de email con diseño profesional y responsive
✅ Código válido por 10 minutos
✅ Verificación de código con validación
✅ Interfaz modal intuitiva en el perfil
✅ **Funciona siempre, incluso si el email ya está verificado**
✅ Indicador visual diferente según estado de verificación
✅ Opción de reenviar código
✅ Mensajes de error claros y específicos
✅ Sistema de autenticación permanente disponible

## Comportamiento del Sistema

### Primera vez (Email no verificado):
1. Aparece mensaje: "Valida tu e-mail y mantén tu cuenta segura"
2. Botón azul: **"Validar"**
3. Al verificar correctamente: Email se marca como verificado

### Después de verificar:
1. Aparece mensaje: "✓ Tu correo está verificado - Autenticación disponible"
2. Botón verde: **"Autenticar"**
3. Al autenticar correctamente: Confirma la identidad del usuario
4. Puede usarse cuantas veces sea necesario

---

¿Necesitas ayuda? Revisa los logs en la consola del servidor Flask.
