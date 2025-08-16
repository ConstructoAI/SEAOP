@echo off
echo ========================================
echo              SEAOP v2.0
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
echo OU desactivez les alias Microsoft Store:
echo Parametres Windows ^> Applications ^> Aliases d'execution
echo Desactivez python.exe et python3.exe
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
    echo FOURNISSEURS ^(mot de passe: demo123^):
    echo - jean@construction-excellence.ca ^(Premium^)
    echo - marie@toitures-pro.ca ^(Standard^)
    echo - pierre@renovations-modernes.ca ^(Entreprise^)
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
echo Interface accessible sur: http://localhost:8501
echo.
echo NAVIGATION SEAOP:
echo - Accueil: Presentation du systeme
echo - Publier un appel d'offres: Creation d'appels d'offres
echo - Mes appels d'offres: Consulter soumissions recues
echo - Espace Entrepreneurs: Dashboard entrepreneurs certifies
echo - Service d'estimation: Demandes d'estimation professionnelles
echo - Administration: Panel administrateur
echo.
echo Fermez cette fenetre pour arreter SEAOP
echo.
echo Ouverture du navigateur dans 3 secondes...
timeout /t 3 /nobreak >nul
start http://localhost:8501

%PYTHON_CMD% -m streamlit run app_v2.py

echo.
echo SEAOP ferme.
pause