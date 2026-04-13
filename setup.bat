@echo off
REM Tenaz-gym Setup Script for Windows
REM Este script configura e instala el backend y frontend

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   TENAZ-GYM SETUP SCRIPT (Windows)
echo ========================================
echo.

REM Colors (simulated)
echo [PASO 1] Configurando Backend...
echo.

cd /d "%~dp0"

if not exist "backend" (
    echo ERROR: Carpeta 'backend' no encontrada
    pause
    exit /b 1
)

cd backend

REM Crear entorno virtual
echo Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: No se pudo crear el entorno virtual. Verifica que Python este instalado.
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)

REM Copiar archivo .env
if not exist ".env" (
    if exist ".env.example" (
        echo Creando archivo .env desde .env.example...
        copy .env.example .env
        echo.
        echo [IMPORTANTE] Edita el archivo 'backend\.env' con tus valores si es necesario
    )
)
echo.
echo [PASO 2] Backend configurado exitosamente!
echo.
echo ========================================
echo   INSTRUCCIONES FINALES
echo ========================================
echo.
echo Para ejecutar el Backend:
echo   1. Abre una terminal en 'backend' y ejecuta:
echo      python app.py
echo.
echo Para ejecutar el Frontend:
echo   1. Abre otra terminal en 'frontend' y ejecuta:
echo      python -m http.server 8080
echo   2. Abre el navegador en:
echo      http://localhost:8080/login.html
echo.
echo Credenciales por defecto:
echo   Usuario: admin
echo   Contrasa: gym123
echo.
echo IMPORTANTE: Cambia la contrasa antes de hacer deploy!
echo.
pause
