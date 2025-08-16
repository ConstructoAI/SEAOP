@echo off
echo ========================================
echo   SOUMISSIONS QUEBEC - PLATEFORME
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
echo Verification de la base de donnees...
if not exist "soumissions_quebec.db" (
    echo Initialisation de la base de donnees avec donnees de demo...
    %PYTHON_CMD% init_db.py
    echo.
    echo ========================================
    echo   BASE DE DONNEES INITIALISEE
    echo ========================================
    echo.
    echo COMPTES DE TEST DISPONIBLES:
    echo.
    echo ENTREPRENEURS ^(mot de passe: demo123^):
    echo - jean@constructiontremblay.ca ^(Premium^)
    echo - marie@electrique-qc.ca ^(Standard^)
    echo - pierre@plomberie-excellence.ca ^(Standard^)
    echo - sylvie@toitures-qc-pro.ca ^(Premium^)
    echo - robert@cuisine-design-plus.ca ^(Entreprise^)
    echo - Et 5 autres comptes...
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
echo   DEMARRAGE DE SOUMISSIONS QUEBEC
echo ========================================
echo.
echo Interface accessible sur: http://localhost:8501
echo.
echo NAVIGATION:
echo - Accueil: Presentation du service
echo - Demande de soumission: Formulaire client
echo - Espace entrepreneur: Dashboard entrepreneurs
echo - Administration: Panel admin
echo.
echo Fermez cette fenetre pour arreter l'application
echo.

%PYTHON_CMD% -m streamlit run app.py

echo.
echo Application fermee.
pause