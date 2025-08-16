@echo off
echo SEAOP - Demarrage simple
echo.

REM Aller dans le bon repertoire
cd /d "%~dp0"

REM Verifier Python
echo Test Python...
py --version
if %errorlevel% neq 0 (
    echo Erreur: Python non trouve
    pause
    exit /b 1
)

REM Verifier fichiers
echo Test fichiers...
if not exist "app_v2.py" (
    echo Erreur: app_v2.py non trouve
    pause
    exit /b 1
)

REM Installer dependances
echo Installation dependances...
py -m pip install streamlit pandas pillow

REM Initialiser base si necessaire
if not exist "seaop.db" (
    echo Initialisation base...
    py init_db_v2.py
)

REM Demarrer
echo Demarrage SEAOP...
echo Interface: http://localhost:8501
py -m streamlit run app_v2.py

pause