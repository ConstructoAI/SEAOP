import sqlite3
import datetime
import hashlib
import random
import os

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_PATH)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database_with_soumissions():
    """Initialise la base de données avec support des soumissions directes"""
    
    # Backup de l'ancienne base si elle existe
    if os.path.exists(DATABASE_PATH):
        backup_name = os.path.join(DATA_DIR, f'seaop_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        os.rename(DATABASE_PATH, backup_name)
        print(f"Backup cree: {backup_name}")
    elif os.path.exists('soumissions_quebec.db'):
        backup_name = os.path.join(DATA_DIR, f'soumissions_quebec_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        if os.path.exists('soumissions_quebec.db'):
            os.rename('soumissions_quebec.db', backup_name)
            print(f"Backup ancien systeme cree: {backup_name}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table des leads (projets clients) - MODIFIÉE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT NOT NULL,
            code_postal TEXT NOT NULL,
            type_projet TEXT NOT NULL,
            description TEXT NOT NULL,
            budget TEXT NOT NULL,
            delai_realisation TEXT NOT NULL,
            photos TEXT,
            plans TEXT,  -- Nouveau: stockage des plans/documents
            documents TEXT,  -- Nouveau: autres documents
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'nouveau',
            numero_reference TEXT UNIQUE,
            visible_entrepreneurs BOOLEAN DEFAULT 1,  -- Nouveau: visibilité
            accepte_soumissions BOOLEAN DEFAULT 1  -- Nouveau: accepte encore des soumissions
        )
    ''')
    
    # Table des entrepreneurs - INCHANGÉE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entrepreneurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_entreprise TEXT NOT NULL,
            nom_contact TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT NOT NULL,
            mot_de_passe_hash TEXT NOT NULL,
            numero_rbq TEXT,
            zones_desservies TEXT,
            types_projets TEXT,
            abonnement TEXT DEFAULT 'gratuit',
            credits_restants INTEGER DEFAULT 5,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'actif',
            certifications TEXT,
            evaluations_moyenne REAL DEFAULT 0.0,  -- Nouveau: note moyenne
            nombre_evaluations INTEGER DEFAULT 0  -- Nouveau: nombre d'évaluations
        )
    ''')
    
    # NOUVELLE TABLE: Soumissions des entrepreneurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soumissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            entrepreneur_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            description_travaux TEXT NOT NULL,
            delai_execution TEXT NOT NULL,
            validite_offre TEXT NOT NULL,
            inclusions TEXT,
            exclusions TEXT,
            conditions TEXT,
            documents TEXT,  -- Documents attachés à la soumission
            statut TEXT DEFAULT 'envoyee',  -- envoyee, vue, acceptee, refusee
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP,
            vue_par_client BOOLEAN DEFAULT 0,
            notes_client TEXT,
            notes_entrepreneur TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id),
            UNIQUE(lead_id, entrepreneur_id)  -- Un entrepreneur ne peut soumettre qu'une fois par projet
        )
    ''')
    
    # NOUVELLE TABLE: Messages entre clients et entrepreneurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            entrepreneur_id INTEGER,
            expediteur_type TEXT NOT NULL,  -- 'client' ou 'entrepreneur'
            expediteur_id INTEGER NOT NULL,
            destinataire_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            pieces_jointes TEXT,
            date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            lu BOOLEAN DEFAULT 0,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id)
        )
    ''')
    
    # NOUVELLE TABLE: Évaluations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            evaluateur_type TEXT NOT NULL,  -- 'client' ou 'entrepreneur'
            note INTEGER NOT NULL CHECK(note >= 1 AND note <= 5),
            commentaire TEXT,
            date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id),
            UNIQUE(soumission_id, evaluateur_type)  -- Une évaluation par partie par soumission
        )
    ''')
    
    # Table des notifications - NOUVELLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_type TEXT NOT NULL,  -- 'client' ou 'entrepreneur'
            utilisateur_id INTEGER NOT NULL,
            type_notification TEXT NOT NULL,  -- 'nouvelle_soumission', 'soumission_acceptee', 'nouveau_message', 'nouvel_appel_offres', etc.
            titre TEXT NOT NULL,
            message TEXT NOT NULL,
            lien_id INTEGER,  -- ID du projet, soumission ou message concerné
            lu BOOLEAN DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des attributions (pour compatibilité) - MODIFIÉE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            entrepreneur_id INTEGER,
            date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'attribue',
            notes TEXT,
            prix_paye REAL DEFAULT 0.0,
            soumission_id INTEGER,  -- Nouveau: lien vers la soumission acceptée
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id),
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
        )
    ''')
    
    # Créer des index pour améliorer les performances
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_statut ON leads(statut)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soumissions_lead ON soumissions(lead_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soumissions_entrepreneur ON soumissions(entrepreneur_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_lead ON messages(lead_id)')
    
    # Insérer des données de démonstration
    
    # Entrepreneurs de démonstration
    entrepreneurs_demo = [
        {
            'nom_entreprise': 'Construction Excellence Inc.',
            'nom_contact': 'Jean Tremblay',
            'email': 'jean@construction-excellence.ca',
            'telephone': '514-555-1001',
            'mot_de_passe': 'demo123',
            'numero_rbq': '1234-5678-01',
            'zones_desservies': 'H1A,H1B,H1C,H2A,H2B,H3A,H3B,H4A',
            'types_projets': 'Rénovation cuisine,Rénovation salle de bain,Agrandissement',
            'abonnement': 'premium',
            'certifications': 'RBQ, APCHQ, Réno-Maître'
        },
        {
            'nom_entreprise': 'Toitures Pro Québec',
            'nom_contact': 'Marie Lavoie',
            'email': 'marie@toitures-pro.ca',
            'telephone': '418-555-2002',
            'mot_de_passe': 'demo123',
            'numero_rbq': '2345-6789-01',
            'zones_desservies': 'G1A,G1B,G1C,G2A,G2B',
            'types_projets': 'Toiture,Revêtement extérieur',
            'abonnement': 'standard',
            'certifications': 'RBQ, AMCQ, BP Canada'
        },
        {
            'nom_entreprise': 'Rénovations Modernes',
            'nom_contact': 'Pierre Gagnon',
            'email': 'pierre@renovations-modernes.ca',
            'telephone': '450-555-3003',
            'mot_de_passe': 'demo123',
            'numero_rbq': '3456-7890-01',
            'zones_desservies': 'J7A,J7B,J7C,J4A,J4B',
            'types_projets': 'Rénovation cuisine,Rénovation salle de bain,Plancher,Peinture',
            'abonnement': 'entreprise',
            'certifications': 'RBQ, APCHQ, Qualité Habitation'
        }
    ]
    
    # Insérer les entrepreneurs
    for entr in entrepreneurs_demo:
        cursor.execute('''
            INSERT INTO entrepreneurs (nom_entreprise, nom_contact, email, telephone, 
                                     mot_de_passe_hash, numero_rbq, zones_desservies, 
                                     types_projets, abonnement, credits_restants, certifications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entr['nom_entreprise'], entr['nom_contact'], entr['email'], entr['telephone'],
              hash_password(entr['mot_de_passe']), entr['numero_rbq'], entr['zones_desservies'],
              entr['types_projets'], entr['abonnement'], 100, entr['certifications']))
    
    # Projets de démonstration avec plus de détails
    leads_demo = [
        {
            'nom': 'Sophie Bergeron',
            'email': 'sophie.bergeron@email.com',
            'telephone': '514-123-4567',
            'code_postal': 'H2A 1A1',
            'type_projet': 'Rénovation cuisine',
            'description': '''Rénovation complète de cuisine dans une maison unifamiliale.
            
            Détails du projet:
            - Surface: 12x15 pieds (180 pi²)
            - Démolition de l'ancienne cuisine
            - Nouvelles armoires sur mesure (style moderne)
            - Comptoir en quartz blanc
            - Dosseret en céramique métro
            - Îlot central avec rangement
            - Nouvel évier sous-plan double
            - Robinetterie haut de gamme
            - Installation de 4 électroménagers encastrés
            - Éclairage sous les armoires (LED)
            - Plancher en vinyle de luxe
            - Peinture complète
            
            Contraintes:
            - Conserver la plomberie existante si possible
            - Travaux du lundi au vendredi seulement
            - Animaux dans la maison (2 chats)''',
            'budget': '30 000$ - 50 000$',
            'delai_realisation': 'Dans 2-3 mois',
            'numero_reference': 'SEAOP-20240301-ABC12345'
        },
        {
            'nom': 'Michel Tremblay',
            'email': 'michel.tremblay@email.com',
            'telephone': '418-987-6543',
            'code_postal': 'G1A 1B1',
            'type_projet': 'Toiture',
            'description': '''Remplacement complet de la toiture - URGENT
            
            Situation actuelle:
            - Toiture en bardeaux d'asphalte de 22 ans
            - Infiltrations d'eau détectées dans le grenier
            - Plusieurs bardeaux manquants suite aux vents
            
            Travaux requis:
            - Enlèvement complet de l'ancienne toiture
            - Inspection et réparation du support si nécessaire
            - Installation membrane synthétique haute qualité
            - Bardeaux architecturaux 30 ans minimum
            - Remplacement des solins
            - Installation de ventilation adéquate
            - Gouttières à inspecter et réparer au besoin
            
            Spécifications:
            - Maison à étages, environ 1800 pi² de toiture
            - Pente 6/12
            - 2 cheminées
            - 4 évents de plomberie''',
            'budget': 'Plus de 50 000$',
            'delai_realisation': 'Dès que possible',
            'numero_reference': 'SEAOP-20240302-DEF67890'
        },
        {
            'nom': 'Catherine Larose',
            'email': 'catherine.larose@email.com',
            'telephone': '450-555-7890',
            'code_postal': 'J4A 2C3',
            'type_projet': 'Rénovation salle de bain',
            'description': '''Transformation complète salle de bain principale
            
            Vision du projet:
            - Style spa moderne et épuré
            - Douche italienne sans seuil
            - Bain autoportant
            - Double vanité flottante
            
            Dimensions: 10x12 pieds
            
            Travaux spécifiques:
            - Démolition complète jusqu'aux montants
            - Reconfiguration de la plomberie
            - Ajout d'un drain linéaire pour douche
            - Membrane d'étanchéité complète
            - Chauffage radiant au plancher
            - Carrelage grand format (24x48)
            - Niche encastrée dans la douche
            - Robinetterie noire mat
            - Miroir LED anti-buée
            - Ventilateur silencieux avec humidistat
            
            Préférences:
            - Palette de couleurs: blanc, gris, noir
            - Finitions haut de gamme
            - Éclairage sur gradateur''',
            'budget': '15 000$ - 30 000$',
            'delai_realisation': 'Dans 1 mois',
            'numero_reference': 'SEAOP-20240303-GHI23456'
        }
    ]
    
    # Insérer les projets
    for lead in leads_demo:
        cursor.execute('''
            INSERT INTO leads (nom, email, telephone, code_postal, type_projet, 
                              description, budget, delai_realisation, numero_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lead['nom'], lead['email'], lead['telephone'], lead['code_postal'], 
              lead['type_projet'], lead['description'], lead['budget'], 
              lead['delai_realisation'], lead['numero_reference']))
    
    # Créer des soumissions de démonstration
    soumissions_demo = [
        {
            'lead_id': 1,  # Projet cuisine de Sophie
            'entrepreneur_id': 1,  # Construction Excellence
            'montant': 42500.00,
            'description_travaux': '''SOUMISSION - RÉNOVATION CUISINE COMPLÈTE
            
            Notre proposition inclut:
            
            DÉMOLITION ET PRÉPARATION (3 jours)
            - Démolition complète de l'ancienne cuisine
            - Protection des zones adjacentes
            - Disposition des débris
            
            TRAVAUX STRUCTURAUX (2 jours)
            - Vérification et renforcement si nécessaire
            - Ajustements pour l'îlot central
            
            PLOMBERIE ET ÉLECTRICITÉ (3 jours)
            - Déplacement plomberie pour îlot
            - Nouveaux circuits pour électroménagers
            - Éclairage sous armoires LED
            
            MENUISERIE (5 jours)
            - Armoires sur mesure en mélamine
            - Îlot central avec rangement
            - Installation professionnelle
            
            FINITION (5 jours)
            - Comptoir quartz 3cm
            - Dosseret céramique
            - Plancher vinyle luxe
            - Peinture 2 couches
            
            TOTAL: 18 jours ouvrables''',
            'delai_execution': '4 semaines',
            'validite_offre': '30 jours',
            'inclusions': '''- Tous matériaux et main d'œuvre
            - Protection des lieux
            - Nettoyage quotidien
            - Garantie 2 ans main d'œuvre
            - Garantie fabricant sur matériaux
            - Coordination des sous-traitants
            - Plans détaillés''',
            'exclusions': '''- Électroménagers
            - Déménagement du contenu
            - Permis municipaux
            - Modifications structurales majeures''',
            'conditions': '''- Acompte 30% à la signature
            - 40% mi-projet
            - 30% à la fin
            - Accès aux lieux requis
            - Décisions dans les 48h''',
            'statut': 'envoyee'
        },
        {
            'lead_id': 1,  # Même projet cuisine
            'entrepreneur_id': 3,  # Rénovations Modernes
            'montant': 38900.00,
            'description_travaux': '''PROPOSITION - RÉNOVATION CUISINE CLÉ EN MAIN
            
            Solution complète incluant:
            
            PHASE 1: DÉMOLITION (2 jours)
            - Retrait complet ancienne cuisine
            - Protection plastique zones adjacentes
            
            PHASE 2: INFRASTRUCTURE (4 jours)
            - Ajustements électriques
            - Plomberie pour îlot
            - Préparation des murs
            
            PHASE 3: INSTALLATION (8 jours)
            - Armoires IKEA série SEKTION
            - Façades personnalisées
            - Comptoir stratifié effet quartz
            - Dosseret tuiles métro
            - Plancher flottant résistant eau
            
            PHASE 4: FINITION (3 jours)
            - Peinture complète
            - Ajustements finaux
            - Nettoyage
            
            Durée totale: 17 jours''',
            'delai_execution': '3-4 semaines',
            'validite_offre': '14 jours',
            'inclusions': 'Tout inclus sauf électroménagers',
            'exclusions': 'Permis, électroménagers, déménagement',
            'conditions': '40% départ, 40% mi-chemin, 20% fin',
            'statut': 'vue'
        },
        {
            'lead_id': 2,  # Projet toiture de Michel
            'entrepreneur_id': 2,  # Toitures Pro
            'montant': 18750.00,
            'description_travaux': '''DEVIS - RÉFECTION COMPLÈTE TOITURE
            
            URGENT - Disponibilité dans 5 jours
            
            Travaux proposés:
            
            1. ENLÈVEMENT (1 jour)
            - Retrait bardeaux existants
            - Inspection complète du support
            - Réparations mineures incluses
            
            2. PRÉPARATION (1 jour)
            - Membrane autocollante Ice & Water
            - Membrane synthétique Titanium
            - Larmiers aluminium
            
            3. INSTALLATION (2 jours)
            - Bardeaux GAF Timberline HDZ
            - Garantie 30 ans
            - Faîtières ventilées
            - Solins aluminium
            
            4. FINITION (0.5 jour)
            - Évents de plomberie
            - Tour des cheminées
            - Nettoyage complet
            
            GARANTIE 10 ANS sur installation''',
            'delai_execution': 'Début dans 5 jours',
            'validite_offre': '7 jours vu l\'urgence',
            'inclusions': 'Tout matériel et main d\'œuvre, conteneur, permis',
            'exclusions': 'Réparations structurales majeures si nécessaires',
            'conditions': 'Paiement sur réception, inspection disponible',
            'statut': 'acceptee'
        }
    ]
    
    # Insérer les soumissions
    for soum in soumissions_demo:
        cursor.execute('''
            INSERT INTO soumissions (lead_id, entrepreneur_id, montant, description_travaux,
                                   delai_execution, validite_offre, inclusions, exclusions,
                                   conditions, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (soum['lead_id'], soum['entrepreneur_id'], soum['montant'], 
              soum['description_travaux'], soum['delai_execution'], soum['validite_offre'],
              soum['inclusions'], soum['exclusions'], soum['conditions'], soum['statut']))
    
    # Créer quelques messages de démonstration
    messages_demo = [
        {
            'lead_id': 1,
            'entrepreneur_id': 1,
            'expediteur_type': 'entrepreneur',
            'expediteur_id': 1,
            'destinataire_id': 1,
            'message': 'Bonjour Mme Bergeron, merci pour votre demande. J\'ai préparé une soumission détaillée pour votre projet de cuisine. N\'hésitez pas si vous avez des questions!'
        },
        {
            'lead_id': 1,
            'entrepreneur_id': 1,
            'expediteur_type': 'client',
            'expediteur_id': 1,
            'destinataire_id': 1,
            'message': 'Merci pour votre soumission. Est-il possible d\'avoir des armoires en bois massif plutôt qu\'en mélamine?'
        },
        {
            'lead_id': 2,
            'entrepreneur_id': 2,
            'expediteur_type': 'entrepreneur',
            'expediteur_id': 2,
            'destinataire_id': 2,
            'message': 'M. Tremblay, vu l\'urgence de votre situation, nous pouvons commencer dès lundi prochain. Confirmez-vous l\'acceptation de notre soumission?'
        }
    ]
    
    # Insérer les messages
    for msg in messages_demo:
        cursor.execute('''
            INSERT INTO messages (lead_id, entrepreneur_id, expediteur_type, 
                                expediteur_id, destinataire_id, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (msg['lead_id'], msg['entrepreneur_id'], msg['expediteur_type'],
              msg['expediteur_id'], msg['destinataire_id'], msg['message']))
    
    conn.commit()
    conn.close()
    
    print("Base de donnees initialisee avec succes!")
    print("\nDonnees creees:")
    print("   - 3 entrepreneurs avec comptes demo")
    print("   - 3 projets detailles avec descriptions completes")
    print("   - 3 soumissions detaillees")
    print("   - 3 messages de demonstration")
    print("\nComptes de test:")
    print("   - Admin: mot de passe 'admin123'")
    print("   - Entrepreneurs: emails ci-dessus + mot de passe 'demo123'")
    print("\nNouvelles fonctionnalites:")
    print("   - Upload de plans et documents")
    print("   - Soumissions directes des entrepreneurs")
    print("   - Messagerie integree")
    print("   - Systeme d'evaluation")

if __name__ == "__main__":
    init_database_with_soumissions()