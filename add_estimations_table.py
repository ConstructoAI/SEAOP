#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter la table estimations au système SEAOP
Service d'estimation payant avec upload de documents
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def add_estimations_table():
    """Ajoute la table estimations pour le service d'estimation payant"""
    
    print("Ajout de la table estimations pour le service d'estimation...")
    
    # Créer un backup avant modification
    if os.path.exists(DATABASE_PATH):
        backup_name = os.path.join(DATA_DIR, f'seaop_backup_estimations_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        import shutil
        shutil.copy2(DATABASE_PATH, backup_name)
        print(f"Backup créé : {backup_name}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Créer la table estimations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estimations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Informations client
                nom_client TEXT NOT NULL,
                email_client TEXT NOT NULL,
                telephone_client TEXT NOT NULL,
                adresse_client TEXT,
                
                -- Détails de la demande
                type_projet TEXT NOT NULL,
                description_detaillee TEXT NOT NULL,
                surface_approximative TEXT,
                budget_approximatif TEXT,
                delai_souhaite TEXT,
                
                -- Documents client (plans, croquis, photos)
                plans_client TEXT,  -- Base64 des documents uploadés par le client
                photos_client TEXT,  -- Photos de l'existant
                documents_client TEXT,  -- Autres documents
                
                -- Informations estimation
                prix_estimation REAL,  -- Prix du service d'estimation
                statut TEXT DEFAULT 'recue',  -- 'recue', 'en_cours', 'terminee', 'envoyee', 'payee'
                
                -- Documents de réponse (estimation + facture)
                estimation_document TEXT,  -- PDF/HTML de l'estimation fournie
                facture_document TEXT,     -- Facture pour le service
                documents_annexes TEXT,    -- Autres documents fournis
                
                -- Métadonnées
                date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_debut_analyse TIMESTAMP,
                date_estimation_terminee TIMESTAMP,
                date_envoi_client TIMESTAMP,
                date_paiement TIMESTAMP,
                
                -- Suivi
                numero_reference TEXT UNIQUE,  -- Référence unique SEAOP-EST-XXXXX
                notes_internes TEXT,  -- Notes pour l'estimateur
                commentaires_client TEXT,  -- Retours du client
                
                -- Facturation
                methode_paiement TEXT,  -- 'virement', 'cheque', 'carte', etc.
                reference_paiement TEXT,  -- Numéro de transaction
                
                UNIQUE(email_client, date_demande)  -- Éviter les doublons
            )
        ''')
        
        # Créer les index pour optimiser les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estimations_statut ON estimations(statut)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estimations_client ON estimations(email_client)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estimations_date ON estimations(date_demande)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estimations_reference ON estimations(numero_reference)')
        
        # Ajouter des données de démonstration pour tester
        estimations_demo = [
            {
                'nom_client': 'Marie Dubois',
                'email_client': 'marie.dubois@exemple.com',
                'telephone_client': '514-555-1234',
                'adresse_client': '123 Rue Saint-Denis, Montréal, QC H2X 1K1',
                'type_projet': 'Rénovation cuisine',
                'description_detaillee': '''Estimation demandée pour rénovation complète de cuisine.
                
Détails de la demande:
- Cuisine actuelle: 12x10 pieds
- Démolition partielle (garder la plomberie existante)
- Nouvelles armoires en bois
- Comptoir en granite ou quartz
- Plancher en céramique
- Électroménagers à remplacer (lave-vaisselle, cuisinière, réfrigérateur)
- Peinture complète
                
Contraintes:
- Budget approximatif: 25 000$ - 35 000$
- Délai souhaité: 2-3 mois
- Disponibilité: weekends pour visites
                
J'aimerais une estimation détaillée avec breakdown des coûts par poste.''',
                'surface_approximative': '120 pi²',
                'budget_approximatif': '25 000$ - 35 000$',
                'delai_souhaite': '2-3 mois',
                'prix_estimation': 150.00,
                'statut': 'recue',
                'numero_reference': 'SEAOP-EST-20240316-001'
            },
            {
                'nom_client': 'Pierre Gagnon',
                'email_client': 'p.gagnon@exemple.com',
                'telephone_client': '450-555-5678',
                'adresse_client': '456 Boulevard Taschereau, Longueuil, QC J4K 2V8',
                'type_projet': 'Agrandissement maison',
                'description_detaillee': '''Demande d'estimation pour agrandissement de maison unifamiliale.
                
Projet envisagé:
- Agrandissement arrière: 16x20 pieds
- 2 étages (rez-de-chaussée + étage)
- Rez-de-chaussée: salon familial + salle d'eau
- Étage: 2 chambres + salle de bain complète
- Raccordement au système existant (plomberie, électricité, chauffage)
- Finition complète intérieure/extérieure
                
Spécifications souhaitées:
- Fondation en béton
- Structure bois
- Revêtement extérieur assorti à l'existant
- Fenêtres double vitrage
- Isolation haute performance
                
Budget approximatif: 80 000$ - 120 000$
Délai flexible: 4-6 mois''',
                'surface_approximative': '640 pi² (320 pi² x 2 étages)',
                'budget_approximatif': '80 000$ - 120 000$',
                'delai_souhaite': '4-6 mois',
                'prix_estimation': 300.00,
                'statut': 'en_cours',
                'numero_reference': 'SEAOP-EST-20240315-002',
                'date_debut_analyse': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'notes_internes': 'Projet complexe - nécessite vérification zonage municipal'
            }
        ]
        
        # Insérer les données de démonstration
        for estimation in estimations_demo:
            cursor.execute('''
                INSERT INTO estimations (
                    nom_client, email_client, telephone_client, adresse_client,
                    type_projet, description_detaillee, surface_approximative,
                    budget_approximatif, delai_souhaite, prix_estimation,
                    statut, numero_reference, date_debut_analyse, notes_internes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estimation['nom_client'], estimation['email_client'], 
                estimation['telephone_client'], estimation.get('adresse_client'),
                estimation['type_projet'], estimation['description_detaillee'],
                estimation['surface_approximative'], estimation['budget_approximatif'],
                estimation['delai_souhaite'], estimation['prix_estimation'],
                estimation['statut'], estimation['numero_reference'],
                estimation.get('date_debut_analyse'), estimation.get('notes_internes')
            ))
        
        # Ajouter des notifications pour les nouvelles estimations
        cursor.execute('''
            INSERT INTO notifications (
                utilisateur_type, utilisateur_id, type_notification,
                titre, message, lien_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'admin', 0, 'nouvelle_estimation',
            'Nouvelle demande d\'estimation',
            'Marie Dubois a demandé une estimation pour une rénovation de cuisine',
            1
        ))
        
        cursor.execute('''
            INSERT INTO notifications (
                utilisateur_type, utilisateur_id, type_notification,
                titre, message, lien_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'admin', 0, 'nouvelle_estimation',
            'Nouvelle demande d\'estimation',
            'Pierre Gagnon a demandé une estimation pour un agrandissement',
            2
        ))
        
        conn.commit()
        print("Table estimations creee avec succes!")
        print("Index de performance ajoutes!")
        print("2 demandes d'estimation de demonstration ajoutees!")
        print("Notifications de test creees!")
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de la table estimations: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def verify_estimations_table():
    """Verifie que la table estimations a ete creee correctement"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Verifier la structure de la table
        cursor.execute("PRAGMA table_info(estimations)")
        columns = cursor.fetchall()
        print(f"\nStructure de la table estimations:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Compter les enregistrements
        cursor.execute("SELECT COUNT(*) FROM estimations")
        count = cursor.fetchone()[0]
        print(f"\nNombre d'estimations en base: {count}")
        
        # Afficher les statuts
        cursor.execute("SELECT statut, COUNT(*) FROM estimations GROUP BY statut")
        statuts = cursor.fetchall()
        print(f"\nRepartition par statut:")
        for statut, nb in statuts:
            print(f"   - {statut}: {nb}")
            
    except Exception as e:
        print(f"Erreur lors de la verification: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("SEAOP - Ajout du service d'estimation")
    print("=" * 50)
    
    add_estimations_table()
    verify_estimations_table()
    
    print("\n" + "=" * 50)
    print("Service d'estimation ajoute avec succes!")
    print("\nProchaines etapes:")
    print("1. Modifier app_v2.py pour ajouter l'interface")
    print("2. Ajouter le menu 'Service d'estimation'")
    print("3. Creer l'interface admin pour gerer les estimations")
    print("4. Tester le systeme complet")