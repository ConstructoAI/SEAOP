#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter la table demandes_technologue à SEAOP
Module de service de technologue pour projets ≤ 6000 pi²
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '.')  # Utiliser le répertoire courant par défaut
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def add_technologue_table():
    """Ajoute la table pour les demandes de services de technologue"""
    
    print("Ajout du module Service de Technologue a SEAOP...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Créer la table demandes_technologue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demandes_technologue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Informations client
                nom_client TEXT NOT NULL,
                email_client TEXT NOT NULL,
                telephone_client TEXT NOT NULL,
                adresse_projet TEXT NOT NULL,
                ville TEXT NOT NULL,
                code_postal TEXT NOT NULL,
                
                -- Détails du projet technique
                type_batiment TEXT NOT NULL,  -- 'résidentiel', 'commercial', 'industriel', 'garage', 'cabanon'
                usage_batiment TEXT NOT NULL,  -- Description de l'usage prévu
                superficie_terrain REAL,  -- En pieds carrés
                superficie_batiment REAL NOT NULL,  -- En pieds carrés (doit être ≤ 6000)
                nombre_etages INTEGER DEFAULT 1,
                nombre_pieces INTEGER,  -- Nombre de pièces/espaces
                
                -- Spécifications techniques
                type_construction TEXT,  -- 'nouvelle', 'agrandissement', 'renovation', 'garage', 'remise'
                style_architectural TEXT,  -- 'traditionnel', 'moderne', 'rustique', 'contemporain'
                contraintes_terrain TEXT,  -- Pente, servitudes, etc.
                exigences_speciales TEXT,  -- Accessibilité, isolation, etc.
                
                -- Services requis
                plans_requis TEXT NOT NULL,  -- 'complet', 'preliminaire', 'concept', 'permis'
                services_inclus TEXT,  -- Services additionnels inclus
                besoin_3d BOOLEAN DEFAULT 0,  -- Modélisation 3D requise
                besoin_permis BOOLEAN DEFAULT 1,  -- Aide pour permis de construction
                visite_terrain BOOLEAN DEFAULT 0,  -- Visite sur site requise
                
                -- Documents du client
                certificat_localisation TEXT,  -- Document base64
                photos_terrain TEXT,  -- Photos actuelles base64
                croquis_client TEXT,  -- Esquisses du client base64
                documents_existants TEXT,  -- Plans existants base64
                
                -- Budget et délais
                budget_construction TEXT,  -- Budget total de construction estimé
                budget_technologue TEXT,  -- Budget pour services de technologue
                date_debut_souhaite DATE,
                date_livraison_plans DATE,
                niveau_urgence TEXT DEFAULT 'normal',
                
                -- Informations technologue (après attribution)
                technologue_assigne TEXT,  -- Nom du technologue ou firme
                numero_otaq TEXT,  -- Numéro de l'Ordre des Technologues du Québec
                
                -- Documents du technologue
                plans_preliminaires TEXT,  -- Plans concept base64
                plans_finaux TEXT,  -- Plans finaux base64
                devis_technique TEXT,  -- Devis descriptif base64
                rapport_conformite TEXT,  -- Analyse de conformité base64
                estimation_couts TEXT,  -- Estimation détaillée
                
                -- Tarification et facturation
                prix_service REAL,  -- Prix du service de technologue
                modalite_paiement TEXT,  -- 'forfait', 'houraire', 'par_plan'
                taux_horaire REAL,  -- Taux horaire si applicable
                pourcentage_complete INTEGER DEFAULT 0,  -- Progression du projet
                
                -- Statuts et suivi
                statut TEXT DEFAULT 'recue',  -- 'recue', 'analyse', 'acceptee', 'en_cours', 'revision', 'terminee'
                notes_internes TEXT,
                commentaires_client TEXT,
                raison_refus TEXT,  -- Si projet refusé
                
                -- Dates de suivi
                date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_analyse TIMESTAMP,
                date_acceptation TIMESTAMP,
                date_debut_plans TIMESTAMP,
                date_revision TIMESTAMP,
                date_livraison TIMESTAMP,
                date_paiement TIMESTAMP,
                
                -- Références
                numero_reference TEXT UNIQUE,  -- SEAOP-TECH-XXXXX
                numero_projet_technologue TEXT,  -- Référence interne technologue
                lead_id INTEGER,  -- Lien éventuel vers un appel d'offres
                
                -- Conformité et validations
                conforme_zonage BOOLEAN,
                conforme_cnb BOOLEAN,  -- Code National du Bâtiment
                conforme_municipal BOOLEAN,  -- Réglements municipaux
                validation_technique BOOLEAN,
                
                -- Types de plans spécialisés
                plan_implantation BOOLEAN DEFAULT 1,  -- Plan d'implantation
                plan_fondation BOOLEAN DEFAULT 1,  -- Plan de fondation
                plan_charpente BOOLEAN DEFAULT 1,  -- Plan de charpente
                plan_electricite BOOLEAN DEFAULT 0,  -- Plan électrique
                plan_plomberie BOOLEAN DEFAULT 0,  -- Plan de plomberie
                
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        # Créer les index pour optimiser les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_statut ON demandes_technologue(statut)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_client ON demandes_technologue(email_client)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_date ON demandes_technologue(date_demande)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_superficie ON demandes_technologue(superficie_batiment)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_reference ON demandes_technologue(numero_reference)')
        
        print("[OK] Table 'demandes_technologue' creee avec succes")
        
        # Vérifier si on doit ajouter des données de démonstration
        cursor.execute("SELECT COUNT(*) FROM demandes_technologue")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Ajout de donnees de demonstration...")
            
            # Ajouter 3 demandes de démonstration
            demandes_demo = [
                {
                    'nom_client': 'Famille Tremblay',
                    'email_client': 'renovation@tremblay-famille.ca',
                    'telephone_client': '418-555-1234',
                    'adresse_projet': '123 Rue des Érables',
                    'ville': 'Québec',
                    'code_postal': 'G1X 2Y3',
                    'type_batiment': 'résidentiel',
                    'usage_batiment': 'Agrandissement cuisine et ajout bureau à domicile',
                    'superficie_terrain': 8500,
                    'superficie_batiment': 4200,
                    'nombre_etages': 2,
                    'nombre_pieces': 8,
                    'type_construction': 'agrandissement',
                    'style_architectural': 'traditionnel',
                    'contraintes_terrain': 'Terrain en pente légère, proximité voisin côté ouest',
                    'exigences_speciales': 'Isolation supérieure R-40, fenêtres Energy Star',
                    'plans_requis': 'complet',
                    'services_inclus': 'implantation,fondation,charpente',
                    'besoin_3d': 1,
                    'besoin_permis': 1,
                    'visite_terrain': 1,
                    'budget_construction': '85 000$ - 110 000$',
                    'budget_technologue': '4 500$ - 6 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=45)).isoformat(),
                    'date_livraison_plans': (datetime.date.today() + datetime.timedelta(days=21)).isoformat(),
                    'niveau_urgence': 'normal',
                    'prix_service': 5200.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'en_cours',
                    'numero_reference': f'SEAOP-TECH-{datetime.datetime.now().strftime("%Y%m%d")}-001',
                    'notes_internes': 'Client régulier. Projet standard d\'agrandissement résidentiel.',
                    'pourcentage_complete': 35,
                    'plan_implantation': 1,
                    'plan_fondation': 1,
                    'plan_charpente': 1,
                    'plan_electricite': 1
                },
                {
                    'nom_client': 'Garage Mécanique Plus Inc.',
                    'email_client': 'projets@garageplus.qc.ca',
                    'telephone_client': '450-555-9876',
                    'adresse_projet': '456 Boulevard Industriel',
                    'ville': 'Longueuil',
                    'code_postal': 'J4H 3K8',
                    'type_batiment': 'commercial',
                    'usage_batiment': 'Garage mécanique avec bureau administratif et aire d\'attente',
                    'superficie_terrain': 12000,
                    'superficie_batiment': 5800,
                    'nombre_etages': 1,
                    'nombre_pieces': 6,
                    'type_construction': 'nouvelle',
                    'style_architectural': 'industriel',
                    'contraintes_terrain': 'Terrain plat, accès camions requis, drainage nécessaire',
                    'exigences_speciales': 'Fosse mécanique, système ventilation, compresseur air',
                    'plans_requis': 'complet',
                    'services_inclus': 'implantation,fondation,charpente,electricite,plomberie',
                    'besoin_3d': 0,
                    'besoin_permis': 1,
                    'visite_terrain': 1,
                    'budget_construction': '180 000$ - 220 000$',
                    'budget_technologue': '8 500$ - 11 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=60)).isoformat(),
                    'date_livraison_plans': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                    'niveau_urgence': 'eleve',
                    'prix_service': 9800.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'acceptee',
                    'numero_reference': f'SEAOP-TECH-{datetime.datetime.now().strftime("%Y%m%d")}-002',
                    'notes_internes': 'Projet commercial nécessitant expertise drainage et ventilation.',
                    'pourcentage_complete': 5,
                    'plan_implantation': 1,
                    'plan_fondation': 1,
                    'plan_charpente': 1,
                    'plan_electricite': 1,
                    'plan_plomberie': 1
                },
                {
                    'nom_client': 'Résidences Lac-Beauport',
                    'email_client': 'construction@lac-beauport.com',
                    'telephone_client': '418-555-4567',
                    'adresse_projet': '789 Chemin du Lac',
                    'ville': 'Lac-Beauport',
                    'code_postal': 'G3B 0X1',
                    'type_batiment': 'résidentiel',
                    'usage_batiment': 'Chalet 4 saisons avec garage attaché',
                    'superficie_terrain': 25000,
                    'superficie_batiment': 3200,
                    'nombre_etages': 2,
                    'nombre_pieces': 6,
                    'type_construction': 'nouvelle',
                    'style_architectural': 'rustique',
                    'contraintes_terrain': 'Terrain boisé en pente, vue sur lac à préserver',
                    'exigences_speciales': 'Fondation sur pilotis, bois rond, foyer central',
                    'plans_requis': 'complet',
                    'services_inclus': 'implantation,fondation,charpente',
                    'besoin_3d': 1,
                    'besoin_permis': 1,
                    'visite_terrain': 1,
                    'budget_construction': '280 000$ - 350 000$',
                    'budget_technologue': '6 000$ - 8 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=90)).isoformat(),
                    'date_livraison_plans': (datetime.date.today() + datetime.timedelta(days=45)).isoformat(),
                    'niveau_urgence': 'normal',
                    'prix_service': 7200.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'recue',
                    'numero_reference': f'SEAOP-TECH-{datetime.datetime.now().strftime("%Y%m%d")}-003',
                    'notes_internes': 'Projet chalet nécessitant expertise fondation sur pente.',
                    'plan_implantation': 1,
                    'plan_fondation': 1,
                    'plan_charpente': 1
                }
            ]
            
            for demande in demandes_demo:
                placeholders = ', '.join(['?' for _ in demande])
                columns = ', '.join(demande.keys())
                cursor.execute(f'''
                    INSERT INTO demandes_technologue ({columns})
                    VALUES ({placeholders})
                ''', list(demande.values()))
            
            print(f"[OK] {len(demandes_demo)} demandes de technologue de demonstration ajoutees")
            
            # Créer des notifications pour l'admin
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_technologue',
                'Nouvelle demande technologue',
                'Famille Tremblay - Agrandissement 4,200 pi2',
                1
            ))
            
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_technologue',
                'Demande urgente technologue',
                'Garage Mecanique Plus - Garage commercial 5,800 pi2',
                2
            ))
            
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_technologue',
                'Nouveau chalet a Lac-Beauport',
                'Residences Lac-Beauport - Chalet 4 saisons 3,200 pi2',
                3
            ))
            
            print("[OK] Notifications creees pour les nouvelles demandes")
        
        conn.commit()
        print("\n[OK] Module Service de Technologue ajoute avec succes a SEAOP!")
        print("\nCaracteristiques du module :")
        print("- Plans techniques pour projets <= 6,000 pi2")
        print("- Services de technologue en architecture")
        print("- Plans d'implantation, fondation, charpente")
        print("- Support electrique et plomberie optionnel")
        print("- Conformite codes du batiment et reglements municipaux")
        print("- Integration avec modules architecture et ingenieur")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout du module : {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_technologue_table()