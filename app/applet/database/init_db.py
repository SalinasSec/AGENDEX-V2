#!/usr/bin/env python3
"""
AgendEx - Instalador y Configurador de Base de Datos MySQL
Liceo Industrial Bicentenario RBL

Crea la base de datos 'agendex_db', sus tablas y datos iniciales,
y genera el archivo .env de configuración para ejecutar en local.
"""

import os
import sys
import getpass
import subprocess

# Asegurar dependencias necesarias
try:
    import pymysql
except ImportError:
    print("[*] Instalando paquete pymysql...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "cryptography"])
    import pymysql


def ejecutar_archivo_sql(cursor, ruta_archivo):
    """Lee y ejecuta un archivo .sql sentencia por sentencia."""
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Separar por punto y coma ignorando comentarios de línea
    comandos = []
    buffer = []
    for linea in contenido.splitlines():
        linea_strip = linea.strip()
        if not linea_strip or linea_strip.startswith("--"):
            continue
        buffer.append(linea)
        if linea_strip.endswith(";"):
            comandos.append("\n".join(buffer))
            buffer = []

    for sql in comandos:
        sql_limpio = sql.strip()
        if sql_limpio:
            try:
                cursor.execute(sql_limpio)
            except Exception as e:
                # Ignorar si tabla ya existe
                if "already exists" not in str(e).lower():
                    print(f"    [!] Detalle: {e}")


def main():
    print("\n" + "=" * 55)
    print("   AGENDEX · INSTALADOR DE BASE DE DATOS LOCAL")
    print("=" * 55)
    print("Este script configurará la base de datos MySQL local")
    print("y creará los datos necesarios para iniciar el sistema.\n")

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

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_schema = os.path.join(directorio_actual, "schema.sql")
    ruta_datos = os.path.join(directorio_actual, "datos_iniciales.sql")
    directorio_raiz = os.path.dirname(directorio_actual)
    ruta_env = os.path.join(directorio_raiz, ".env")

    with conexion.cursor() as cursor:
        print("[+] Creando base de datos 'agendex_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS agendex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("USE agendex_db;")

        print("[+] Creando tablas del sistema...")
        if os.path.exists(ruta_schema):
            ejecutar_archivo_sql(cursor, ruta_schema)
            print("    [OK] Tablas creadas correctamente.")
        else:
            print(f"    [!] No se encontró {ruta_schema}")

        print("[+] Insertando datos iniciales (cursos, asignaturas, profesores, alumnos y usuarios)...")
        if os.path.exists(ruta_datos):
            ejecutar_archivo_sql(cursor, ruta_datos)
            print("    [OK] Datos iniciales cargados con éxito.")
        else:
            print(f"    [!] No se encontró {ruta_datos}")

    conexion.close()

    # Generar archivo .env local
    print("[+] Generando archivo de configuración local (.env)...")
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

    print("\n" + "=" * 55)
    print("   ¡INSTALACIÓN COMPLETADA CON ÉXITO!")
    print("=" * 55)
    print("Para iniciar el servidor local ejecuta:")
    print("   start.bat   (en Windows)  o  python app.py\n")


if __name__ == "__main__":
    main()
