#!/usr/bin/env python3
"""
Script de test pour SEAOP
Vérifie que tous les composants fonctionnent correctement
"""

import sqlite3
import os
import sys

def test_database():
    """Test de la base de données SEAOP"""
    print("Test de la base de donnees...")
    
    if not os.path.exists('seaop.db'):
        print("ERREUR Base de données seaop.db non trouvée")
        return False
    
    try:
        conn = sqlite3.connect('seaop.db')
        cursor = conn.cursor()
        
        # Test des tables principales
        tables_required = ['leads', 'entrepreneurs', 'soumissions', 'messages', 'evaluations']
        
        for table in tables_required:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  Table {table}: {count} enregistrements")
        
        # Test des données de démonstration
        cursor.execute("SELECT COUNT(*) FROM leads WHERE numero_reference LIKE 'SEAOP-%'")
        leads_seaop = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entrepreneurs WHERE email LIKE '%@%'")
        entrepreneurs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM soumissions")
        soumissions_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  Statistiques:")
        print(f"     - Appels d'offres SEAOP: {leads_seaop}")
        print(f"     - Entrepreneurs inscrits: {entrepreneurs_count}")
        print(f"     - Soumissions totales: {soumissions_count}")
        
        if leads_seaop > 0 and entrepreneurs_count > 0:
            print("Base de donnees SEAOP fonctionnelle")
            return True
        else:
            print("Donnees de demonstration manquantes")
            return False
            
    except Exception as e:
        print(f"Erreur base de donnees: {e}")
        return False

def test_files():
    """Test de la présence des fichiers requis"""
    print("\n Test des fichiers...")
    
    files_required = [
        ('app_v2.py', 'Application principale SEAOP'),
        ('init_db_v2.py', 'Script d\'initialisation'),
        ('style.css', 'Feuille de style'),
        ('requirements.txt', 'Dépendances Python'),
        ('run_seaop.bat', 'Script de lancement'),
        ('README_SEAOP.md', 'Documentation'),
        ('config_seaop.py', 'Configuration')
    ]
    
    all_files_ok = True
    
    for filename, description in files_required:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  OK {filename} ({size} bytes) - {description}")
        else:
            print(f"  ERREUR {filename} manquant - {description}")
            all_files_ok = False
    
    return all_files_ok

def test_config():
    """Test du fichier de configuration"""
    print("\n Test de la configuration...")
    
    try:
        import config_seaop
        
        print(f"  OK Version: {config_seaop.VERSION}")
        print(f"  OK Nom: {config_seaop.NOM_SYSTEME}")
        print(f"  OK Base de données: {config_seaop.DATABASE_FILE}")
        print(f"  OK Types de projets: {len(config_seaop.TYPES_PROJETS)} configurés")
        print(f"  OK Tranches budgétaires: {len(config_seaop.TRANCHES_BUDGET)} configurées")
        
        return True
        
    except ImportError as e:
        print(f"  ERREUR Erreur import config: {e}")
        return False
    except Exception as e:
        print(f"  ERREUR Erreur configuration: {e}")
        return False

def test_streamlit_import():
    """Test des imports Streamlit"""
    print("\n Test des dépendances...")
    
    try:
        import streamlit
        print(f"  OK Streamlit {streamlit.__version__} disponible")
        
        import pandas
        print(f"  OK Pandas {pandas.__version__} disponible")
        
        import sqlite3
        print(f"  OK SQLite3 disponible")
        
        from PIL import Image
        print(f"  OK Pillow (PIL) disponible")
        
        return True
        
    except ImportError as e:
        print(f"  ERREUR Dépendance manquante: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("SEAOP - Test de fonctionnement\n")
    print("=" * 50)
    
    # Exécution des tests
    tests = [
        ("Fichiers", test_files),
        ("Configuration", test_config),
        ("Dépendances", test_streamlit_import),
        ("Base de données", test_database)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERREUR Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print(" RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "OK PASS" if success else "ERREUR FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print(" SEAOP est prêt à fonctionner !")
        print("\n Pour démarrer SEAOP:")
        print("   - Exécutez: python -m streamlit run app_v2.py")
        print("   - Ou double-cliquez sur: run_seaop.bat")
        print("   - Interface: http://localhost:8501")
    else:
        print("ATTENTION Certains problèmes doivent être corrigés")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())