@echo off
echo ========================================
echo            SEAOP v2.0
echo   Systeme Electronique d'Appel d'Offres Public
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
echo Verification de la base de donnees SEAOP...
if not exist "seaop.db" (
    echo Initialisation de la base de donnees SEAOP...
    %PYTHON_CMD% init_db_v2.py
    echo.
    echo ========================================
    echo      BASE SEAOP INITIALISEE
    echo ========================================
    echo.
    echo COMPTES DE TEST DISPONIBLES:
    echo.
    echo FOURNISSEURS/ENTREPRENEURS (mot de passe: demo123):
    echo - jean@construction-excellence.ca (Premium)
    echo - marie@toitures-pro.ca (Standard)
    echo - pierre@renovations-modernes.ca (Entreprise)
    echo.
    echo ADMINISTRATEUR:
    echo - Mot de passe: admin123
    echo.
) else (
    echo Base de donnees SEAOP existante trouvee.
)

echo Installation/Verification des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo ========================================
echo         DEMARRAGE SEAOP
echo ========================================
echo.
echo FONCTIONNALITES SEAOP:
echo - Publication d'appels d'offres avec plans et documents
echo - Soumissions electroniques des fournisseurs
echo - Interface de comparaison et selection des offres
echo - Messagerie integree organisme-fournisseur
echo - Systeme d'evaluation et qualification
echo - Conformite aux standards d'appels d'offres publics
echo.
echo Interface accessible sur: http://localhost:8501
echo.
echo NAVIGATION:
echo - Accueil: Presentation du systeme SEAOP
echo - Nouveau projet: Publier un appel d'offres
echo - Mes projets: Consulter appels d'offres et soumissions
echo - Espace entrepreneur: Acces fournisseurs/entrepreneurs
echo - Administration: Panel administrateur
echo.
echo Fermez cette fenetre pour arreter SEAOP
echo.

%PYTHON_CMD% -m streamlit run app_v2.py

echo.
echo SEAOP ferme.
pause