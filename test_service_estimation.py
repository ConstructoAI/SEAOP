#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du service d'estimation SEAOP
Valide les principales fonctionnalités
"""

import sqlite3
import os
import sys

# Ajouter le répertoire courant au path pour importer les fonctions
sys.path.append('.')

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def test_database_structure():
    """Test de la structure de la base de données"""
    print("=== TEST STRUCTURE BASE DE DONNÉES ===")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Vérifier que la table estimations existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estimations'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("Table 'estimations' existe")
    else:
        print("Table 'estimations' n'existe pas")
        return False
    
    # Vérifier les colonnes importantes
    cursor.execute("PRAGMA table_info(estimations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = [
        'id', 'nom_client', 'email_client', 'type_projet', 
        'description_detaillee', 'statut', 'numero_reference',
        'plans_client', 'estimation_document', 'facture_document'
    ]
    
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        print(f"Colonnes manquantes: {missing_columns}")
        return False
    else:
        print("Toutes les colonnes requises presentes")
    
    conn.close()
    return True

def test_sample_data():
    """Test des données de démonstration"""
    print("\n=== TEST DONNÉES DE DÉMONSTRATION ===")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Compter les estimations
    cursor.execute("SELECT COUNT(*) FROM estimations")
    count = cursor.fetchone()[0]
    print(f"Nombre d'estimations: {count}")
    
    if count == 0:
        print("Aucune estimation de demonstration")
        return False
    
    # Vérifier les statuts
    cursor.execute("SELECT statut, COUNT(*) FROM estimations GROUP BY statut")
    statuts = cursor.fetchall()
    print("Repartition par statut:")
    for statut, nb in statuts:
        print(f"   - {statut}: {nb}")
    
    # Vérifier les données complètes
    cursor.execute("SELECT nom_client, email_client, type_projet, numero_reference FROM estimations")
    estimations = cursor.fetchall()
    
    print("Estimations de demonstration:")
    for est in estimations:
        print(f"   - {est[0]} ({est[1]}): {est[2]} - {est[3]}")
    
    conn.close()
    return True

def test_functions_import():
    """Test de l'import des fonctions d'estimation"""
    print("\n=== TEST IMPORT FONCTIONS ===")
    
    try:
        from app_v2 import (
            creer_demande_estimation,
            get_estimations_admin,
            get_estimations_client,
            mettre_a_jour_statut_estimation,
            ajouter_documents_estimation
        )
        print("Toutes les fonctions d'estimation importees avec succes")
        return True
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        return False

def test_create_estimation():
    """Test de création d'une nouvelle estimation"""
    print("\n=== TEST CRÉATION ESTIMATION ===")
    
    try:
        from app_v2 import creer_demande_estimation
        
        # Données de test
        estimation_test = {
            'nom_client': 'Test Client',
            'email_client': 'test@exemple.com',
            'telephone_client': '514-555-0000',
            'adresse_client': '123 Rue Test, Montréal, QC',
            'type_projet': 'Test Rénovation',
            'description_detaillee': 'Ceci est un test de création d\'estimation',
            'surface_approximative': '100 pi²',
            'budget_approximatif': 'Test budget',
            'delai_souhaite': 'Test délai',
            'plans_client': '',
            'photos_client': '',
            'documents_client': '',
            'prix_estimation': 250.0
        }
        
        # Créer l'estimation
        success = creer_demande_estimation(estimation_test)
        
        if success:
            print("✅ Estimation de test créée avec succès")
            
            # Vérifier qu'elle a été créée
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM estimations WHERE email_client = ?", 
                         (estimation_test['email_client'],))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                print("✅ Estimation trouvée en base de données")
                return True
            else:
                print("❌ Estimation non trouvée en base")
                return False
        else:
            print("❌ Échec de création de l'estimation")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de création: {e}")
        return False

def test_admin_functions():
    """Test des fonctions administrateur"""
    print("\n=== TEST FONCTIONS ADMIN ===")
    
    try:
        from app_v2 import get_estimations_admin, mettre_a_jour_statut_estimation
        
        # Test récupération estimations admin
        estimations = get_estimations_admin()
        print(f"✅ Récupération estimations admin: {len(estimations)} trouvées")
        
        if estimations:
            # Test mise à jour statut
            first_estimation = estimations[0]
            success = mettre_a_jour_statut_estimation(
                first_estimation['id'], 
                'en_cours',
                'Test de mise à jour statut'
            )
            
            if success:
                print("✅ Mise à jour statut réussie")
                return True
            else:
                print("❌ Échec mise à jour statut")
                return False
        else:
            print("⚠️ Aucune estimation pour tester les fonctions admin")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test des fonctions admin: {e}")
        return False

def test_client_functions():
    """Test des fonctions client"""
    print("\n=== TEST FONCTIONS CLIENT ===")
    
    try:
        from app_v2 import get_estimations_client
        
        # Test avec email de démonstration
        estimations = get_estimations_client('marie.dubois@exemple.com')
        print(f"✅ Récupération estimations client: {len(estimations)} trouvées")
        
        # Test avec email inexistant
        estimations_vide = get_estimations_client('inexistant@test.com')
        print(f"✅ Test email inexistant: {len(estimations_vide)} estimations (normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des fonctions client: {e}")
        return False

def test_cleanup():
    """Nettoie les données de test"""
    print("\n=== NETTOYAGE ===")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Supprimer l'estimation de test
        cursor.execute("DELETE FROM estimations WHERE email_client = ?", ('test@exemple.com',))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted > 0:
            print(f"✅ {deleted} estimation(s) de test supprimée(s)")
        else:
            print("ℹ️ Aucune estimation de test à supprimer")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

def main():
    """Exécute tous les tests"""
    print("TESTS DU SERVICE D'ESTIMATION SEAOP")
    print("=" * 50)
    
    tests = [
        ("Structure base de données", test_database_structure),
        ("Données de démonstration", test_sample_data),
        ("Import des fonctions", test_functions_import),
        ("Création estimation", test_create_estimation),
        ("Fonctions admin", test_admin_functions),
        ("Fonctions client", test_client_functions),
        ("Nettoyage", test_cleanup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 50)
    print("RESUME DES TESTS")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nRESULTATS FINAUX:")
    print(f"   Tests reussis: {passed}")
    print(f"   Tests echoues: {failed}")
    print(f"   Taux de reussite: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\nTOUS LES TESTS SONT PASSES !")
        print("Le service d'estimation est pret a etre utilise.")
    else:
        print(f"\n{failed} test(s) ont echoue.")
        print("Verifiez les erreurs ci-dessus avant de proceder.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)