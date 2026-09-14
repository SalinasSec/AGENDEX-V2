@echo off
chcp 65001 > nul
cls
echo ============================================================
echo   AGENDEX · INSTALADOR Y CONFIGURADOR LOCAL (FLASK + MYSQL)
echo ============================================================
echo.

echo [1/3] Verificando instalación de Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontró Python instalado en tu sistema o no está en el PATH.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python detectado correctamente.
echo.

echo [2/3] Instalando librerías requeridas (Flask, PyMySQL, etc.)...
python -m pip install --upgrade pip > nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Ocurrió un error al instalar las dependencias con pip.
    pause
    exit /b 1
)
echo [OK] Librerías instaladas con éxito.
echo.

echo [3/3] Configurando base de datos MySQL y procedimientos almacenados...
python database\init_db.py
if errorlevel 1 (
    echo [!] Hubo un detalle durante la configuración de la base de datos.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ¡TODO LISTO! PUEDES INICIAR AGENDEX EJECUTANDO:
echo       start.bat
echo ============================================================
echo.
pause
