@echo off
chcp 65001 >nul
echo ============================================
echo   AgendEx - Configuracion e Instalacion
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

REM Crear entorno virtual
if not exist ".venv" (
    echo [1/4] Creando entorno virtual...
    python -m venv .venv
) else (
    echo [1/4] Entorno virtual ya existe.
)

REM Activar y actualizar pip
echo [2/4] Actualizando pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q

REM Instalar dependencias
echo [3/4] Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

REM Crear base de datos
echo.
echo [4/4] Creando la base de datos en MySQL...
echo.

REM --- Buscar mysql.exe automaticamente ---
set "MYSQL_EXE="

REM 1) Ya esta en el PATH?
where mysql >nul 2>&1
if not errorlevel 1 set "MYSQL_EXE=mysql"

REM 2) Preguntarle al Registro de Windows donde quedo instalado
REM    (asi es como el propio instalador de MySQL lo anota; funciona
REM    sin importar en que carpeta o version lo hayan instalado)
if not defined MYSQL_EXE (
    for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\MySQL AB" /s /v Location 2^>nul ^| findstr /i "Location"') do (
        if exist "%%B\bin\mysql.exe" set "MYSQL_EXE=%%B\bin\mysql.exe"
    )
)
if not defined MYSQL_EXE (
    for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\MySQL AB" /s /v Location 2^>nul ^| findstr /i "Location"') do (
        if exist "%%B\bin\mysql.exe" set "MYSQL_EXE=%%B\bin\mysql.exe"
    )
)

REM 3) Carpetas tipicas de instalacion (cualquier version)
if not defined MYSQL_EXE (
    for /d %%D in ("C:\Program Files\MySQL\MySQL Server *") do (
        if exist "%%D\bin\mysql.exe" set "MYSQL_EXE=%%D\bin\mysql.exe"
    )
)
if not defined MYSQL_EXE (
    for /d %%D in ("C:\Program Files (x86)\MySQL\MySQL Server *") do (
        if exist "%%D\bin\mysql.exe" set "MYSQL_EXE=%%D\bin\mysql.exe"
    )
)

REM 4) Paquetes tipo XAMPP/WAMP/Laragon, por si MySQL vino incluido ahi
if not defined MYSQL_EXE if exist "C:\xampp\mysql\bin\mysql.exe" set "MYSQL_EXE=C:\xampp\mysql\bin\mysql.exe"
if not defined MYSQL_EXE (
    for /d %%D in ("C:\wamp64\bin\mysql\mysql*") do (
        if exist "%%D\bin\mysql.exe" set "MYSQL_EXE=%%D\bin\mysql.exe"
    )
)
if not defined MYSQL_EXE (
    for /d %%D in ("C:\laragon\bin\mysql\mysql-*") do (
        if exist "%%D\bin\mysql.exe" set "MYSQL_EXE=%%D\bin\mysql.exe"
    )
)

REM 5) Ultimo recurso: busqueda amplia en todo Program Files (mas lenta)
if not defined MYSQL_EXE (
    echo Buscando mysql.exe en el disco, un momento...
    for /f "delims=" %%F in ('dir /s /b "C:\Program Files\mysql.exe" 2^>nul') do (
        if not defined MYSQL_EXE set "MYSQL_EXE=%%F"
    )
)
if not defined MYSQL_EXE (
    for /f "delims=" %%F in ('dir /s /b "C:\Program Files (x86)\mysql.exe" 2^>nul') do (
        if not defined MYSQL_EXE set "MYSQL_EXE=%%F"
    )
)

REM 6) No se encontro de ninguna forma: pedirlo manualmente
if not defined MYSQL_EXE (
    echo [ADVERTENCIA] No se encontro mysql.exe automaticamente.
    echo Abre "MySQL Workbench" -^> tu conexion -^> boton derecho -^> "Edit Connection"
    echo para confirmar donde esta instalado el servidor, o busca "mysql.exe"
    echo dentro de la carpeta de instalacion de MySQL Server ^(NO Workbench^).
    set /p MYSQL_EXE=Ruta completa a mysql.exe: 
)

if not defined MYSQL_EXE (
    echo [ERROR] No se indico una ruta a mysql.exe. No se pudo crear la base de datos.
    echo Puedes intentarlo despues corriendo este mismo setup.bat de nuevo.
    goto :fin_bd
)

set /p DB_USER=Usuario MySQL [root]: 
if "%DB_USER%"=="" set DB_USER=root
set /p DB_PASS=Contrasena MySQL: 

echo.
echo Ejecutando schema.sql, usuarios_iniciales.sql y cursos_liceo.sql...
"%MYSQL_EXE%" -u %DB_USER% -p%DB_PASS% < schema.sql
if errorlevel 1 (
    echo [ERROR] Fallo schema.sql. Revisa usuario/contrasena de MySQL e intenta de nuevo.
    goto :fin_bd
)
"%MYSQL_EXE%" -u %DB_USER% -p%DB_PASS% < usuarios_iniciales.sql
"%MYSQL_EXE%" -u %DB_USER% -p%DB_PASS% < cursos_liceo.sql
echo.
echo [OK] Base de datos creada. La base queda VACIA (solo estructura,
echo      usuarios iniciales para iniciar sesion y los cursos del liceo).

:fin_bd

REM Actualizar config si es necesario (solo si se llegaron a pedir credenciales)
if defined DB_USER (
    set /p OP_WRITE_CONFIG=¿Actualizar config.py con estas credenciales? (s/n): 
    if /i "%OP_WRITE_CONFIG%"=="s" (
        python -c "import re; f='config.py'; c=open(f).read(); c=re.sub(r'mysql\+pymysql://[^@]+@', 'mysql+pymysql://%DB_USER%:%DB_PASS%@', c); open(f,'w').write(c); print('config.py actualizado')" 2>nul || echo [ADVERTENCIA] No se pudo actualizar automaticamente.
    )
)

echo.
echo ============================================
echo   Instalacion completada.
echo   Para iniciar el sistema ejecuta: start.bat
echo.
echo   Usuarios iniciales (login por correo):
echo     UTP    : utp@liceorbl.cl      / utp123
echo     Profe  : profe@liceosofofa.cl / profe123
echo     Inspe  : inspe@liceorbl.cl    / inspe123
echo     Alumno : alumno@liceorbl.cl   / alumno123
echo ============================================
pause