@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Primero instala las dependencias siguiendo la guia PASO_A_PASO.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py
pause
