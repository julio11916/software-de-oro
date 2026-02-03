import os
import sys
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================
print("=" * 60)
print("SOFTWARE DE ORO - Inicializando sistema")
print("=" * 60)

# Configurar rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
BD_DIR = os.path.join(BASE_DIR, 'bd')

# Crear directorios si no existen
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(BD_DIR, exist_ok=True)

# Ruta del archivo Excel principal
EXCEL_FILE = os.path.join(BD_DIR, 'base_datos.xlsx')
print(f"📁 Ruta base de datos: {EXCEL_FILE}")

# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================
def inicializar_base_datos():
    """Crea la base de datos Excel con tablas iniciales"""
    try:
        if not os.path.exists(EXCEL_FILE):
            print("🆕 Creando base de datos inicial...")
            
            # Usar ExcelWriter para crear múltiples hojas
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                # 1. TABLA USUARIOS
                usuarios_data = {
                    'id': [1, 2, 3],
                    'nombre': ['Juan Pérez', 'María García', 'Carlos López'],
                    'email': ['juan@email.com', 'maria@email.com', 'carlos@email.com'],
                    'telefono': ['555-0101', '555-0102', '555-0103'],
                    'fecha_registro': ['2024-01-15', '2024-01-16', '2024-01-17'],
                    'activo': [True, True, True]
                }
                pd.DataFrame(usuarios_data).to_excel(writer, sheet_name='usuarios', index=False)
                
                # 2. TABLA PRODUCTOS
                productos_data = {
                    'id': [101, 102, 103],
                    'nombre': ['Laptop Oro', 'Tablet Plata', 'Teléfono Diamante'],
                    'categoria': ['Electrónica', 'Electrónica', 'Electrónica'],
                    'precio': [1200.50, 450.75, 899.99],
                    'stock': [15, 32, 8],
                    'descripcion': ['Laptop de alta gama', 'Tablet empresarial', 'Teléfono flagship']
                }
                pd.DataFrame(productos_data).to_excel(writer, sheet_name='productos', index=False)
                
                # 3. TABLA VENTAS
                ventas_data = {
                    'id': [1001, 1002],
                    'id_usuario': [1, 2],
                    'id_producto': [101, 102],
                    'cantidad': [1, 2],
                    'total': [1200.50, 901.50],
                    'fecha_venta': ['2024-01-20', '2024-01-21']
                }
                pd.DataFrame(ventas_data).to_excel(writer, sheet_name='ventas', index=False)
                
                # 4. TABLA CONFIGURACIÓN (vacía)
                pd.DataFrame(columns=['clave', 'valor', 'descripcion']).to_excel(
                    writer, sheet_name='configuracion', index=False
                )
            
            print(f"✅ Base de datos creada: {EXCEL_FILE}")
            print("   - Tablas: usuarios, productos, ventas, configuracion")
            return True
            
        else:
            print("✅ Base de datos ya existe")
            return True
            
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def ver_estado_base_datos():
    """Muestra información de la base de datos"""
    try:
        if os.path.exists(EXCEL_FILE):
            excel_file = pd.ExcelFile(EXCEL_FILE)
            print(f"\n📊 ESTADO BASE DE DATOS:")
            print(f"   Archivo: {os.path.basename(EXCEL_FILE)}")
            print(f"   Tamaño: {os.path.getsize(EXCEL_FILE) / 1024:.2f} KB")
            print(f"   Tablas disponibles:")
            
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
                print(f"   • {sheet}: {len(df)} registros")
        else:
            print("⚠️  Base de datos no existe")
    except Exception as e:
        print(f"❌ Error leyendo base: {e}")

def crear_tabla_interactiva():
    """Prompt interactivo para crear nuevas tablas"""
    print("\n" + "=" * 50)
    print("📋 CREAR NUEVA TABLA")
    print("=" * 50)
    
    try:
        # Nombre de la tabla
        while True:
            nombre = input("Nombre de la tabla (sin espacios): ").strip()
            if nombre and ' ' not in nombre:
                break
            print("⚠️  Nombre inválido. Sin espacios por favor.")
        
        # Columnas
        print("\n💡 Ejemplo: id,nombre,edad,email")
        columnas_input = input("Columnas (separadas por coma): ").strip()
        
        if not columnas_input:
            print("⚠️  Debes especificar al menos una columna")
            return
        
        columnas = [col.strip() for col in columnas_input.split(',')]
        
        # Leer archivo Excel existente o crear nuevo
        if os.path.exists(EXCEL_FILE):
            # Modo append para añadir nueva hoja
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                nueva_tabla = pd.DataFrame(columns=columnas)
                nueva_tabla.to_excel(writer, sheet_name=nombre, index=False)
        else:
            # Crear archivo nuevo
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                nueva_tabla = pd.DataFrame(columns=columnas)
                nueva_tabla.to_excel(writer, sheet_name=nombre, index=False)
        
        print(f"\n✅ Tabla '{nombre}' creada exitosamente!")
        print(f"   Columnas: {', '.join(columnas)}")
        
        # Preguntar si agregar datos de ejemplo
        agregar_ejemplo = input("\n¿Agregar datos de ejemplo? (s/n): ").lower()
        if agregar_ejemplo == 's':
            agregar_datos_ejemplo(nombre, columnas)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def agregar_datos_ejemplo(nombre_tabla, columnas):
    """Agrega datos de ejemplo a una tabla nueva"""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=nombre_tabla)
        
        # Datos de ejemplo basados en columnas
        datos_ejemplo = {}
        for i, col in enumerate(columnas):
            if 'id' in col.lower():
                datos_ejemplo[col] = [1, 2, 3]
            elif 'nombre' in col.lower():
                datos_ejemplo[col] = ['Ejemplo 1', 'Ejemplo 2', 'Ejemplo 3']
            elif 'email' in col.lower():
                datos_ejemplo[col] = ['ej1@email.com', 'ej2@email.com', 'ej3@email.com']
            elif 'fecha' in col.lower():
                datos_ejemplo[col] = ['2024-01-01', '2024-01-02', '2024-01-03']
            else:
                datos_ejemplo[col] = ['Dato 1', 'Dato 2', 'Dato 3']
        
        nuevo_df = pd.DataFrame(datos_ejemplo)
        
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            nuevo_df.to_excel(writer, sheet_name=nombre_tabla, index=False)
        
        print(f"✅ 3 registros de ejemplo agregados a '{nombre_tabla}'")
        
    except Exception as e:
        print(f"⚠️  No se pudieron agregar datos de ejemplo: {e}")

# ============================================================================
# APLICACIÓN FLASK (INTERFAZ WEB)
# ============================================================================
app = Flask(__name__, template_folder=TEMPLATES_DIR)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    """Obtener todos los usuarios (API)"""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='usuarios')
        usuarios = df.fillna('').to_dict('records')
        return jsonify({'success': True, 'data': usuarios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    """Crear nuevo usuario"""
    try:
        data = request.json
        
        # Leer usuarios existentes
        df = pd.read_excel(EXCEL_FILE, sheet_name='usuarios')
        
        # Generar nuevo ID
        nuevo_id = df['id'].max() + 1 if not df.empty else 1
        
        nuevo_usuario = {
            'id': nuevo_id,
            'nombre': data.get('nombre', ''),
            'email': data.get('email', ''),
            'telefono': data.get('telefono', ''),
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'activo': True
        }
        
        # Agregar al DataFrame
        df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        
        # Guardar
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='usuarios', index=False)
        
        return jsonify({
            'success': True, 
            'message': 'Usuario creado exitosamente',
            'id': nuevo_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/dashboard')
def dashboard():
    """Página de dashboard"""
    try:
        stats = {}
        
        if os.path.exists(EXCEL_FILE):
            # Estadísticas de usuarios
            usuarios_df = pd.read_excel(EXCEL_FILE, sheet_name='usuarios')
            stats['total_usuarios'] = len(usuarios_df)
            stats['usuarios_activos'] = usuarios_df['activo'].sum() if 'activo' in usuarios_df.columns else 0
            
            # Estadísticas de productos
            productos_df = pd.read_excel(EXCEL_FILE, sheet_name='productos')
            stats['total_productos'] = len(productos_df)
            stats['valor_inventario'] = (productos_df['precio'] * productos_df['stock']).sum() if 'precio' in productos_df.columns else 0
            
            # Estadísticas de ventas
            ventas_df = pd.read_excel(EXCEL_FILE, sheet_name='ventas')
            stats['total_ventas'] = len(ventas_df)
            stats['ingresos_totales'] = ventas_df['total'].sum() if 'total' in ventas_df.columns else 0
            
        return render_template('dashboard.html', stats=stats)
        
    except Exception as e:
        return f"Error cargando dashboard: {str(e)}"

# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================
def mostrar_menu():
    """Muestra el menú principal del sistema"""
    print("\n" + "=" * 50)
    print("🏆 SOFTWARE DE ORO - MENÚ PRINCIPAL")
    print("=" * 50)
    print("1. 🚀 Iniciar servidor web (Flask)")
    print("2. 📊 Ver estado de base de datos")
    print("3. 📋 Crear nueva tabla")
    print("4. 📁 Ver contenido de una tabla")
    print("5. ❌ Salir")
    print("=" * 50)
    
    try:
        opcion = input("Selecciona una opción (1-5): ").strip()
        return opcion
    except KeyboardInterrupt:
        print("\n\n👋 Sesión terminada por el usuario")
        sys.exit(0)

def ver_contenido_tabla():
    """Muestra el contenido de una tabla específica"""
    try:
        if not os.path.exists(EXCEL_FILE):
            print("⚠️  La base de datos no existe")
            return
        
        excel_file = pd.ExcelFile(EXCEL_FILE)
        
        print("\n📋 TABLAS DISPONIBLES:")
        for i, sheet in enumerate(excel_file.sheet_names, 1):
            print(f"   {i}. {sheet}")
        
        try:
            seleccion = int(input("\nSelecciona número de tabla: "))
            if 1 <= seleccion <= len(excel_file.sheet_names):
                tabla_seleccionada = excel_file.sheet_names[seleccion - 1]
                df = pd.read_excel(EXCEL_FILE, sheet_name=tabla_seleccionada)
                
                print(f"\n📄 CONTENIDO DE '{tabla_seleccionada}':")
                print("=" * 60)
                print(df.to_string(index=False))
                print(f"\n📊 Total registros: {len(df)}")
                
                # Opción para exportar a CSV
                exportar = input("\n¿Exportar a CSV? (s/n): ").lower()
                if exportar == 's':
                    csv_file = os.path.join(BD_DIR, f"{tabla_seleccionada}.csv")
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    print(f"✅ Exportado a: {csv_file}")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Debes ingresar un número")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================
if __name__ == '__main__':
    # Inicializar base de datos
    if not inicializar_base_datos():
        print("❌ No se pudo inicializar la base de datos")
        sys.exit(1)
    
    # Ver estado inicial
    ver_estado_base_datos()
    
    # Bucle principal del menú
    while True:
        opcion = mostrar_menu()
        
        if opcion == '1':
            print("\n🚀 Iniciando servidor web...")
            print("🌐 Abre tu navegador en: http://127.0.0.1:5000")
            print("📝 Presiona Ctrl+C para detener el servidor\n")
            app.run(debug=True, port=5000, use_reloader=False)
            break
            
        elif opcion == '2':
            ver_estado_base_datos()
            
        elif opcion == '3':
            crear_tabla_interactiva()
            
        elif opcion == '4':
            ver_contenido_tabla()
            
        elif opcion == '5':
            print("\n👋 ¡Hasta pronto!")
            sys.exit(0)
            
        else:
            print("❌ Opción no válida. Intenta de nuevo.")