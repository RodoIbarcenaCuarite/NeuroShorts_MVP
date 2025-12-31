@echo off
set "PYTHON_PATH=python"
set "SCRIPT_PATH=%~dp0src\render_engine.py"

if "%~1"=="" (
    echo Uso: run_neuroshorts.bat [ruta_al_json]
    echo Ejemplo: run_neuroshorts.bat test_input.json
    pause
    exit /b
)

echo Ejecutando NeuroShorts Render Engine...
%PYTHON_PATH% "%SCRIPT_PATH%" "%~1"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Hubo un error al renderizar.
    pause
) else (
    echo ✅ Renderizado completado exitosamente.
)
