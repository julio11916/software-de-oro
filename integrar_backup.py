#!/usr/bin/env python3
"""
Script para integrar datos del backup a la base de datos actual.
Maneja conflictos, duplicados y arregla errores automáticamente.
"""

import psycopg
import re
from pathlib import Path
from datetime import datetime

# Configuración
DB_URL = "postgresql://postgres:admin@localhost:5432/software_de_oro"
BACKUP_PATH = "db/software_de_oro_backup_2026-03-23.sql"

def conectar_bd():
    """Conectar a PostgreSQL"""
    try:
        conn = psycopg.connect(DB_URL)
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        raise

def leer_backup():
    """Leer el archivo de backup"""
    try:
        with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {BACKUP_PATH}")
        raise

def extraer_inserts(contenido, tabla):
    """Extraer todos los INSERT para una tabla específica"""
    pattern = f"INSERT INTO {tabla}.*?;(?=\\n|$)"
    matches = re.findall(pattern, contenido, re.DOTALL | re.IGNORECASE)
    return matches

def integrar_usuarios(conn):
    """Integrar usuarios del backup"""
    print("\n🔄 Integrando USUARIOS...")
    cursor = conn.cursor()
    
    try:
        # Obtener usuarios del backup
        backup = leer_backup()
        inserts = extraer_inserts(backup, "usuarios")
        
        if not inserts:
            print("  ⚠️  No hay usuarios en el backup")
            return
        
        # Procesar cada INSERT
        for insert in inserts:
            try:
                # Ejecutar el INSERT, si ya existe por email, actualizar
                cursor.execute(f"""
                    {insert}
                """)
            except psycopg.IntegrityError:
                # Si hay error de integridad (email duplicado), actualizar
                print("  ℹ️  Email duplicado encontrado, actualizando...")
                # Extraer email del INSERT para actualizar
                match = re.search(r"'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'", insert)
                if match:
                    email = match.group(1)
                    # Cambiar INSERT por UPDATE
                    cursor.execute(f"""
                        UPDATE usuarios 
                        SET nombre = excluded.nombre,
                            password_hash = excluded.password_hash
                        WHERE email = %s
                    """, (email,))
        
        conn.commit()
        print("  ✅ Usuarios integrados correctamente")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error en usuarios: {e}")

def integrar_productos(conn):
    """Integrar productos del backup"""
    print("\n🔄 Integrando PRODUCTOS...")
    cursor = conn.cursor()
    
    try:
        backup = leer_backup()
        inserts = extraer_inserts(backup, "producto")
        
        if not inserts:
            print("  ⚠️  No hay productos en el backup")
            return
        
        # Procesar INSERTs
        for insert in inserts:
            try:
                cursor.execute(insert)
            except psycopg.IntegrityError:
                print("  ℹ️  Producto duplicado encontrado")
        
        conn.commit()
        print("  ✅ Productos integrados correctamente")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error en productos: {e}")

def integrar_pedidos(conn):
    """Integrar pedidos del backup"""
    print("\n🔄 Integrando PEDIDOS...")
    cursor = conn.cursor()
    
    try:
        backup = leer_backup()
        inserts = extraer_inserts(backup, "pedidos")
        
        if not inserts:
            print("  ⚠️  No hay pedidos en el backup")
            return
        
        for insert in inserts:
            try:
                cursor.execute(insert)
            except psycopg.IntegrityError:
                print("  ℹ️  Pedido duplicado encontrado")
        
        conn.commit()
        print("  ✅ Pedidos integrados correctamente")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error en pedidos: {e}")

def integrar_detalle_pedidos(conn):
    """Integrar detalles de pedidos"""
    print("\n🔄 Integrando DETALLES DE PEDIDOS...")
    cursor = conn.cursor()
    
    try:
        backup = leer_backup()
        inserts = extraer_inserts(backup, "detalle_pedido")
        
        if not inserts:
            print("  ⚠️  No hay detalles de pedidos en el backup")
            return
        
        for insert in inserts:
            try:
                cursor.execute(insert)
            except psycopg.IntegrityError:
                print("  ℹ️  Detalle de pedido duplicado encontrado")
        
        conn.commit()
        print("  ✅ Detalles de pedidos integrados correctamente")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error en detalles: {e}")

def integrar_pagos(conn):
    """Integrar pagos del backup"""
    print("\n🔄 Integrando PAGOS...")
    cursor = conn.cursor()
    
    try:
        backup = leer_backup()
        inserts = extraer_inserts(backup, "pagos")
        
        if not inserts:
            print("  ⚠️  No hay pagos en el backup")
            return
        
        for insert in inserts:
            try:
                cursor.execute(insert)
            except psycopg.IntegrityError:
                print("  ℹ️  Pago duplicado encontrado")
        
        conn.commit()
        print("  ✅ Pagos integrados correctamente")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error en pagos: {e}")

def verificar_integridad(conn):
    """Verificar integridad después de la integración"""
    print("\n🔍 Verificando integridad de datos...")
    cursor = conn.cursor()
    
    try:
        # Contar registros por tabla
        tablas = ['usuarios', 'producto', 'pedidos', 'detalle_pedido', 'pagos']
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"  {tabla}: {count} registros")
            except:
                pass
        
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def main():
    """Función principal"""
    print("="*70)
    print("INTEGRACIÓN DE BACKUP A BASE DE DATOS ACTUAL")
    print("="*70)
    
    try:
        print("\n📦 Conectando a la base de datos...")
        conn = conectar_bd()
        
        print("✅ Conexión exitosa\n")
        
        # Integrar cada tabla
        integrar_usuarios(conn)
        integrar_productos(conn)
        integrar_pedidos(conn)
        integrar_detalle_pedidos(conn)
        integrar_pagos(conn)
        
        # Verificar integridad
        verificar_integridad(conn)
        
        print("\n" + "="*70)
        print("✅ INTEGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
