@echo off
title Sistema Web Colonia Residencial
color 0B

cd /d "%~dp0"

echo ======================================================================
echo       SISTEMA WEB DE GESTION DE COLONIA RESIDENCIAL
echo ======================================================================
echo.

if not exist ".env" (
    echo [INFO] Creando archivo .env a partir de .env.example...
    copy ".env.example" ".env" >nul
)

if exist "venv\Scripts\python.exe" goto iniciar_servidor

echo [INFO] Configurando entorno virtual por primera vez...
python -m venv venv
call venv\Scripts\pip.exe install -r requirements.txt

:iniciar_servidor
echo [INFO] Verificando tablas y datos semilla en Neon PostgreSQL...
venv\Scripts\python.exe init_db.py

echo.
echo ======================================================================
echo  Servidor corriendo en: http://127.0.0.1:5000
echo  Usuario: admin  ^|  Password: admin123
echo  Para detener el servidor presiona Ctrl + C
echo ======================================================================
echo.

venv\Scripts\python.exe run.py

echo.
echo Servidor detenido.
pause
