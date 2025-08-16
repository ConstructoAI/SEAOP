import sqlite3
import datetime
import hashlib
import random

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database_with_demo_data():
    """Initialise la base de données avec des données de démonstration"""
    
    conn = sqlite3.connect('soumissions_quebec.db')
    cursor = conn.cursor()
    
    # Supprimer les tables existantes pour recommencer
    cursor.execute('DROP TABLE IF EXISTS attributions')
    cursor.execute('DROP TABLE IF EXISTS entrepreneurs')
    cursor.execute('DROP TABLE IF EXISTS leads')
    
    # Créer les tables
    # Table des leads
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
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'nouveau',
            numero_reference TEXT UNIQUE
        )
    ''')
    
    # Table des entrepreneurs
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
            certifications TEXT
        )
    ''')
    
    # Table des attributions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            entrepreneur_id INTEGER,
            date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'attribue',
            notes TEXT,
            prix_paye REAL DEFAULT 0.0,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id)
        )
    ''')
    
    # Données de démonstration pour entrepreneurs
    entrepreneurs_demo = [
        {
            'nom_entreprise': 'Construction Tremblay Inc.',
            'nom_contact': 'Jean Tremblay',
            'email': 'jean@constructiontremblay.ca',
            'telephone': '514-555-1001',
            'mot_de_passe': 'demo123',
            'numero_rbq': '1234-5678-01',
            'zones_desservies': 'H1A,H1B,H1C,H2A,H2B',
            'types_projets': 'Rénovation cuisine,Rénovation salle de bain,Agrandissement',
            'abonnement': 'premium',
            'credits_restants': 100,
            'certifications': 'RBQ, CNESST, Assurance responsabilité 2M$'
        },
        {
            'nom_entreprise': 'Électricité Moderne Québec',
            'nom_contact': 'Marie Leblanc',
            'email': 'marie@electrique-qc.ca',
            'telephone': '418-555-2002',
            'mot_de_passe': 'demo123',
            'numero_rbq': '2345-6789-01',
            'zones_desservies': 'G1A,G1B,G1C,G2A,G2B',
            'types_projets': 'Électricité',
            'abonnement': 'standard',
            'credits_restants': 35,
            'certifications': 'Maître électricien, RBQ, CMEQ'
        },
        {
            'nom_entreprise': 'Plomberie Excellence',
            'nom_contact': 'Pierre Gagnon',
            'email': 'pierre@plomberie-excellence.ca',
            'telephone': '450-555-3003',
            'mot_de_passe': 'demo123',
            'numero_rbq': '3456-7890-01',
            'zones_desservies': 'J7A,J7B,J7C,J4A,J4B',
            'types_projets': 'Plomberie,Rénovation salle de bain',
            'abonnement': 'standard',
            'credits_restants': 42,
            'certifications': 'Maître plombier, RBQ, CMMTQ'
        },
        {
            'nom_entreprise': 'Toitures Québec Pro',
            'nom_contact': 'Sylvie Boucher',
            'email': 'sylvie@toitures-qc-pro.ca',
            'telephone': '819-555-4004',
            'mot_de_passe': 'demo123',
            'numero_rbq': '4567-8901-01',
            'zones_desservies': 'J9A,J9B,J8A,J8B,J8C',
            'types_projets': 'Toiture,Revêtement extérieur',
            'abonnement': 'premium',
            'credits_restants': 85,
            'certifications': 'RBQ, AMCQ, Assurance 5M$'
        },
        {
            'nom_entreprise': 'Cuisine Design Plus',
            'nom_contact': 'Robert Lavoie',
            'email': 'robert@cuisine-design-plus.ca',
            'telephone': '514-555-5005',
            'mot_de_passe': 'demo123',
            'numero_rbq': '5678-9012-01',
            'zones_desservies': 'H3A,H3B,H3C,H4A,H4B',
            'types_projets': 'Rénovation cuisine,Plancher',
            'abonnement': 'entreprise',
            'credits_restants': 999,
            'certifications': 'RBQ, Designer certifié, APCHQ'
        },
        {
            'nom_entreprise': 'Peinture Artistique Montréal',
            'nom_contact': 'Louise Martin',
            'email': 'louise@peinture-artistique-mtl.ca',
            'telephone': '514-555-6006',
            'mot_de_passe': 'demo123',
            'numero_rbq': '6789-0123-01',
            'zones_desservies': 'H1A,H2A,H3A,H4A,H5A',
            'types_projets': 'Peinture',
            'abonnement': 'gratuit',
            'credits_restants': 3,
            'certifications': 'RBQ, APMQ'
        },
        {
            'nom_entreprise': 'Revêtement Extérieur Durable',
            'nom_contact': 'François Côté',
            'email': 'francois@revetement-durable.ca',
            'telephone': '450-555-7007',
            'mot_de_passe': 'demo123',
            'numero_rbq': '7890-1234-01',
            'zones_desservies': 'J4A,J4B,J4C,J5A,J5B',
            'types_projets': 'Revêtement extérieur,Toiture',
            'abonnement': 'standard',
            'credits_restants': 28,
            'certifications': 'RBQ, APCHQ, Certifié James Hardie'
        },
        {
            'nom_entreprise': 'Planchers Nobles Québec',
            'nom_contact': 'Annie Dubois',
            'email': 'annie@planchers-nobles-qc.ca',
            'telephone': '418-555-8008',
            'mot_de_passe': 'demo123',
            'numero_rbq': '8901-2345-01',
            'zones_desservies': 'G1A,G1B,G1C,G1D,G1E',
            'types_projets': 'Plancher',
            'abonnement': 'standard',
            'credits_restants': 38,
            'certifications': 'RBQ, Installateur certifié bois franc'
        },
        {
            'nom_entreprise': 'Solutions Bâtiment Global',
            'nom_contact': 'Marc Bérubé',
            'email': 'marc@solutions-batiment.ca',
            'telephone': '819-555-9009',
            'mot_de_passe': 'demo123',
            'numero_rbq': '9012-3456-01',
            'zones_desservies': 'J9A,J9B,J9C,J8A,J8B',
            'types_projets': 'Agrandissement,Rénovation cuisine,Rénovation salle de bain,Plancher',
            'abonnement': 'premium',
            'credits_restants': 75,
            'certifications': 'RBQ, APCHQ, Entrepreneur général'
        },
        {
            'nom_entreprise': 'Rénovation Express 24h',
            'nom_contact': 'Caroline Roy',
            'email': 'caroline@renovation-express.ca',
            'telephone': '514-555-1010',
            'mot_de_passe': 'demo123',
            'numero_rbq': '0123-4567-01',
            'zones_desservies': 'H1A,H1B,H1C,H1D,H1E',
            'types_projets': 'Peinture,Plancher,Électricité,Plomberie',
            'abonnement': 'gratuit',
            'credits_restants': 2,
            'certifications': 'RBQ, Service d\'urgence 24h'
        }
    ]
    
    # Insérer les entrepreneurs
    for entr in entrepreneurs_demo:
        cursor.execute('''
            INSERT INTO entrepreneurs (nom_entreprise, nom_contact, email, telephone, 
                                     mot_de_passe_hash, numero_rbq, zones_desservies, 
                                     types_projets, abonnement, credits_restants, 
                                     certifications, date_inscription)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entr['nom_entreprise'], entr['nom_contact'], entr['email'], entr['telephone'],
              hash_password(entr['mot_de_passe']), entr['numero_rbq'], entr['zones_desservies'],
              entr['types_projets'], entr['abonnement'], entr['credits_restants'],
              entr['certifications'], datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 365))))
    
    # Données de démonstration pour leads
    leads_demo = [
        {
            'nom': 'Sophie Lafleur',
            'email': 'sophie.lafleur@email.com',
            'telephone': '514-123-4567',
            'code_postal': 'H1A 2B3',
            'type_projet': 'Rénovation cuisine',
            'description': 'Je souhaite rénover complètement ma cuisine. Elle fait environ 12x10 pieds. Je veux des armoires modernes, un îlot central, et changer tous les électroménagers. Budget flexible pour un travail de qualité.',
            'budget': '30 000$ - 50 000$',
            'delai_realisation': 'Dans 2-3 mois',
            'numero_reference': 'SQ-20240115-ABC12345'
        },
        {
            'nom': 'Michel Bergeron',
            'email': 'michel.bergeron@email.com',
            'telephone': '418-987-6543',
            'code_postal': 'G1A 1A1',
            'type_projet': 'Toiture',
            'description': 'Ma toiture a 20 ans et commence à montrer des signes d\'usure. Quelques bardeaux se détachent et j\'ai eu une petite infiltration l\'hiver dernier. Maison bungalow de 1200 pi2.',
            'budget': 'Plus de 50 000$',
            'delai_realisation': 'Dès que possible',
            'numero_reference': 'SQ-20240116-DEF67890'
        },
        {
            'nom': 'Catherine Morin',
            'email': 'catherine.morin@email.com',
            'telephone': '450-555-7890',
            'code_postal': 'J4A 3B2',
            'type_projet': 'Rénovation salle de bain',
            'description': 'Rénovation complète d\'une salle de bain au sous-sol. Actuellement très désuète, je veux moderniser avec douche italienne, vanité double et plancher chauffant.',
            'budget': '15 000$ - 30 000$',
            'delai_realisation': 'Dans 1 mois',
            'numero_reference': 'SQ-20240117-GHI23456'
        },
        {
            'nom': 'Pierre Caron',
            'email': 'pierre.caron@email.com',
            'telephone': '819-444-1122',
            'code_postal': 'J9A 1B1',
            'type_projet': 'Électricité',
            'description': 'Mise aux normes électriques de ma maison construite en 1975. Plusieurs prises ne fonctionnent plus et le panneau électrique doit être changé. Urgence car inspection nécessaire pour vente.',
            'budget': '5 000$ - 15 000$',
            'delai_realisation': 'Dès que possible',
            'numero_reference': 'SQ-20240118-JKL78901'
        },
        {
            'nom': 'Isabelle Tanguay',
            'email': 'isabelle.tanguay@email.com',
            'telephone': '514-777-8888',
            'code_postal': 'H3A 2C1',
            'type_projet': 'Agrandissement',
            'description': 'Agrandissement de ma maison pour ajouter une chambre et une salle de bain à l\'étage. L\'agrandissement ferait environ 16x12 pieds avec toit cathédrale.',
            'budget': 'Plus de 50 000$',
            'delai_realisation': 'Dans 3-6 mois',
            'numero_reference': 'SQ-20240119-MNO34567'
        },
        {
            'nom': 'Jean-François Dubé',
            'email': 'jf.dube@email.com',
            'telephone': '418-666-5555',
            'code_postal': 'G1B 2A2',
            'type_projet': 'Plancher',
            'description': 'Remplacement du plancher de bois franc dans le salon, cuisine et couloir. Environ 800 pi2 au total. Je préfère du chêne ou de l\'érable, fini satiné.',
            'budget': '15 000$ - 30 000$',
            'delai_realisation': 'Dans 2-3 mois',
            'numero_reference': 'SQ-20240120-PQR89012'
        },
        {
            'nom': 'Martine Pelletier',
            'email': 'martine.pelletier@email.com',
            'telephone': '450-333-4444',
            'code_postal': 'J5A 1C3',
            'type_projet': 'Peinture',
            'description': 'Peinture intérieure complète de ma maison. 3 chambres, salon, cuisine, couloirs et escalier. Préparation des murs nécessaire, quelques trous à boucher.',
            'budget': 'Moins de 5 000$',
            'delai_realisation': 'Dans 1 mois',
            'numero_reference': 'SQ-20240121-STU45678'
        },
        {
            'nom': 'Alain Côté',
            'email': 'alain.cote@email.com',
            'telephone': '819-888-9999',
            'code_postal': 'J8A 2B1',
            'type_projet': 'Revêtement extérieur',
            'description': 'Remplacement du revêtement extérieur en aluminium par de la brique ou de la pierre. Façade avant seulement, environ 400 pi2. Isolation à vérifier.',
            'budget': '30 000$ - 50 000$',
            'delai_realisation': 'Plus de 6 mois',
            'numero_reference': 'SQ-20240122-VWX90123'
        },
        {
            'nom': 'Nathalie Bouchard',
            'email': 'nathalie.bouchard@email.com',
            'telephone': '514-111-2222',
            'code_postal': 'H4A 1B2',
            'type_projet': 'Plomberie',
            'description': 'Problème de basse pression d\'eau dans toute la maison. Possiblement les tuyaux en cuivre qui sont bouchés. Maison de 1960, jamais de rénovation plomberie.',
            'budget': '5 000$ - 15 000$',
            'delai_realisation': 'Dès que possible',
            'numero_reference': 'SQ-20240123-YZA56789'
        },
        {
            'nom': 'François Girard',
            'email': 'francois.girard@email.com',
            'telephone': '418-222-3333',
            'code_postal': 'G1C 3A1',
            'type_projet': 'Rénovation cuisine',
            'description': 'Rénovation partielle de cuisine. Garder les armoires actuelles mais les repeindre, changer le comptoir pour du quartz et changer le dosseret.',
            'budget': '5 000$ - 15 000$',
            'delai_realisation': 'Dans 1 mois',
            'numero_reference': 'SQ-20240124-BCD23456'
        }
    ]
    
    # Générer des leads supplémentaires pour avoir 50 au total
    noms_quebecois = [
        'Gisèle Tremblay', 'Claude Leblanc', 'Diane Gagnon', 'André Boucher', 'Lise Lavoie',
        'Réal Martin', 'Denise Côté', 'Normand Roy', 'Ginette Bergeron', 'Marcel Morin',
        'Francine Caron', 'Yvon Tanguay', 'Monique Dubé', 'Gaston Pelletier', 'Céline Bouchard',
        'Bernard Girard', 'Nicole Simard', 'Paul Fortin', 'Johanne Bélanger', 'Daniel Ouellet',
        'Carole Gauthier', 'Roger Levesque', 'Sylvie Roberge', 'Jean-Claude Nadeau', 'Louise Cloutier',
        'Jacques Masse', 'Hélène Demers', 'Yves Langlois', 'Chantal Desjardins', 'Robert Poulin',
        'Manon Bédard', 'Gilles Paradis', 'Francine Larouche', 'René Thériault', 'Micheline Vaillancourt',
        'Jean-Paul Gosselin', 'Pierrette Champagne', 'Serge Dufresne', 'Ghislaine Turcotte', 'Alain Mercier'
    ]
    
    types_projets = ['Rénovation cuisine', 'Rénovation salle de bain', 'Toiture', 'Revêtement extérieur', 
                    'Plancher', 'Peinture', 'Agrandissement', 'Électricité', 'Plomberie', 
                    'Chauffage/Climatisation', 'Isolation', 'Fenêtres et portes', 'Maçonnerie', 'Charpenterie', 'Autre']
    
    budgets = ['Moins de 5 000$', '5 000$ - 15 000$', '15 000$ - 30 000$', '30 000$ - 50 000$', 'Plus de 50 000$']
    
    delais = ['Dès que possible', 'Dans 1 mois', 'Dans 2-3 mois', 'Dans 3-6 mois', 'Plus de 6 mois']
    
    codes_postaux_qc = [
        # Montréal et région métropolitaine
        'H1A 1A1', 'H2B 2B2', 'H3C 3C3', 'H4D 4D4', 'H5E 5E5', 'H7A 1A1', 'H8B 2B2', 'H9C 3C3',
        # Québec et région
        'G1A 1A1', 'G2B 2B2', 'G3C 3C3', 'G4D 4D4', 'G5E 5E5', 'G6A 1A1', 'G7B 2B2', 'G8C 3C3',
        # Rive-Sud de Montréal (Longueuil, Brossard, etc.)
        'J4A 1A1', 'J5B 2B2', 'J6C 3C3', 'J7D 4D4', 'J8E 5E5',
        # Laval et Laurentides
        'H7A 1A1', 'J7A 1A1', 'J8A 1A1', 'J9A 1A1', 'J0A 1A1',
        # Outaouais (Gatineau)
        'J8X 1A1', 'J9H 1A1', 'J8Y 1A1', 'J9J 1A1',
        # Mauricie (Trois-Rivières)
        'G8Z 1A1', 'G9A 1A1', 'G9B 1A1', 'G9C 1A1',
        # Estrie (Sherbrooke)
        'J1E 1A1', 'J1G 1A1', 'J1H 1A1', 'J1K 1A1',
        # Saguenay
        'G7H 1A1', 'G7G 1A1', 'G7J 1A1', 'G7K 1A1'
    ]
    
    descriptions_templates = [
        "Projet de {type_projet} pour ma résidence. J'aimerais avoir plusieurs soumissions pour comparer les prix et approches.",
        "Besoin de travaux de {type_projet}. Recherche entrepreneur qualifié avec de bonnes références.",
        "Planification de {type_projet}. Ouvert aux suggestions et conseils d'experts.",
        "Urgent: travaux de {type_projet} nécessaires. Disponible pour rencontre rapidement.",
        "Rénovation de {type_projet} prévue. Budget flexible selon la qualité du travail proposé."
    ]
    
    # Insérer les 10 premiers leads avec descriptions détaillées
    for lead in leads_demo:
        days_ago = random.randint(1, 90)
        date_creation = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        
        cursor.execute('''
            INSERT INTO leads (nom, email, telephone, code_postal, type_projet, 
                              description, budget, delai_realisation, numero_reference, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lead['nom'], lead['email'], lead['telephone'], lead['code_postal'], 
              lead['type_projet'], lead['description'], lead['budget'], 
              lead['delai_realisation'], lead['numero_reference'], date_creation))
    
    # Générer 40 leads supplémentaires
    for i in range(40):
        nom = random.choice(noms_quebecois)
        type_projet = random.choice(types_projets)
        description = random.choice(descriptions_templates).format(type_projet=type_projet.lower())
        
        # Générer email basé sur le nom
        email_name = nom.lower().replace(' ', '.').replace('é', 'e').replace('è', 'e').replace('ç', 'c')
        email = f"{email_name}@email.com"
        
        # Générer numéro de téléphone québécois
        area_codes = ['514', '418', '450', '819', '438', '581', '579', '367']
        area_code = random.choice(area_codes)
        phone_number = f"{area_code}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        days_ago = random.randint(1, 90)
        date_creation = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        
        # Générer numéro de référence unique
        ref_number = f"SQ-{date_creation.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        
        cursor.execute('''
            INSERT INTO leads (nom, email, telephone, code_postal, type_projet, 
                              description, budget, delai_realisation, numero_reference, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nom, email, phone_number, random.choice(codes_postaux_qc), 
              type_projet, description, random.choice(budgets), 
              random.choice(delais), ref_number, date_creation))
    
    # Créer des attributions pour simuler l'activité
    cursor.execute('SELECT id FROM leads')
    lead_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT id FROM entrepreneurs')
    entrepreneur_ids = [row[0] for row in cursor.fetchall()]
    
    # Attribuer des leads de façon réaliste
    for lead_id in lead_ids:
        # 70% des leads ont au moins une attribution
        if random.random() < 0.7:
            # Nombre d'attributions par lead (1-5)
            nb_attributions = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 8, 2])[0]
            
            entrepreneurs_choisis = random.sample(entrepreneur_ids, min(nb_attributions, len(entrepreneur_ids)))
            
            for entrepreneur_id in entrepreneurs_choisis:
                # Prix basé sur le type de projet du lead
                cursor.execute('SELECT type_projet, budget FROM leads WHERE id = ?', (lead_id,))
                type_projet, budget = cursor.fetchone()
                
                prix_base = {
                    "Peinture": 45.0, "Plancher": 55.0, "Électricité": 65.0, "Plomberie": 65.0,
                    "Chauffage/Climatisation": 75.0, "Isolation": 60.0, "Fenêtres et portes": 70.0,
                    "Maçonnerie": 80.0, "Charpenterie": 85.0, "Rénovation cuisine": 95.0, 
                    "Rénovation salle de bain": 85.0, "Toiture": 105.0, "Revêtement extérieur": 90.0, 
                    "Agrandissement": 120.0, "Autre": 70.0
                }
                
                multiplicateur_budget = {
                    "Moins de 5 000$": 0.8, "5 000$ - 15 000$": 1.0, "15 000$ - 30 000$": 1.3,
                    "30 000$ - 50 000$": 1.6, "Plus de 50 000$": 2.0
                }
                
                prix = prix_base.get(type_projet, 50.0) * multiplicateur_budget.get(budget, 1.0)
                prix = round(prix + random.uniform(-10, 10), 2)  # Ajouter variation
                
                days_ago = random.randint(1, 60)
                date_attribution = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                
                statuts_possibles = ['attribue', 'contacte', 'soumission_envoyee', 'contrat_signe']
                statut = random.choices(statuts_possibles, weights=[30, 40, 20, 10])[0]
                
                notes_exemples = [
                    "Client très intéressé, visite prévue la semaine prochaine",
                    "Soumission envoyée, en attente de réponse",
                    "Client a choisi un autre entrepreneur",
                    "Projet reporté à l'automne",
                    "Contrat signé, début des travaux prévu",
                    "Client ne répond plus aux appels",
                    "Demande de modifications à la soumission",
                    "Rencontre effectuée, client satisfait de notre approche"
                ]
                
                notes = random.choice(notes_exemples) if random.random() < 0.6 else ""
                
                cursor.execute('''
                    INSERT INTO attributions (lead_id, entrepreneur_id, date_attribution, 
                                            statut, notes, prix_paye)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (lead_id, entrepreneur_id, date_attribution, statut, notes, prix))
    
    conn.commit()
    conn.close()
    
    print("✅ Base de données initialisée avec succès!")
    print("📊 Données créées:")
    print(f"   • 10 entrepreneurs avec comptes demo (mot de passe: demo123)")
    print(f"   • 50 leads de démonstration")
    print(f"   • Attributions réalistes pour simulation d'activité")
    print("\n🔑 Comptes de test:")
    print("   • Admin: mot de passe 'admin123'")
    print("   • Entrepreneurs: email de la liste + mot de passe 'demo123'")

if __name__ == "__main__":
    init_database_with_demo_data()