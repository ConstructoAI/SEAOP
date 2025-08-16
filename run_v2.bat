@echo off
echo ========================================
echo   SOUMISSIONS QUEBEC V2 - PLATEFORME
echo ========================================
echo.

echo Recherche de Python...

REM Essayer python dans le PATH
python --version 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_python
)

REM Essayer py launcher
py --version 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :found_python
)

REM Essayer python3
python3 --version 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto :found_python
)

echo.
echo ========================================
echo ERREUR: Python n'est pas trouve
echo ========================================
echo.
echo SOLUTIONS:
echo 1. Installez Python depuis https://python.org
echo 2. Cochez "Add Python to PATH" pendant l'installation
echo 3. Redemarrez votre ordinateur
echo.
pause
exit /b 1

:found_python
echo Python trouve: %PYTHON_CMD%
%PYTHON_CMD% --version

echo.
echo Verification de la base de donnees...
if not exist "soumissions_quebec.db" (
    echo Initialisation de la base de donnees V2...
    %PYTHON_CMD% init_db_v2.py
    echo.
    echo ========================================
    echo   BASE DE DONNEES V2 INITIALISEE
    echo ========================================
    echo.
    echo COMPTES DE TEST DISPONIBLES:
    echo.
    echo ENTREPRENEURS (mot de passe: demo123):
    echo - jean@construction-excellence.ca (Premium)
    echo - marie@toitures-pro.ca (Standard)
    echo - pierre@renovations-modernes.ca (Entreprise)
    echo.
    echo ADMINISTRATEUR:
    echo - Mot de passe: admin123
    echo.
) else (
    echo Base de donnees existante trouvee.
)

echo Installation/Verification des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo ========================================
echo   DEMARRAGE SOUMISSIONS QUEBEC V2
echo ========================================
echo.
echo NOUVELLES FONCTIONNALITES:
echo - Upload de plans et documents par les clients
echo - Soumissions directes des entrepreneurs
echo - Interface client pour consulter les soumissions
echo - Messagerie integree
echo - Systeme d'evaluation
echo.
echo Interface accessible sur: http://localhost:8501
echo.
echo NAVIGATION:
echo - Accueil: Presentation du service
echo - Nouveau projet: Publier un projet (clients)
echo - Mes projets: Consulter ses projets et soumissions
echo - Espace entrepreneur: Dashboard entrepreneurs
echo - Administration: Panel admin
echo.
echo Fermez cette fenetre pour arreter l'application
echo.

%PYTHON_CMD% -m streamlit run app_v2.py

echo.
echo Application fermee.
pause