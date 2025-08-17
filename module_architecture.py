#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Service d'Architecture pour SEAOP
Gestion des demandes de plans d'architecture pour projets > 6000 pi²
"""

import streamlit as st
import sqlite3
import datetime
import uuid
import os
import base64
from typing import Dict, List, Optional

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

# === FONCTIONS POUR SERVICE D'ARCHITECTURE ===

def creer_demande_architecture(demande_data: Dict) -> str:
    """Crée une nouvelle demande de plans d'architecture"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Générer un numéro de référence unique
        numero_reference = f"SEAOP-ARCH-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculer le prix estimé basé sur la superficie
        superficie = float(demande_data.get('superficie_batiment', 0))
        if superficie < 10000:
            prix_base = 15000
            prix_par_pi2 = 1.50
        elif superficie < 25000:
            prix_base = 25000
            prix_par_pi2 = 1.25
        elif superficie < 50000:
            prix_base = 40000
            prix_par_pi2 = 1.00
        else:
            prix_base = 60000
            prix_par_pi2 = 0.85
        
        prix_estime = prix_base + (superficie * prix_par_pi2)
        
        # Services inclus
        services_inclus = []
        if demande_data.get('inclure_structure'):
            services_inclus.append('structure')
            prix_estime += superficie * 0.25
        if demande_data.get('inclure_mecanique'):
            services_inclus.append('mecanique')
            prix_estime += superficie * 0.20
        if demande_data.get('inclure_electrique'):
            services_inclus.append('electrique')
            prix_estime += superficie * 0.15
        if demande_data.get('inclure_civil'):
            services_inclus.append('civil')
            prix_estime += superficie * 0.10
        
        services_str = ','.join(services_inclus) if services_inclus else ''
        
        cursor.execute('''
            INSERT INTO demandes_architecture (
                nom_client, email_client, telephone_client, adresse_projet,
                ville, code_postal, type_batiment, usage_batiment,
                superficie_terrain, superficie_batiment, nombre_etages,
                nombre_logements, type_construction, style_architectural,
                contraintes_terrain, exigences_speciales, plans_requis,
                services_inclus, besoin_3d, besoin_permis,
                certificat_localisation, photos_terrain, croquis_client,
                budget_construction, budget_architecture, date_debut_souhaite,
                date_livraison_plans, niveau_urgence, prix_service,
                modalite_paiement, numero_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            demande_data['nom_client'],
            demande_data['email_client'],
            demande_data['telephone_client'],
            demande_data['adresse_projet'],
            demande_data['ville'],
            demande_data['code_postal'],
            demande_data['type_batiment'],
            demande_data['usage_batiment'],
            demande_data.get('superficie_terrain'),
            demande_data['superficie_batiment'],
            demande_data.get('nombre_etages', 1),
            demande_data.get('nombre_logements'),
            demande_data['type_construction'],
            demande_data.get('style_architectural', ''),
            demande_data.get('contraintes_terrain', ''),
            demande_data.get('exigences_speciales', ''),
            demande_data['plans_requis'],
            services_str,
            1 if demande_data.get('besoin_3d') else 0,
            1 if demande_data.get('besoin_permis', True) else 0,
            demande_data.get('certificat_localisation', ''),
            demande_data.get('photos_terrain', ''),
            demande_data.get('croquis_client', ''),
            demande_data.get('budget_construction', ''),
            demande_data.get('budget_architecture', ''),
            str(demande_data.get('date_debut_souhaite', '')),
            str(demande_data.get('date_livraison_plans', '')),
            demande_data.get('niveau_urgence', 'normal'),
            prix_estime,
            demande_data.get('modalite_paiement', 'forfait'),
            numero_reference
        ))
        
        demande_id = cursor.lastrowid
        
        # Créer une notification admin
        cursor.execute('''
            INSERT INTO notifications (
                utilisateur_type, utilisateur_id, type_notification,
                titre, message, lien_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'admin', 0, 'nouvelle_demande_architecture',
            '🏛️ Nouvelle demande d\'architecture',
            f'{demande_data["nom_client"]} - {demande_data["type_batiment"]} de {superficie:,.0f} pi²',
            demande_id
        ))
        
        conn.commit()
        return numero_reference
        
    except Exception as e:
        print(f"Erreur lors de la création de la demande d'architecture: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_demandes_architecture_admin() -> List[Dict]:
    """Récupère toutes les demandes d'architecture pour l'admin"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nom_client, email_client, telephone_client, type_batiment,
               usage_batiment, superficie_batiment, nombre_etages, ville,
               budget_construction, prix_service, statut, date_demande,
               numero_reference, niveau_urgence, date_livraison_plans,
               certificat_localisation, photos_terrain, croquis_client,
               plans_preliminaires, plans_finaux, pourcentage_complete
        FROM demandes_architecture
        ORDER BY 
            CASE niveau_urgence 
                WHEN 'critique' THEN 1 
                WHEN 'eleve' THEN 2 
                WHEN 'normal' THEN 3 
                WHEN 'faible' THEN 4 
            END,
            date_demande DESC
    ''')
    
    demandes = []
    for row in cursor.fetchall():
        demandes.append({
            'id': row[0],
            'nom_client': row[1],
            'email_client': row[2],
            'telephone_client': row[3],
            'type_batiment': row[4],
            'usage_batiment': row[5],
            'superficie_batiment': row[6],
            'nombre_etages': row[7],
            'ville': row[8],
            'budget_construction': row[9],
            'prix_service': row[10],
            'statut': row[11],
            'date_demande': row[12],
            'numero_reference': row[13],
            'niveau_urgence': row[14],
            'date_livraison_plans': row[15],
            'certificat_localisation': row[16],
            'photos_terrain': row[17],
            'croquis_client': row[18],
            'plans_preliminaires': row[19],
            'plans_finaux': row[20],
            'pourcentage_complete': row[21]
        })
    
    conn.close()
    return demandes

def get_demandes_architecture_client(email_client: str) -> List[Dict]:
    """Récupère les demandes d'architecture d'un client"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, type_batiment, usage_batiment, superficie_batiment,
               ville, prix_service, statut, date_demande, numero_reference,
               date_livraison_plans, pourcentage_complete, plans_finaux
        FROM demandes_architecture
        WHERE email_client = ?
        ORDER BY date_demande DESC
    ''', (email_client,))
    
    demandes = []
    for row in cursor.fetchall():
        demandes.append({
            'id': row[0],
            'type_batiment': row[1],
            'usage_batiment': row[2],
            'superficie_batiment': row[3],
            'ville': row[4],
            'prix_service': row[5],
            'statut': row[6],
            'date_demande': row[7],
            'numero_reference': row[8],
            'date_livraison_plans': row[9],
            'pourcentage_complete': row[10],
            'plans_finaux': row[11]
        })
    
    conn.close()
    return demandes

def get_demande_architecture_by_id(demande_id: int) -> Optional[Dict]:
    """Récupère une demande d'architecture par son ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM demandes_architecture WHERE id = ?
    ''', (demande_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    # Mapper toutes les colonnes
    columns = [description[0] for description in cursor.description]
    demande = dict(zip(columns, row))
    
    conn.close()
    return demande

def mettre_a_jour_statut_architecture(demande_id: int, nouveau_statut: str, notes: str = None, pourcentage: int = None) -> bool:
    """Met à jour le statut d'une demande d'architecture"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        updates = ['statut = ?']
        params = [nouveau_statut]
        
        # Ajouter les dates selon le statut
        if nouveau_statut == 'en_analyse':
            updates.append('date_analyse = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif nouveau_statut == 'acceptee':
            updates.append('date_acceptation = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif nouveau_statut == 'en_cours':
            updates.append('date_debut_plans = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif nouveau_statut == 'revision':
            updates.append('date_revision = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif nouveau_statut == 'approuvee':
            updates.append('date_approbation = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elif nouveau_statut == 'livree':
            updates.append('date_livraison = ?')
            params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if notes:
            updates.append('notes_internes = ?')
            params.append(notes)
        
        if pourcentage is not None:
            updates.append('pourcentage_complete = ?')
            params.append(pourcentage)
        
        params.append(demande_id)
        
        cursor.execute(f'''
            UPDATE demandes_architecture 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def ajouter_plans_architecture(demande_id: int, plans_preliminaires: str = None, plans_finaux: str = None, devis: str = None) -> bool:
    """Ajoute les plans d'architecture à une demande"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if plans_preliminaires:
            updates.append('plans_preliminaires = ?')
            params.append(plans_preliminaires)
        
        if plans_finaux:
            updates.append('plans_finaux = ?')
            params.append(plans_finaux)
        
        if devis:
            updates.append('devis_architecture = ?')
            params.append(devis)
        
        if updates:
            params.append(demande_id)
            
            cursor.execute(f'''
                UPDATE demandes_architecture 
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout des plans: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def encoder_fichiers_architecture(fichiers_uploades: list) -> str:
    """Encode une liste de fichiers en base64 pour stockage"""
    if not fichiers_uploades:
        return ""
    
    fichiers_encodes = []
    
    for fichier in fichiers_uploades:
        try:
            contenu = fichier.read()
            contenu_b64 = base64.b64encode(contenu).decode('utf-8')
            fichiers_encodes.append(f"{fichier.name}:{contenu_b64}")
        except Exception as e:
            print(f"Erreur lors de l'encodage de {fichier.name}: {e}")
    
    return ','.join(fichiers_encodes)

def get_stats_architecture() -> Dict:
    """Récupère les statistiques du service d'architecture"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Stats générales
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN statut = 'recue' THEN 1 END) as recues,
            COUNT(CASE WHEN statut IN ('en_analyse', 'acceptee', 'en_cours', 'revision') THEN 1 END) as en_cours,
            COUNT(CASE WHEN statut IN ('livree', 'terminee') THEN 1 END) as terminees,
            SUM(CASE WHEN statut IN ('livree', 'terminee') THEN prix_service ELSE 0 END) as ca_total,
            AVG(superficie_batiment) as superficie_moyenne,
            AVG(CASE WHEN statut IN ('livree', 'terminee') THEN prix_service END) as prix_moyen
        FROM demandes_architecture
    ''')
    
    stats = cursor.fetchone()
    
    # Distribution par type de bâtiment
    cursor.execute('''
        SELECT type_batiment, COUNT(*) as nombre
        FROM demandes_architecture
        GROUP BY type_batiment
    ''')
    
    types_batiments = cursor.fetchall()
    
    conn.close()
    
    return {
        'total': stats[0] if stats[0] else 0,
        'recues': stats[1] if stats[1] else 0,
        'en_cours': stats[2] if stats[2] else 0,
        'terminees': stats[3] if stats[3] else 0,
        'ca_total': stats[4] if stats[4] else 0,
        'superficie_moyenne': stats[5] if stats[5] else 0,
        'prix_moyen': stats[6] if stats[6] else 0,
        'types_batiments': types_batiments
    }

# === INTERFACE STREAMLIT POUR SERVICE D'ARCHITECTURE ===

def page_service_architecture():
    """Page du service d'architecture pour projets > 6000 pi²"""
    
    st.markdown("## 🏛️ Service d'Architecture Professionnelle")
    st.markdown("### Plans d'architecte pour projets de grande envergure (> 6,000 pi²)")
    
    # Onglets pour client et consultation
    tab1, tab2, tab3 = st.tabs(["📐 Nouvelle demande", "📋 Mes demandes", "ℹ️ Informations"])
    
    with tab1:
        st.markdown("""
        #### Obtenez des plans d'architecte professionnels
        
        **Service complet incluant :**
        - Plans d'architecture scellés par architecte OAQ
        - Conformité au Code National du Bâtiment
        - Aide pour permis de construction
        - Modélisation 3D (optionnel)
        - Coordination avec ingénieurs (structure, mécanique, électrique)
        """)
        
        # Vérification de la superficie
        st.warning("""
        ⚠️ **Important** : Ce service est **obligatoire** pour les projets de plus de 6,000 pi² 
        selon la réglementation québécoise. Un architecte membre de l'OAQ doit signer les plans.
        """)
        
        with st.form("formulaire_architecture"):
            # Section 1: Informations client
            st.markdown("### 1️⃣ Vos informations")
            col1, col2 = st.columns(2)
            
            with col1:
                nom_client = st.text_input("Nom complet ou entreprise *", placeholder="Corporation ABC Inc.")
                telephone = st.text_input("Téléphone *", placeholder="514-555-1234")
                ville = st.text_input("Ville du projet *", placeholder="Montréal")
            
            with col2:
                email = st.text_input("Email *", placeholder="contact@entreprise.com")
                adresse_projet = st.text_input("Adresse du projet *", placeholder="1234 Rue Principale")
                code_postal = st.text_input("Code postal *", placeholder="H1A 1A1")
            
            # Section 2: Détails du projet
            st.markdown("### 2️⃣ Détails du projet architectural")
            
            col1, col2 = st.columns(2)
            
            with col1:
                type_batiment = st.selectbox(
                    "Type de bâtiment *",
                    ["", "résidentiel", "commercial", "industriel", "institutionnel", "mixte"]
                )
                
                superficie_batiment = st.number_input(
                    "Superficie totale du bâtiment (pi²) *",
                    min_value=6000,
                    value=6000,
                    step=100,
                    help="Minimum 6,000 pi² pour ce service"
                )
                
                nombre_etages = st.number_input(
                    "Nombre d'étages",
                    min_value=1,
                    max_value=50,
                    value=1
                )
                
                if type_batiment == "résidentiel":
                    nombre_logements = st.number_input(
                        "Nombre de logements",
                        min_value=1,
                        value=1
                    )
                else:
                    nombre_logements = None
            
            with col2:
                type_construction = st.selectbox(
                    "Type de construction *",
                    ["", "nouvelle", "agrandissement", "renovation_majeure"]
                )
                
                superficie_terrain = st.number_input(
                    "Superficie du terrain (pi²)",
                    min_value=0,
                    value=0,
                    step=100,
                    help="Laissez 0 si non applicable"
                )
                
                style_architectural = st.selectbox(
                    "Style architectural souhaité",
                    ["", "moderne", "contemporain", "traditionnel", "industriel", "minimaliste", "autre"]
                )
            
            usage_batiment = st.text_area(
                "Usage prévu du bâtiment *",
                placeholder="Ex: Immeuble de 24 condos avec stationnement souterrain et espaces commerciaux au RDC",
                height=100
            )
            
            # Section 3: Spécifications techniques
            st.markdown("### 3️⃣ Spécifications et contraintes")
            
            contraintes_terrain = st.text_area(
                "Contraintes du terrain",
                placeholder="Ex: Terrain en pente, servitudes, zone inondable, proximité d'un cours d'eau...",
                height=80
            )
            
            exigences_speciales = st.text_area(
                "Exigences spéciales",
                placeholder="Ex: Certification LEED, accessibilité universelle, insonorisation supérieure...",
                height=80
            )
            
            # Section 4: Services requis
            st.markdown("### 4️⃣ Services requis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                plans_requis = st.selectbox(
                    "Type de plans requis *",
                    ["", "preliminaire", "concept", "execution", "complet"],
                    help="Préliminaire: esquisse, Concept: 30%, Exécution: 100%, Complet: tous les plans"
                )
                
                besoin_3d = st.checkbox("Modélisation 3D requise", value=False)
                besoin_permis = st.checkbox("Aide pour permis de construction", value=True)
            
            with col2:
                st.markdown("**Services d'ingénierie additionnels:**")
                inclure_structure = st.checkbox("Structure", help="+0.25$/pi²")
                inclure_mecanique = st.checkbox("Mécanique (CVAC, plomberie)", help="+0.20$/pi²")
                inclure_electrique = st.checkbox("Électrique", help="+0.15$/pi²")
                inclure_civil = st.checkbox("Civil (drainage, égouts)", help="+0.10$/pi²")
            
            # Section 5: Budget et délais
            st.markdown("### 5️⃣ Budget et échéancier")
            
            col1, col2 = st.columns(2)
            
            with col1:
                budget_construction = st.selectbox(
                    "Budget de construction estimé",
                    ["", "Moins de 1M$", "1M$ - 5M$", "5M$ - 10M$", 
                     "10M$ - 25M$", "25M$ - 50M$", "Plus de 50M$"]
                )
                
                date_debut_souhaite = st.date_input(
                    "Date de début de construction souhaitée",
                    min_value=datetime.date.today() + datetime.timedelta(days=60),
                    value=datetime.date.today() + datetime.timedelta(days=120)
                )
            
            with col2:
                budget_architecture = st.selectbox(
                    "Budget pour services d'architecture",
                    ["", "À déterminer", "50k$ - 100k$", "100k$ - 250k$", 
                     "250k$ - 500k$", "500k$ - 1M$", "Plus de 1M$"]
                )
                
                date_livraison_plans = st.date_input(
                    "Date de livraison des plans souhaitée",
                    min_value=datetime.date.today() + datetime.timedelta(days=30),
                    value=datetime.date.today() + datetime.timedelta(days=60)
                )
            
            niveau_urgence = st.selectbox(
                "Niveau d'urgence",
                ["normal", "faible", "eleve", "critique"],
                format_func=lambda x: {
                    'faible': '🟢 Faible - Délai flexible',
                    'normal': '🟡 Normal - Délai standard',
                    'eleve': '🟠 Élevé - Prioritaire',
                    'critique': '🔴 Critique - Très urgent'
                }[x]
            )
            
            # Section 6: Documents
            st.markdown("### 6️⃣ Documents à fournir")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                certificat = st.file_uploader(
                    "Certificat de localisation",
                    type=['pdf', 'jpg', 'png'],
                    help="Document du terrain existant"
                )
            
            with col2:
                photos = st.file_uploader(
                    "Photos du terrain/bâtiment",
                    type=['jpg', 'png', 'jpeg'],
                    accept_multiple_files=True,
                    help="Photos actuelles du site"
                )
            
            with col3:
                croquis = st.file_uploader(
                    "Croquis ou esquisses",
                    type=['pdf', 'jpg', 'png', 'dwg'],
                    accept_multiple_files=True,
                    help="Vos idées préliminaires"
                )
            
            # Estimation du prix
            st.markdown("### 💰 Estimation du coût")
            
            if superficie_batiment > 0:
                # Calcul estimé
                if superficie_batiment < 10000:
                    prix_base = 15000
                    prix_pi2 = 1.50
                elif superficie_batiment < 25000:
                    prix_base = 25000
                    prix_pi2 = 1.25
                elif superficie_batiment < 50000:
                    prix_base = 40000
                    prix_pi2 = 1.00
                else:
                    prix_base = 60000
                    prix_pi2 = 0.85
                
                prix_estime = prix_base + (superficie_batiment * prix_pi2)
                
                # Ajouts pour services
                if inclure_structure:
                    prix_estime += superficie_batiment * 0.25
                if inclure_mecanique:
                    prix_estime += superficie_batiment * 0.20
                if inclure_electrique:
                    prix_estime += superficie_batiment * 0.15
                if inclure_civil:
                    prix_estime += superficie_batiment * 0.10
                
                st.info(f"""
                **Estimation préliminaire : {prix_estime:,.2f}$**
                
                Cette estimation inclut:
                - Plans d'architecture de base : {prix_base:,.2f}$
                - Superficie ({superficie_batiment:,.0f} pi² × {prix_pi2}$/pi²) : {(superficie_batiment * prix_pi2):,.2f}$
                {f"- Services de structure : {(superficie_batiment * 0.25):,.2f}$" if inclure_structure else ""}
                {f"- Services mécaniques : {(superficie_batiment * 0.20):,.2f}$" if inclure_mecanique else ""}
                {f"- Services électriques : {(superficie_batiment * 0.15):,.2f}$" if inclure_electrique else ""}
                {f"- Services civils : {(superficie_batiment * 0.10):,.2f}$" if inclure_civil else ""}
                
                *Prix final sujet à analyse détaillée du projet*
                """)
            
            # Bouton de soumission
            submitted = st.form_submit_button("📤 Soumettre la demande", type="primary")
            
            if submitted:
                # Validation
                if not all([nom_client, email, telephone, adresse_projet, ville, code_postal,
                           type_batiment, type_construction, usage_batiment, plans_requis]):
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                elif superficie_batiment < 6000:
                    st.error("❌ La superficie doit être d'au moins 6,000 pi²")
                else:
                    # Préparer les données
                    demande_data = {
                        'nom_client': nom_client,
                        'email_client': email,
                        'telephone_client': telephone,
                        'adresse_projet': adresse_projet,
                        'ville': ville,
                        'code_postal': code_postal,
                        'type_batiment': type_batiment,
                        'usage_batiment': usage_batiment,
                        'superficie_terrain': superficie_terrain if superficie_terrain > 0 else None,
                        'superficie_batiment': superficie_batiment,
                        'nombre_etages': nombre_etages,
                        'nombre_logements': nombre_logements,
                        'type_construction': type_construction,
                        'style_architectural': style_architectural,
                        'contraintes_terrain': contraintes_terrain,
                        'exigences_speciales': exigences_speciales,
                        'plans_requis': plans_requis,
                        'inclure_structure': inclure_structure,
                        'inclure_mecanique': inclure_mecanique,
                        'inclure_electrique': inclure_electrique,
                        'inclure_civil': inclure_civil,
                        'besoin_3d': besoin_3d,
                        'besoin_permis': besoin_permis,
                        'budget_construction': budget_construction,
                        'budget_architecture': budget_architecture,
                        'date_debut_souhaite': date_debut_souhaite,
                        'date_livraison_plans': date_livraison_plans,
                        'niveau_urgence': niveau_urgence,
                        'modalite_paiement': 'forfait'
                    }
                    
                    # Encoder les fichiers
                    if certificat:
                        demande_data['certificat_localisation'] = encoder_fichiers_architecture([certificat])
                    if photos:
                        demande_data['photos_terrain'] = encoder_fichiers_architecture(photos)
                    if croquis:
                        demande_data['croquis_client'] = encoder_fichiers_architecture(croquis)
                    
                    # Créer la demande
                    numero_ref = creer_demande_architecture(demande_data)
                    
                    if numero_ref:
                        st.success(f"""
                        ✅ **Demande créée avec succès!**
                        
                        **Numéro de référence : {numero_ref}**
                        
                        Vous recevrez une réponse dans les 48 heures ouvrables.
                        
                        **Prochaines étapes:**
                        1. Analyse de votre demande par notre équipe
                        2. Contact d'un architecte OAQ pour validation
                        3. Proposition détaillée avec échéancier
                        4. Début des plans après acceptation
                        """)
                        
                        st.balloons()
                    else:
                        st.error("❌ Erreur lors de la création de la demande. Veuillez réessayer.")
    
    with tab2:
        st.markdown("### 📋 Suivi de vos demandes d'architecture")
        
        email_consultation = st.text_input(
            "Entrez votre email pour consulter vos demandes",
            placeholder="contact@entreprise.com"
        )
        
        if st.button("🔍 Rechercher mes demandes"):
            if email_consultation:
                demandes = get_demandes_architecture_client(email_consultation)
                
                if demandes:
                    st.success(f"✅ {len(demandes)} demande(s) trouvée(s)")
                    
                    for demande in demandes:
                        with st.expander(f"📐 {demande['numero_reference']} - {demande['type_batiment'].title()}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"**Type:** {demande['type_batiment'].title()}")
                                st.markdown(f"**Superficie:** {demande['superficie_batiment']:,.0f} pi²")
                                st.markdown(f"**Ville:** {demande['ville']}")
                            
                            with col2:
                                statut_emoji = {
                                    'recue': '📨', 'en_analyse': '🔍', 'acceptee': '✅',
                                    'en_cours': '📐', 'revision': '📝', 'approuvee': '👍',
                                    'livree': '📦', 'terminee': '✔️'
                                }.get(demande['statut'], '📋')
                                
                                st.markdown(f"**Statut:** {statut_emoji} {demande['statut'].replace('_', ' ').title()}")
                                st.markdown(f"**Prix:** {demande['prix_service']:,.2f}$")
                                if demande['pourcentage_complete']:
                                    st.progress(demande['pourcentage_complete'] / 100)
                                    st.caption(f"Progression: {demande['pourcentage_complete']}%")
                            
                            with col3:
                                st.markdown(f"**Date demande:** {demande['date_demande'][:10] if demande['date_demande'] else 'N/A'}")
                                st.markdown(f"**Livraison prévue:** {demande['date_livraison_plans'] if demande['date_livraison_plans'] else 'À déterminer'}")
                            
                            st.markdown("---")
                            st.markdown(f"**Usage:** {demande['usage_batiment']}")
                            
                            # Téléchargement des plans si disponibles
                            if demande['plans_finaux']:
                                st.markdown("### 📥 Documents disponibles")
                                st.download_button(
                                    "⬇️ Télécharger les plans finaux",
                                    data=demande['plans_finaux'],
                                    file_name=f"Plans_{demande['numero_reference']}.pdf",
                                    mime="application/pdf"
                                )
                else:
                    st.info("❌ Aucune demande trouvée pour cet email")
            else:
                st.warning("⚠️ Veuillez entrer votre email")
    
    with tab3:
        st.markdown("""
        ### ℹ️ Informations sur le service d'architecture
        
        #### 📏 Quand un architecte est-il obligatoire au Québec?
        
        Selon la Loi sur les architectes du Québec, un architecte membre de l'OAQ est **obligatoire** pour:
        
        - **Bâtiments publics** : Toute superficie
        - **Édifices à bureaux** : Plus de 300 m² (3,230 pi²) par étage
        - **Commerces** : Plus de 300 m² (3,230 pi²) par étage
        - **Industries** : Plus de 300 m² (3,230 pi²) par étage
        - **Habitations** : 5 logements et plus OU plus de 600 m² (6,460 pi²) total
        
        #### 💰 Structure de prix typique
        
        | Superficie | Prix de base | Prix/pi² | Services inclus |
        |------------|--------------|----------|-----------------|
        | 6,000 - 10,000 pi² | 15,000$ | 1.50$ | Plans de base |
        | 10,000 - 25,000 pi² | 25,000$ | 1.25$ | Plans détaillés |
        | 25,000 - 50,000 pi² | 40,000$ | 1.00$ | Coordination complète |
        | 50,000 pi² et + | 60,000$ | 0.85$ | Gestion de projet |
        
        **Services additionnels:**
        - Structure : +0.25$/pi²
        - Mécanique : +0.20$/pi²
        - Électrique : +0.15$/pi²
        - Civil : +0.10$/pi²
        
        #### 📋 Documents livrables
        
        **Plans préliminaires (30%):**
        - Plan d'implantation
        - Plans d'étage
        - Élévations
        - Coupes principales
        
        **Plans d'exécution (100%):**
        - Plans architecturaux complets
        - Détails de construction
        - Devis descriptif
        - Bordereau des finis
        - Plans pour permis
        
        #### ⏱️ Délais typiques
        
        - **Analyse initiale** : 2-3 jours ouvrables
        - **Plans préliminaires** : 2-3 semaines
        - **Plans d'exécution** : 4-8 semaines
        - **Révisions** : 1-2 semaines
        - **Approbation finale** : 3-5 jours
        
        #### 📞 Support
        
        Pour toute question sur le service d'architecture:
        - 📧 architecture@seaop.ca
        - 📞 1-800-SEAOP-QC
        - 💬 Chat en direct disponible
        """)
        
        # Statistiques du service
        st.markdown("---")
        st.markdown("### 📊 Statistiques du service")
        
        stats = get_stats_architecture()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projets totaux", stats['total'])
        
        with col2:
            st.metric("En cours", stats['en_cours'])
        
        with col3:
            st.metric("Superficie moyenne", f"{stats['superficie_moyenne']:,.0f} pi²" if stats['superficie_moyenne'] else "N/A")
        
        with col4:
            st.metric("Prix moyen", f"{stats['prix_moyen']:,.2f}$" if stats['prix_moyen'] else "N/A")