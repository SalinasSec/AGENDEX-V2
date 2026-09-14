@echo off
chcp 65001 >nul
echo ============================================
echo   AgendEx - Sistema de Evaluaciones
echo ============================================
echo.
if not exist ".venv" (
    echo [INFO] Ejecutando setup por primera vez...
    call setup.bat
    exit /b
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo Iniciando servidor Flask en http://localhost:5000
echo Presiona Ctrl+C para detener.
echo.
start "" http://localhost:5000
python app.py
