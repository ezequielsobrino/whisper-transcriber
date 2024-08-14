@echo off
setlocal enabledelayedexpansion

REM Configuración de la ruta del entorno virtual
set "VENV_PATH=.venv"
if not "%~1"=="" set "VENV_PATH=%~1"

echo Directorio actual: %cd%
echo Ruta del entorno virtual: %VENV_PATH%

REM Verificar si el entorno virtual existe, si no, crearlo
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo El entorno virtual no existe. Creando uno nuevo...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual.
        echo Asegúrate de tener Python instalado y accesible desde la línea de comandos.
        pause
        exit /b 1
    )
    echo Entorno virtual creado exitosamente.
)

REM Activar el entorno virtual
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo Entorno virtual activado correctamente.

REM Instalar dependencias si es necesario
if not exist "%VENV_PATH%\Scripts\pip.exe" (
    echo Instalando pip en el entorno virtual...
    python -m ensurepip --upgrade
)

echo Instalando/Actualizando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: No se pudieron instalar las dependencias.
    echo Asegúrate de tener un archivo requirements.txt en el directorio del proyecto.
    pause
    exit /b 1
)

REM Verificar si run.py existe
if not exist "run.py" (
    echo Error: No se encontró el archivo run.py en el directorio actual.
    echo Directorio actual: %cd%
    pause
    exit /b 1
)

REM Intenta abrir con Chrome
set "chrome_path="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "chrome_path=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "chrome_path=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

if defined chrome_path (
    start "" "!chrome_path!" "http://127.0.0.1:5000/v2"
) else (
    REM Si Chrome no está instalado, usa el navegador por defecto
    start http://127.0.0.1:5000/v2
)

echo Ejecutando run.py...
REM Ejecutar run.py
python run.py
if errorlevel 1 (
    echo Error: Hubo un problema al ejecutar run.py.
    pause
    exit /b 1
)

endlocal