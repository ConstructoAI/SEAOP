#!/usr/bin/env python3
"""Test simple du service d'estimation"""

import sqlite3
import os
import sys

# Configuration
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def test_estimations():
    """Test simple des estimations"""
    print("Test du service d'estimation SEAOP")
    print("=" * 40)
    
    # Test 1: Vérifier la table
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estimations'")
    if cursor.fetchone():
        print("OK - Table estimations existe")
    else:
        print("ERREUR - Table estimations manquante")
        return False
    
    # Test 2: Compter les estimations
    cursor.execute("SELECT COUNT(*) FROM estimations")
    count = cursor.fetchone()[0]
    print(f"OK - {count} estimation(s) en base")
    
    # Test 3: Vérifier les statuts
    cursor.execute("SELECT statut, COUNT(*) FROM estimations GROUP BY statut")
    statuts = cursor.fetchall()
    print("Statuts disponibles:")
    for statut, nb in statuts:
        print(f"  - {statut}: {nb}")
    
    # Test 4: Test import fonctions
    try:
        sys.path.append('.')
        from app_v2 import creer_demande_estimation, get_estimations_admin
        print("OK - Fonctions importees")
        
        # Test 5: Test récupération admin
        estimations = get_estimations_admin()
        print(f"OK - {len(estimations)} estimations recuperees par admin")
        
    except Exception as e:
        print(f"ERREUR - Import: {e}")
        return False
    
    conn.close()
    print("=" * 40)
    print("TESTS TERMINES - Service d'estimation fonctionnel")
    return True

if __name__ == "__main__":
    success = test_estimations()
    if success:
        print("\nSUCCES - Le service d'estimation fonctionne correctement!")
    else:
        print("\nERREUR - Problemes detectes")
    exit(0 if success else 1)