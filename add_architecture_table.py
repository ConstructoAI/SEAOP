#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter la table demandes_architecture à SEAOP
Module de service d'architecture pour projets > 6000 pi²
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '.')  # Utiliser le répertoire courant par défaut
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def add_architecture_table():
    """Ajoute la table pour les demandes de plans d'architecture"""
    
    print("Ajout du module Service d'Architecture a SEAOP...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
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
        
        # Créer la table demandes_architecture
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demandes_architecture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Informations client
                nom_client TEXT NOT NULL,
                email_client TEXT NOT NULL,
                telephone_client TEXT NOT NULL,
                adresse_projet TEXT NOT NULL,
                ville TEXT NOT NULL,
                code_postal TEXT NOT NULL,
                
                -- Détails du projet architectural
                type_batiment TEXT NOT NULL,  -- 'résidentiel', 'commercial', 'industriel', 'institutionnel', 'mixte'
                usage_batiment TEXT NOT NULL,  -- Description de l'usage prévu
                superficie_terrain REAL,  -- En pieds carrés
                superficie_batiment REAL NOT NULL,  -- En pieds carrés (doit être > 6000)
                nombre_etages INTEGER DEFAULT 1,
                nombre_logements INTEGER,  -- Pour projets multi-logements
                
                -- Spécifications techniques
                type_construction TEXT,  -- 'nouvelle', 'agrandissement', 'renovation_majeure'
                style_architectural TEXT,  -- 'moderne', 'traditionnel', 'contemporain', etc.
                contraintes_terrain TEXT,  -- Pente, servitudes, etc.
                exigences_speciales TEXT,  -- Accessibilité, LEED, etc.
                
                -- Services requis
                plans_requis TEXT NOT NULL,  -- 'complet', 'preliminaire', 'concept', 'execution'
                services_inclus TEXT,  -- 'structure', 'mecanique', 'electrique', 'civil'
                besoin_3d BOOLEAN DEFAULT 0,  -- Modélisation 3D requise
                besoin_permis BOOLEAN DEFAULT 1,  -- Aide pour permis de construction
                
                -- Documents du client
                certificat_localisation TEXT,  -- Document base64
                photos_terrain TEXT,  -- Photos actuelles base64
                croquis_client TEXT,  -- Esquisses du client base64
                documents_urbanisme TEXT,  -- Règlements municipaux base64
                
                -- Budget et délais
                budget_construction TEXT,  -- Budget total de construction estimé
                budget_architecture TEXT,  -- Budget pour services d'architecture
                date_debut_souhaite DATE,
                date_livraison_plans DATE,
                niveau_urgence TEXT DEFAULT 'normal',
                
                -- Informations architecte (après attribution)
                architecte_assigne TEXT,  -- Nom de l'architecte ou firme
                numero_oaq TEXT,  -- Numéro de l'Ordre des Architectes du Québec
                
                -- Documents de l'architecte
                plans_preliminaires TEXT,  -- Plans concept base64
                plans_finaux TEXT,  -- Plans finaux scellés base64
                devis_architecture TEXT,  -- Devis descriptif base64
                rapport_urbanisme TEXT,  -- Analyse réglementaire base64
                estimation_couts_construction TEXT,  -- Estimation détaillée
                
                -- Tarification et facturation
                prix_service REAL,  -- Prix du service d'architecture
                modalite_paiement TEXT,  -- 'forfait', 'pourcentage', 'horaire'
                pourcentage_complete INTEGER DEFAULT 0,  -- Progression du projet
                
                -- Statuts et suivi
                statut TEXT DEFAULT 'recue',  -- 'recue', 'en_analyse', 'acceptee', 'en_cours', 'revision', 'approuvee', 'livree', 'terminee'
                notes_internes TEXT,
                commentaires_client TEXT,
                raison_refus TEXT,  -- Si projet refusé
                
                -- Dates de suivi
                date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_analyse TIMESTAMP,
                date_acceptation TIMESTAMP,
                date_debut_plans TIMESTAMP,
                date_revision TIMESTAMP,
                date_approbation TIMESTAMP,
                date_livraison TIMESTAMP,
                date_paiement TIMESTAMP,
                
                -- Références
                numero_reference TEXT UNIQUE,  -- SEAOP-ARCH-XXXXX
                numero_projet_architecte TEXT,  -- Référence interne architecte
                lead_id INTEGER,  -- Lien éventuel vers un appel d'offres
                
                -- Conformité et validations
                conforme_zonage BOOLEAN,
                conforme_cnb BOOLEAN,  -- Code National du Bâtiment
                validation_ingenieur BOOLEAN,
                validation_urbanisme BOOLEAN,
                
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        # Créer les index pour optimiser les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arch_statut ON demandes_architecture(statut)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arch_client ON demandes_architecture(email_client)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arch_date ON demandes_architecture(date_demande)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arch_superficie ON demandes_architecture(superficie_batiment)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arch_reference ON demandes_architecture(numero_reference)')
        
        print("[OK] Table 'demandes_architecture' creee avec succes")
        
        # Vérifier si on doit ajouter des données de démonstration
        cursor.execute("SELECT COUNT(*) FROM demandes_architecture")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Ajout de données de démonstration...")
            
            # Ajouter 2 demandes de démonstration
            demandes_demo = [
                {
                    'nom_client': 'Corporation Immobilière Montréal',
                    'email_client': 'projets@corp-immo-mtl.com',
                    'telephone_client': '514-555-8900',
                    'adresse_projet': '1234 Boulevard René-Lévesque',
                    'ville': 'Montréal',
                    'code_postal': 'H3B 4W8',
                    'type_batiment': 'commercial',
                    'usage_batiment': 'Immeuble de bureaux classe A avec rez-de-chaussée commercial',
                    'superficie_terrain': 15000,
                    'superficie_batiment': 45000,
                    'nombre_etages': 6,
                    'type_construction': 'nouvelle',
                    'style_architectural': 'contemporain',
                    'contraintes_terrain': 'Terrain en coin avec servitude de passage. Proximité métro.',
                    'exigences_speciales': 'Certification LEED Or visée. Accessibilité universelle complète.',
                    'plans_requis': 'complet',
                    'services_inclus': 'structure,mecanique,electrique,civil',
                    'besoin_3d': 1,
                    'besoin_permis': 1,
                    'budget_construction': '15 000 000$ - 18 000 000$',
                    'budget_architecture': '750 000$ - 900 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=90)).isoformat(),
                    'date_livraison_plans': (datetime.date.today() + datetime.timedelta(days=60)).isoformat(),
                    'niveau_urgence': 'normal',
                    'prix_service': 850000.00,
                    'modalite_paiement': 'pourcentage',
                    'statut': 'en_analyse',
                    'numero_reference': f'SEAOP-ARCH-{datetime.datetime.now().strftime("%Y%m%d")}-001',
                    'notes_internes': 'Projet majeur nécessitant coordination avec plusieurs consultants.'
                },
                {
                    'nom_client': 'Développements Résidentiels Laval Inc.',
                    'email_client': 'info@dev-residentiel-laval.ca',
                    'telephone_client': '450-555-3456',
                    'adresse_projet': '789 Avenue des Prairies',
                    'ville': 'Laval',
                    'code_postal': 'H7N 2T8',
                    'type_batiment': 'résidentiel',
                    'usage_batiment': 'Complexe de 3 bâtiments de condominiums avec espaces communs',
                    'superficie_terrain': 25000,
                    'superficie_batiment': 72000,
                    'nombre_etages': 4,
                    'nombre_logements': 84,
                    'type_construction': 'nouvelle',
                    'style_architectural': 'moderne',
                    'contraintes_terrain': 'Terrain avec dénivelé important. Zone inondable 0-20 ans partielle.',
                    'exigences_speciales': 'Insonorisation supérieure. Toits verts. Stationnement souterrain.',
                    'plans_requis': 'preliminaire',
                    'services_inclus': 'structure,mecanique,electrique',
                    'besoin_3d': 1,
                    'besoin_permis': 1,
                    'budget_construction': '22 000 000$ - 25 000 000$',
                    'budget_architecture': '1 100 000$ - 1 250 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=120)).isoformat(),
                    'date_livraison_plans': (datetime.date.today() + datetime.timedelta(days=45)).isoformat(),
                    'niveau_urgence': 'eleve',
                    'prix_service': 125000.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'recue',
                    'numero_reference': f'SEAOP-ARCH-{datetime.datetime.now().strftime("%Y%m%d")}-002',
                    'notes_internes': 'Client régulier. Prévoir rencontre avec urbanisme municipal.'
                }
            ]
            
            for demande in demandes_demo:
                placeholders = ', '.join(['?' for _ in demande])
                columns = ', '.join(demande.keys())
                cursor.execute(f'''
                    INSERT INTO demandes_architecture ({columns})
                    VALUES ({placeholders})
                ''', list(demande.values()))
            
            print(f"[OK] {len(demandes_demo)} demandes d'architecture de demonstration ajoutees")
            
            # Créer des notifications pour l'admin
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_architecture',
                '🏛️ Nouvelle demande d\'architecture',
                'Corporation Immobilière Montréal - Immeuble 45,000 pi²',
                1
            ))
            
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_architecture',
                '🏛️ Demande urgente d\'architecture',
                'Développements Résidentiels Laval - Complexe 72,000 pi²',
                2
            ))
            
            print("[OK] Notifications creees pour les nouvelles demandes")
        
        conn.commit()
        print("\n[OK] Module Service d'Architecture ajoute avec succes a SEAOP!")
        print("\nCaracteristiques du module :")
        print("- Gestion des projets > 6,000 pi2 necessitant architecte")
        print("- Workflow complet de la demande a la livraison")
        print("- Support multi-types de batiments")
        print("- Gestion des documents et plans")
        print("- Conformite OAQ et codes du batiment")
        print("- Integration avec les appels d'offres")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout du module : {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_architecture_table()