@echo off
chcp 65001 > nul
cls
echo ============================================================
echo   INICIANDO AGENDEX (FLASK + MYSQL)
echo ============================================================
echo.
echo Abriendo navegador en http://127.0.0.1:5000 ...
start http://127.0.0.1:5000

echo.
echo Presiona Ctrl+C en esta ventana para detener el servidor.
echo.
python app.py
pause
