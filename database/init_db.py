#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgendEx - Inicializador Interactivo de Base de Datos MySQL
Ejecuta el esquema, datos iniciales y genera la configuración local (.env).
"""

import os
import sys
import getpass

try:
    import pymysql
except ImportError:
    print("\n[!] Falta la librería PyMySQL. Instalando dependencias...")
    os.system(f'"{sys.executable}" -m pip install pymysql python-dotenv cryptography')
    import pymysql


def leer_archivo_sql(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def ejecutar_script_sql(cursor, contenido_sql):
    # Separar comandos respetando DELIMITER para procedimientos almacenados
    lineas = contenido_sql.splitlines()
    delimiter = ";"
    buffer_sql = []

    for linea in lineas:
        linea_strip = linea.strip()
        if not linea_strip or linea_strip.startswith("--"):
            continue

        if linea_strip.upper().startswith("DELIMITER"):
            partes = linea_strip.split()
            if len(partes) > 1:
                delimiter = partes[1]
            continue

        buffer_sql.append(linea)

        texto_acumulado = "\n".join(buffer_sql)
        if texto_acumulado.strip().endswith(delimiter):
            # Quitar el delimitador del final
            query = texto_acumulado.strip()
            if query.endswith(delimiter):
                query = query[:-len(delimiter)].strip()

            if query:
                try:
                    cursor.execute(query)
                except Exception as e:
                    # Ignorar advertencias si la tabla ya existe
                    if "already exists" not in str(e).lower():
                        print(f"    [!] Nota en consulta: {e}")

            buffer_sql = []


def main():
    print("\n" + "=" * 60)
    print("  AGENDEX · CONFIGURADOR DE BASE DE DATOS MYSQL (LOCAL)")
    print("=" * 60)
    print("Este asistente creará la base de datos 'agendex_db', sus tablas,")
    print("los procedimientos de validación y la nómina inicial de usuarios.\n")

    # Solicitar parámetros
    host = input("Servidor MySQL [localhost]: ").strip() or "localhost"
    try:
        puerto_str = input("Puerto MySQL [3306]: ").strip() or "3306"
        puerto = int(puerto_str)
    except ValueError:
        puerto = 3306

    usuario = input("Usuario MySQL [root]: ").strip() or "root"
    password = getpass.getpass("Contraseña de MySQL (enter si no tiene): ")

    print(f"\n[+] Conectando a MySQL en {host}:{puerto} con usuario '{usuario}'...")

    try:
        conexion = pymysql.connect(
            host=host,
            port=puerto,
            user=usuario,
            password=password,
            charset="utf8mb4",
            autocommit=True
        )
    except Exception as err:
        print(f"\n[ERROR] No se pudo conectar a MySQL: {err}")
        print("Verifica que el servicio MySQL (XAMPP, WampServer o MySQL Service) esté encendido.")
        sys.exit(1)

    with conexion.cursor() as cursor:
        print("[+] Creando base de datos 'agendex_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS agendex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("USE agendex_db;")

        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_schema = os.path.join(directorio_actual, "schema.sql")
        ruta_datos = os.path.join(directorio_actual, "datos_iniciales.sql")

        print("[+] Ejecutando esquema relacional (tablas y procedimientos)...")
        if os.path.exists(ruta_schema):
            sql_schema = leer_archivo_sql(ruta_schema)
            ejecutar_script_sql(cursor, sql_schema)
            print("    [OK] Tablas y procedimientos almacenados creados.")
        else:
            print(f"    [!] No se encontró {ruta_schema}")

        print("[+] Cargando datos iniciales (cursos, asignaturas, profesores, alumnos)...")
        if os.path.exists(ruta_datos):
            sql_datos = leer_archivo_sql(ruta_datos)
            ejecutar_script_sql(cursor, sql_datos)
            print("    [OK] Datos iniciales insertados con éxito.")
        else:
            print(f"    [!] No se encontró {ruta_datos}")

    conexion.close()

    # Guardar archivo .env local para Flask
    directorio_raiz = os.path.dirname(directorio_actual)
    ruta_env = os.path.join(directorio_raiz, ".env")

    print(f"[+] Generando archivo de configuración local (.env)...")
    contenido_env = f"""# Configuración local de AgendEx (Flask + MySQL)
DB_HOST={host}
DB_PORT={puerto}
DB_USER={usuario}
DB_PASSWORD={password}
DB_NAME=agendex_db
SECRET_KEY=agendex_secret_key_{os.urandom(8).hex()}
PORT=5000
"""

    with open(ruta_env, "w", encoding="utf-8") as f:
        f.write(contenido_env)

    print("    [OK] Archivo .env configurado correctamente.")
    print("\n" + "=" * 60)
    print("  ¡INSTALACIÓN DE BASE DE DATOS COMPLETADA CON ÉXITO!")
    print("=" * 60)
    print("Ahora puedes iniciar la aplicación ejecutando:")
    print("   start.bat  (en Windows)  o  python app.py\n")


if __name__ == "__main__":
    main()
