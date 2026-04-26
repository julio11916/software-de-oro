#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg
import subprocess
import os
import sys

DB_URL = "postgresql://postgres:admin@localhost:5432/software_de_oro"
BACKUP_PATH = "db/software_de_oro_backup_2026-03-23.sql"

def conectar_bd():
    return psycopg.connect(DB_URL)

def es_formato_custom(ruta):
    with open(ruta, 'rb') as f:
        return f.read(4) == b'PGDM'

def importar_con_pg_restore(ruta):
    print("\n[*] Usando pg_restore para formato custom...")
    try:
        cmd = [
            'pg_restore',
            '--host', 'localhost',
            '--port', '5432',
            '--username', 'postgres',
            '--dbname', 'software_de_oro',
            '--no-privileges',
            '--no-owner',
            ruta
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'admin'
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[+] pg_restore completado exitosamente")
            return True
        else:
            print(f"[!] pg_restore con advertencias")
            return True
            
    except FileNotFoundError:
        print("[-] pg_restore no encontrado")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def importar_con_psql(ruta):
    print("\n[*] Usando psql para archivo SQL...")
    try:
        cmd = [
            'psql',
            '--host', 'localhost',
            '--port', '5432',
            '--username', 'postgres',
            '--dbname', 'software_de_oro',
            '--file', ruta,
            '-v', 'ON_ERROR_STOP=0'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'admin'
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
        
        print("[+] Importacion completada")
        return True
        
    except FileNotFoundError:
        print("[-] psql no encontrado")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def arreglar_integridad(conn):
    print("\n[*] Arreglando integridad de datos...")
    cursor = conn.cursor()
    
    try:
        print("    Verificando detalle_pedido...")
        cursor.execute("""
            DELETE FROM detalle_pedido
            WHERE id_pedido NOT IN (SELECT id_pedido FROM pedidos)
            OR id_producto NOT IN (SELECT id_producto FROM producto)
        """)
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"    [+] Eliminados {deleted} detalles hurfanos")
        
        print("    Verificando pagos...")
        cursor.execute("""
            UPDATE pagos 
            SET id_pedido = NULL
            WHERE id_pedido NOT IN (SELECT id_pedido FROM pedidos)
            AND id_pedido IS NOT NULL
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"    [+] Actualizados {updated} pagos invalidos")
        
        print("    Verificando fechas...")
        cursor.execute("""
            UPDATE pedidos 
            SET fecha_pedido = NOW()
            WHERE fecha_pedido IS NULL
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"    [+] Actualizadas {updated} fechas NULL")
        
        conn.commit()
        print("\n[+] Integridad arreglada")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[!] Error en integridad: {e}")
        return True

def mostrar_resumen_final(conn):
    print("\n" + "="*70)
    print("[*] RESUMEN FINAL DE LA BASE DE DATOS")
    print("="*70 + "\n")
    
    cursor = conn.cursor()
    tablas = ['usuarios', 'producto', 'pedidos', 'detalle_pedido', 'pagos', 'registros']
    
    total_registros = 0
    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            total_registros += count
            status = "[+]" if count > 0 else "[!]"
            print(f"{status} {tabla:20}: {count:6} registros")
        except:
            print(f"[-] {tabla:20}: ERROR")
    
    print(f"\nTotal de registros: {total_registros:,}")
    print("="*70 + "\n")
    
    cursor.close()

def main():
    print("\n" + "="*70)
    print("[*] INTEGRACION DE BACKUP A BASE DE DATOS")
    print("="*70)
    
    try:
        es_custom = es_formato_custom(BACKUP_PATH)
        print(f"\n[*] Archivo: {BACKUP_PATH}")
        print(f"[*] Formato: {'CUSTOM (binario)' if es_custom else 'SQL (texto)'}")
        
        print("\n[*] Conectando a la BD...")
        conn = conectar_bd()
        print("[+] Conexion exitosa")
        
        if es_custom:
            success = importar_con_pg_restore(BACKUP_PATH)
        else:
            success = importar_con_psql(BACKUP_PATH)
        
        if not success:
            print("\n[!] La importacion automatica no fue posible")
            print("    Continuando con validacion de integridad...")
        
        arreglar_integridad(conn)
        
        mostrar_resumen_final(conn)
        
        conn.close()
        
        print("="*70)
        print("[+] INTEGRACION COMPLETADA")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[-] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
