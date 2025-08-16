#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration de base de données SEAOP
Ajoute les nouvelles colonnes sans perdre les données existantes
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def migrate_database():
    """Migration de la base de données vers la version avec urgence"""
    print("Debut de la migration de la base de donnees SEAOP...")
    
    # Créer un backup avant migration
    if os.path.exists(DATABASE_PATH):
        backup_name = os.path.join(DATA_DIR, f'seaop_backup_migration_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        import shutil
        shutil.copy2(DATABASE_PATH, backup_name)
        print(f"Backup cree : {backup_name}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(leads)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Colonnes existantes dans 'leads': {columns}")
        
        # Ajouter les colonnes manquantes une par une
        columns_to_add = [
            ('date_limite_soumissions', 'DATE'),
            ('date_debut_souhaite', 'DATE'),
            ('niveau_urgence', 'TEXT DEFAULT "normal"')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE leads ADD COLUMN {column_name} {column_type}')
                    print(f"[OK] Colonne '{column_name}' ajoutee avec succes")
                except sqlite3.OperationalError as e:
                    print(f"[ERREUR] Erreur lors de l'ajout de '{column_name}': {e}")
            else:
                print(f"[OK] Colonne '{column_name}' existe deja")
        
        # Créer la table notifications si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_type TEXT NOT NULL,
                utilisateur_id INTEGER NOT NULL,
                type_notification TEXT NOT NULL,
                titre TEXT NOT NULL,
                message TEXT NOT NULL,
                lien_id INTEGER,
                lu BOOLEAN DEFAULT 0,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[OK] Table 'notifications' verifiee/creee")
        
        # Mettre à jour les projets existants avec des valeurs par défaut
        cursor.execute('''
            UPDATE leads 
            SET 
                date_limite_soumissions = date(date_creation, '+14 days'),
                date_debut_souhaite = date(date_creation, '+30 days'),
                niveau_urgence = 'normal'
            WHERE date_limite_soumissions IS NULL
        ''')
        
        rows_updated = cursor.rowcount
        print(f"[OK] {rows_updated} projet(s) mis a jour avec des delais par defaut")
        
        # Vérifier la structure finale
        cursor.execute("PRAGMA table_info(leads)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"Colonnes finales dans 'leads': {final_columns}")
        
        conn.commit()
        print("[OK] Migration terminee avec succes !")
        
    except Exception as e:
        print(f"[ERREUR] Erreur durant la migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_migration():
    """Vérifie que la migration s'est bien passée"""
    print("\nVerification de la migration...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Test de la requête qui causait l'erreur
        cursor.execute('''
            SELECT l.*, 
                   (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions
            FROM leads l
            WHERE l.visible_entrepreneurs = 1 AND l.accepte_soumissions = 1
            ORDER BY 
                CASE l.niveau_urgence 
                    WHEN 'critique' THEN 1 
                    WHEN 'eleve' THEN 2 
                    WHEN 'normal' THEN 3 
                    WHEN 'faible' THEN 4 
                END,
                l.date_limite_soumissions ASC,
                l.date_creation DESC
            LIMIT 5
        ''')
        
        projets = cursor.fetchall()
        print(f"[OK] Requete test reussie : {len(projets)} projet(s) trouve(s)")
        
        # Afficher quelques infos sur les projets
        for i, projet in enumerate(projets[:3]):
            print(f"   Projet {i+1}: {projet[5]} - Urgence: {projet[19] if len(projet) > 19 else 'N/A'}")
            
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la verification: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    try:
        migrate_database()
        if verify_migration():
            print("\n[SUCCES] Migration SEAOP terminee avec succes !")
            print("Vous pouvez maintenant relancer l'application:")
            print("   py -m streamlit run app_v2.py")
        else:
            print("\n[ERREUR] La verification a echoue. Verifiez les logs.")
    except Exception as e:
        print(f"\n[ERREUR FATALE] Erreur fatale: {e}")
        print("Essayez de reinitialiser completement avec: py init_db_v2.py")