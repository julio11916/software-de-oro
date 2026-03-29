#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg

try:
    conn = psycopg.connect('postgresql://postgres:admin@localhost:5432/software_de_oro')
    conn.autocommit = True
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("[*] VERIFICANDO ESTADO ACTUAL DE LA BASE DE DATOS")
    print("="*70 + "\n")

    # Obtener todas las tablas
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"[*] Tablas encontradas: {len(tables)}\n")

    total = 0
    for t in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {t}')
            c = cursor.fetchone()[0]
            total += c
            print(f"[+] {t:25}: {c:6} registros")
        except Exception as e:
            print(f"[-] {t:25}: ERROR")

    print(f"\n[*] TOTAL: {total:,} registros en toda la BD")
    print("="*70 + "\n")

    # Verificar integridad en pedidos
    print("[*] Verificando integridad...")
    try:
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE id_usuario IS NULL")
        orphaned_pedidos = cursor.fetchone()[0]
        if orphaned_pedidos > 0:
            print(f"    [!] {orphaned_pedidos} pedidos sin usuario (huérfanos)")
    except:
        pass
    
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM detalle_pedido d 
            WHERE NOT EXISTS (SELECT 1 FROM pedidos p WHERE p.id_pedido = d.id_pedido)
        """)
        orphaned_detalles = cursor.fetchone()[0]
        if orphaned_detalles > 0:
            print(f"    [!] {orphaned_detalles} detalles de pedido sin pedido padre")
    except:
        pass
    
    print("    [+] Verificación completada\n")

    print("="*70)
    print("[+] ESTADO DE LA BASE DE DATOS VERIFICADO")
    print("="*70 + "\n")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n[ERROR] {e}\n")
