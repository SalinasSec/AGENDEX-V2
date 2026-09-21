@echo off
cls
echo ============================================================
echo   INICIANDO AGENDEX (FLASK + MYSQL)
echo ============================================================
echo.
echo Abriendo navegador en http://localhost:5000 ...
start http://localhost:5000

echo.
echo Presiona Ctrl+C en esta ventana para detener el servidor.
echo.
python app.py
pause
