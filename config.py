# -*- coding: utf-8 -*-
"""
Configuración de la aplicación Flask y conexión a MySQL para AgendEx.
"""

import os
from dotenv import load_dotenv
import pymysql

# Cargar variables de entorno desde .env si existe
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "agendex-liceo-secret-2024")
    
    # Parámetros de MySQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "agendex_db")

def get_db_connection():
    """
    Retorna una conexión activa a la base de datos MySQL con cursor DictCursor.
    """
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
