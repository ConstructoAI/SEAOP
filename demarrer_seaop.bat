@echo off
title SEAOP - Demarrage
color 0A

echo.
echo ================================================
echo            SEAOP v2.0 - DEMARRAGE
echo   Systeme Electronique d'Appel d'Offres Public
echo ================================================
echo.

REM Aller dans le bon repertoire
cd /d "%~dp0"

REM Verifier la presence de Python
echo [1/4] Verification de Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python non trouve
    echo.
    echo Veuillez installer Python depuis https://python.org
    echo Cochez "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)
echo OK - Python detecte

REM Verifier/installer les dependances
echo [2/4] Verification des dependances...
py -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERREUR: Installation des dependances echouee
    pause
    exit /b 1
)
echo OK - Dependances installees

REM Initialiser la base de donnees si necessaire
echo [3/4] Verification de la base de donnees...
if not exist "seaop.db" (
    echo Initialisation de la base SEAOP...
    py init_db_v2.py
    if %errorlevel% neq 0 (
        echo ERREUR: Initialisation base de donnees echouee
        pause
        exit /b 1
    )
    echo OK - Base de donnees initialisee
) else (
    echo OK - Base de donnees existante trouvee
)

REM Demarrer SEAOP
echo [4/4] Demarrage de SEAOP...
echo.
echo ================================================
echo          SEAOP DEMARRE AVEC SUCCES
echo ================================================
echo.
echo Interface Web: http://localhost:8501
echo.
echo COMPTES DE DEMONSTRATION:
echo.
echo Fournisseurs (mot de passe: demo123):
echo - jean@construction-excellence.ca
echo - marie@toitures-pro.ca  
echo - pierre@renovations-modernes.ca
echo.
echo Administrateur: admin123
echo.
echo Appuyez sur Ctrl+C pour arreter SEAOP
echo Fermez cette fenetre pour arreter le serveur
echo.

REM Lancer Streamlit
py -m streamlit run app_v2.py --server.port=8501 --server.headless=true

REM Si on arrive ici, Streamlit s'est arrete
echo.
echo SEAOP arrete.
pause