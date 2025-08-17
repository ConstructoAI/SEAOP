#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter la table demandes_ingenieur à SEAOP
Module de service d'ingénieur en structure pour calculs et plans structuraux
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '.')  # Utiliser le répertoire courant par défaut
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def add_ingenieur_table():
    """Ajoute la table pour les demandes de services d'ingénieur en structure"""
    
    print("Ajout du module Service d'Ingenieur en Structure a SEAOP...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Créer la table demandes_ingenieur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demandes_ingenieur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Informations client
                nom_client TEXT NOT NULL,
                email_client TEXT NOT NULL,
                telephone_client TEXT NOT NULL,
                adresse_projet TEXT NOT NULL,
                ville TEXT NOT NULL,
                code_postal TEXT NOT NULL,
                
                -- Détails du projet structural
                type_structure TEXT NOT NULL,  -- 'batiment', 'pont', 'industriel', 'fondation', 'autre'
                type_batiment TEXT,  -- 'résidentiel', 'commercial', 'industriel', 'institutionnel'
                usage_structure TEXT NOT NULL,  -- Description de l'usage
                superficie_projet REAL,  -- En pieds carrés
                hauteur_structure REAL,  -- En pieds
                nombre_etages INTEGER DEFAULT 1,
                charge_exploitation TEXT,  -- Description des charges prévues
                
                -- Spécifications techniques
                type_construction TEXT,  -- 'acier', 'beton', 'bois', 'mixte'
                sol_porteur TEXT,  -- Type de sol et capacité portante
                zone_sismique TEXT,  -- Zone sismique du projet
                contraintes_particulieres TEXT,  -- Contraintes spéciales
                normes_requises TEXT,  -- CNB, CSA, autres normes
                
                -- Services requis
                services_demandes TEXT NOT NULL,  -- 'calculs', 'plans', 'surveillance', 'complet'
                calculs_requis TEXT,  -- Types de calculs nécessaires
                plans_requis TEXT,  -- Types de plans structuraux
                surveillance_chantier BOOLEAN DEFAULT 0,  -- Surveillance requise
                certification_requise BOOLEAN DEFAULT 1,  -- Sceau d'ingénieur requis
                
                -- Documents du client
                plans_architecte TEXT,  -- Plans d'architecte base64
                etude_sol TEXT,  -- Rapport géotechnique base64
                photos_existant TEXT,  -- Photos de l'existant base64
                autres_documents TEXT,  -- Autres documents base64
                
                -- Budget et délais
                budget_structure TEXT,  -- Budget pour structure
                budget_ingenieur TEXT,  -- Budget pour services d'ingénieur
                date_debut_souhaite DATE,
                date_livraison_souhaite DATE,
                niveau_urgence TEXT DEFAULT 'normal',
                
                -- Informations ingénieur (après attribution)
                ingenieur_assigne TEXT,  -- Nom de l'ingénieur ou firme
                numero_oiq TEXT,  -- Numéro de l'Ordre des Ingénieurs du Québec
                
                -- Livrables de l'ingénieur
                calculs_structures TEXT,  -- Calculs structuraux base64
                plans_structures TEXT,  -- Plans structuraux base64
                specifications_techniques TEXT,  -- Devis techniques base64
                rapport_surveillance TEXT,  -- Rapport de surveillance base64
                certificat_conformite TEXT,  -- Certificat de conformité base64
                
                -- Tarification et facturation
                prix_service REAL,  -- Prix du service d'ingénieur
                modalite_paiement TEXT,  -- 'forfait', 'horaire', 'pourcentage'
                taux_horaire REAL,  -- Taux horaire si applicable
                pourcentage_complete INTEGER DEFAULT 0,  -- Progression du projet
                
                -- Statuts et suivi
                statut TEXT DEFAULT 'recue',  -- 'recue', 'analyse', 'acceptee', 'calculs', 'plans', 'revision', 'terminee'
                notes_internes TEXT,
                commentaires_client TEXT,
                raison_refus TEXT,  -- Si projet refusé
                
                -- Dates de suivi
                date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_analyse TIMESTAMP,
                date_acceptation TIMESTAMP,
                date_debut_calculs TIMESTAMP,
                date_fin_calculs TIMESTAMP,
                date_debut_plans TIMESTAMP,
                date_fin_plans TIMESTAMP,
                date_livraison TIMESTAMP,
                date_paiement TIMESTAMP,
                
                -- Références
                numero_reference TEXT UNIQUE,  -- SEAOP-ING-XXXXX
                numero_projet_ingenieur TEXT,  -- Référence interne ingénieur
                lead_id INTEGER,  -- Lien éventuel vers un appel d'offres
                demande_architecture_id INTEGER,  -- Lien vers demande d'architecture
                
                -- Conformité et validations
                conforme_cnb BOOLEAN,  -- Code National du Bâtiment
                conforme_csa BOOLEAN,  -- Normes CSA
                validation_pairs BOOLEAN,  -- Validation par pairs
                
                -- Spécialités techniques
                analyse_sismique BOOLEAN DEFAULT 0,
                analyse_vent BOOLEAN DEFAULT 0,
                analyse_neige BOOLEAN DEFAULT 0,
                analyse_dynamique BOOLEAN DEFAULT 0,
                modelisation_3d BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (lead_id) REFERENCES leads (id),
                FOREIGN KEY (demande_architecture_id) REFERENCES demandes_architecture (id)
            )
        ''')
        
        # Créer les index pour optimiser les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ing_statut ON demandes_ingenieur(statut)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ing_client ON demandes_ingenieur(email_client)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ing_date ON demandes_ingenieur(date_demande)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ing_type ON demandes_ingenieur(type_structure)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ing_reference ON demandes_ingenieur(numero_reference)')
        
        print("[OK] Table 'demandes_ingenieur' creee avec succes")
        
        # Vérifier si on doit ajouter des données de démonstration
        cursor.execute("SELECT COUNT(*) FROM demandes_ingenieur")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Ajout de donnees de demonstration...")
            
            # Ajouter 3 demandes de démonstration
            demandes_demo = [
                {
                    'nom_client': 'Développements Urbains Québec Inc.',
                    'email_client': 'structure@dev-urbain-qc.com',
                    'telephone_client': '418-555-2100',
                    'adresse_projet': '555 Grande Allée Est',
                    'ville': 'Québec',
                    'code_postal': 'G1R 2K2',
                    'type_structure': 'batiment',
                    'type_batiment': 'commercial',
                    'usage_structure': 'Centre commercial 3 étages avec stationnement souterrain 2 niveaux',
                    'superficie_projet': 85000,
                    'hauteur_structure': 45,
                    'nombre_etages': 3,
                    'charge_exploitation': 'Magasins: 250 lb/pi², Aires communes: 100 lb/pi², Stationnement: 50 lb/pi²',
                    'type_construction': 'mixte',
                    'sol_porteur': 'Argile dense, capacité 4000 lb/pi² à 8 pieds',
                    'zone_sismique': 'Zone 2 - Risque sismique modéré',
                    'contraintes_particulieres': 'Proximité métro, vibrations à considérer. Excavation limitée.',
                    'normes_requises': 'CNB 2020, CSA A23.3, CSA S16',
                    'services_demandes': 'complet',
                    'calculs_requis': 'Fondations, structure principale, dalles, analyse sismique',
                    'plans_requis': 'Plans de fondation, charpente, détails connexions',
                    'surveillance_chantier': 1,
                    'certification_requise': 1,
                    'budget_structure': '2 500 000$ - 3 000 000$',
                    'budget_ingenieur': '125 000$ - 150 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=60)).isoformat(),
                    'date_livraison_souhaite': (datetime.date.today() + datetime.timedelta(days=45)).isoformat(),
                    'niveau_urgence': 'normal',
                    'prix_service': 135000.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'analyse',
                    'numero_reference': f'SEAOP-ING-{datetime.datetime.now().strftime("%Y%m%d")}-001',
                    'notes_internes': 'Projet complexe nécessitant modélisation 3D pour analyse sismique.',
                    'analyse_sismique': 1,
                    'analyse_vent': 1,
                    'modelisation_3d': 1
                },
                {
                    'nom_client': 'Habitations Rive-Sud Ltée',
                    'email_client': 'projets@habitations-rs.ca',
                    'telephone_client': '450-555-7890',
                    'adresse_projet': '789 Chemin des Patriotes',
                    'ville': 'Longueuil',
                    'code_postal': 'J4K 3M7',
                    'type_structure': 'batiment',
                    'type_batiment': 'résidentiel',
                    'usage_structure': 'Immeuble résidentiel 6 étages, 48 logements',
                    'superficie_projet': 32000,
                    'hauteur_structure': 65,
                    'nombre_etages': 6,
                    'charge_exploitation': 'Logements: 40 lb/pi², Corridors: 80 lb/pi², Toiture: 30 lb/pi²',
                    'type_construction': 'beton',
                    'sol_porteur': 'Sable dense et gravier, capacité 6000 lb/pi² à 6 pieds',
                    'zone_sismique': 'Zone 3 - Risque sismique élevé',
                    'contraintes_particulieres': 'Hauteur limitée par zonage. Isolation acoustique renforcée.',
                    'normes_requises': 'CNB 2020, CSA A23.3',
                    'services_demandes': 'calculs',
                    'calculs_requis': 'Structure béton, dalles, murs porteurs, fondations',
                    'plans_requis': 'Plans structure générale',
                    'surveillance_chantier': 0,
                    'certification_requise': 1,
                    'budget_structure': '950 000$ - 1 200 000$',
                    'budget_ingenieur': '35 000$ - 45 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                    'date_livraison_souhaite': (datetime.date.today() + datetime.timedelta(days=21)).isoformat(),
                    'niveau_urgence': 'eleve',
                    'prix_service': 42000.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'recue',
                    'numero_reference': f'SEAOP-ING-{datetime.datetime.now().strftime("%Y%m%d")}-002',
                    'notes_internes': 'Client régulier. Projet standard mais délai serré.',
                    'analyse_sismique': 1,
                    'analyse_vent': 1
                },
                {
                    'nom_client': 'Industries Mauricie Inc.',
                    'email_client': 'expansion@industries-mauricie.com',
                    'telephone_client': '819-555-4567',
                    'adresse_projet': '1200 Boulevard Industriel',
                    'ville': 'Trois-Rivières',
                    'code_postal': 'G8T 5L9',
                    'type_structure': 'industriel',
                    'type_batiment': 'industriel',
                    'usage_structure': 'Entrepôt avec pont roulant 20 tonnes et bureaux administratifs',
                    'superficie_projet': 15000,
                    'hauteur_structure': 28,
                    'nombre_etages': 1,
                    'charge_exploitation': 'Entrepôt: 500 lb/pi², Pont roulant: 20T, Bureaux: 50 lb/pi²',
                    'type_construction': 'acier',
                    'sol_porteur': 'Roc à 4 pieds, capacité portante excellente',
                    'zone_sismique': 'Zone 1 - Risque sismique faible',
                    'contraintes_particulieres': 'Pont roulant existant à intégrer. Expansion future prévue.',
                    'normes_requises': 'CNB 2020, CSA S16, AISC',
                    'services_demandes': 'plans',
                    'calculs_requis': 'Charpente acier, connexions, fondations ponctuelles',
                    'plans_requis': 'Plans charpente acier, détails connexions, fondations',
                    'surveillance_chantier': 1,
                    'certification_requise': 1,
                    'budget_structure': '380 000$ - 450 000$',
                    'budget_ingenieur': '28 000$ - 35 000$',
                    'date_debut_souhaite': (datetime.date.today() + datetime.timedelta(days=45)).isoformat(),
                    'date_livraison_souhaite': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                    'niveau_urgence': 'normal',
                    'prix_service': 32000.00,
                    'modalite_paiement': 'forfait',
                    'statut': 'acceptee',
                    'numero_reference': f'SEAOP-ING-{datetime.datetime.now().strftime("%Y%m%d")}-003',
                    'notes_internes': 'Projet industriel standard. Client a déjà travaillé avec nous.',
                    'pourcentage_complete': 15,
                    'analyse_vent': 1
                }
            ]
            
            for demande in demandes_demo:
                placeholders = ', '.join(['?' for _ in demande])
                columns = ', '.join(demande.keys())
                cursor.execute(f'''
                    INSERT INTO demandes_ingenieur ({columns})
                    VALUES ({placeholders})
                ''', list(demande.values()))
            
            print(f"[OK] {len(demandes_demo)} demandes d'ingenieur de demonstration ajoutees")
            
            # Créer des notifications pour l'admin
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_ingenieur',
                'Nouvelle demande d\'ingenieur',
                'Developpements Urbains Quebec - Centre commercial 85,000 pi2',
                1
            ))
            
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_ingenieur',
                'Demande urgente d\'ingenieur',
                'Habitations Rive-Sud - Immeuble 6 etages urgent',
                2
            ))
            
            cursor.execute('''
                INSERT INTO notifications (
                    utilisateur_type, utilisateur_id, type_notification,
                    titre, message, lien_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'admin', 0, 'nouvelle_demande_ingenieur',
                'Projet industriel accepte',
                'Industries Mauricie - Entrepot avec pont roulant',
                3
            ))
            
            print("[OK] Notifications creees pour les nouvelles demandes")
        
        conn.commit()
        print("\n[OK] Module Service d'Ingenieur en Structure ajoute avec succes a SEAOP!")
        print("\nCaracteristiques du module :")
        print("- Calculs et plans structuraux par ingenieur OIQ")
        print("- Support multi-materiaux (acier, beton, bois, mixte)")
        print("- Analyses sismique, vent et neige")
        print("- Surveillance de chantier optionnelle")
        print("- Conformite CNB et normes CSA")
        print("- Integration avec modules architecture et appels d'offres")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout du module : {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_ingenieur_table()