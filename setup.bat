@echo off
cls
echo ============================================================
echo   AGENDEX - INSTALADOR Y CONFIGURADOR LOCAL (FLASK + MYSQL)
echo ============================================================
echo.

echo [1/3] Verificando instalacion de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python instalado en el sistema o no esta en el PATH.
    echo Por favor instala Python 3.10 o superior marcando la casilla "Add Python to PATH".
    echo Descarga: https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python detectado correctamente.
echo.

echo [2/3] Instalando librerias requeridas (Flask, PyMySQL, etc.)...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Ocurrio un error al instalar las dependencias con pip.
    pause
    exit /b 1
)
echo [OK] Librerias instaladas con exito.
echo.

echo [3/3] Configurando base de datos MySQL y procedimientos...
python database\init_db.py
if errorlevel 1 (
    echo [!] Hubo un error durante la configuracion de la base de datos.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   TODO LISTO! PUEDES INICIAR AGENDEX EJECUTANDO: start.bat
echo ============================================================
echo.
pause
