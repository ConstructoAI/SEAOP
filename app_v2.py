import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import datetime
import os
import uuid
from typing import Optional, List, Dict, Any
import re
from dataclasses import dataclass
from PIL import Image
import io
import base64

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '/opt/render/project/data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

# Configuration de la page
st.set_page_config(
    page_title="SEAOP - Système Électronique d'Appel d'Offres Public",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS personnalisé
def load_css():
    """Charge le fichier CSS personnalisé"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Classes de données
@dataclass
class Lead:
    id: Optional[int] = None
    nom: str = ""
    email: str = ""
    telephone: str = ""
    code_postal: str = ""
    type_projet: str = ""
    description: str = ""
    budget: str = ""
    delai_realisation: str = ""
    photos: Optional[str] = None
    plans: Optional[str] = None
    documents: Optional[str] = None
    date_creation: Optional[datetime.datetime] = None
    statut: str = "nouveau"
    numero_reference: Optional[str] = None
    visible_entrepreneurs: bool = True
    accepte_soumissions: bool = True

@dataclass
class Entrepreneur:
    id: Optional[int] = None
    nom_entreprise: str = ""
    nom_contact: str = ""
    email: str = ""
    telephone: str = ""
    mot_de_passe_hash: str = ""
    numero_rbq: str = ""
    zones_desservies: str = ""
    types_projets: str = ""
    abonnement: str = "gratuit"
    credits_restants: int = 5
    date_inscription: Optional[datetime.datetime] = None
    statut: str = "actif"
    certifications: str = ""
    evaluations_moyenne: float = 0.0
    nombre_evaluations: int = 0

@dataclass
class Soumission:
    id: Optional[int] = None
    lead_id: int = 0
    entrepreneur_id: int = 0
    montant: float = 0.0
    description_travaux: str = ""
    delai_execution: str = ""
    validite_offre: str = ""
    inclusions: str = ""
    exclusions: str = ""
    conditions: str = ""
    documents: Optional[str] = None
    statut: str = "envoyee"
    date_creation: Optional[datetime.datetime] = None
    vue_par_client: bool = False
    notes_client: str = ""
    notes_entrepreneur: str = ""

# Fonctions utilitaires
def init_database():
    """Initialise la base de données SQLite avec toutes les tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table des leads (projets)
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
            plans TEXT,
            documents TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'nouveau',
            numero_reference TEXT UNIQUE,
            visible_entrepreneurs BOOLEAN DEFAULT 1,
            accepte_soumissions BOOLEAN DEFAULT 1
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
            certifications TEXT,
            evaluations_moyenne REAL DEFAULT 0.0,
            nombre_evaluations INTEGER DEFAULT 0
        )
    ''')
    
    # Table des soumissions
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
            documents TEXT,
            statut TEXT DEFAULT 'envoyee',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP,
            vue_par_client BOOLEAN DEFAULT 0,
            notes_client TEXT,
            notes_entrepreneur TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id),
            UNIQUE(lead_id, entrepreneur_id)
        )
    ''')
    
    # Table des messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            entrepreneur_id INTEGER,
            expediteur_type TEXT NOT NULL,
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
    
    # Table des évaluations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soumission_id INTEGER NOT NULL,
            evaluateur_type TEXT NOT NULL,
            note INTEGER NOT NULL CHECK(note >= 1 AND note <= 5),
            commentaire TEXT,
            date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id),
            UNIQUE(soumission_id, evaluateur_type)
        )
    ''')
    
    # Table des attributions (pour compatibilité)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            entrepreneur_id INTEGER,
            date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            statut TEXT DEFAULT 'attribue',
            notes TEXT,
            prix_paye REAL DEFAULT 0.0,
            soumission_id INTEGER,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (entrepreneur_id) REFERENCES entrepreneurs (id),
            FOREIGN KEY (soumission_id) REFERENCES soumissions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def valider_email(email: str) -> bool:
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def valider_telephone(telephone: str) -> bool:
    """Valide le format d'un numéro de téléphone québécois"""
    pattern = r'^(\+1[-.\s]?)?\(?([2-9][0-9]{2})\)?[-.\s]?([2-9][0-9]{2})[-.\s]?([0-9]{4})$'
    return re.match(pattern, telephone.replace(" ", "")) is not None

def valider_code_postal(code_postal: str) -> bool:
    """Valide le format d'un code postal canadien"""
    pattern = r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$'
    return re.match(pattern, code_postal) is not None

def generer_numero_reference() -> str:
    """Génère un numéro de référence unique"""
    return f"SEAOP-{datetime.datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def sauvegarder_lead(lead: Lead) -> str:
    """Sauvegarde un lead dans la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    numero_ref = generer_numero_reference()
    lead.numero_reference = numero_ref
    
    cursor.execute('''
        INSERT INTO leads (nom, email, telephone, code_postal, type_projet, 
                          description, budget, delai_realisation, photos, plans, documents, numero_reference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lead.nom, lead.email, lead.telephone, lead.code_postal, lead.type_projet,
          lead.description, lead.budget, lead.delai_realisation, lead.photos, lead.plans, lead.documents, numero_ref))
    
    conn.commit()
    conn.close()
    
    return numero_ref

def authentifier_entrepreneur(email: str, mot_de_passe: str) -> Optional[Entrepreneur]:
    """Authentifie un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM entrepreneurs WHERE email = ? AND mot_de_passe_hash = ?
    ''', (email, hash_password(mot_de_passe)))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return Entrepreneur(
            id=result[0], nom_entreprise=result[1], nom_contact=result[2],
            email=result[3], telephone=result[4], mot_de_passe_hash=result[5],
            numero_rbq=result[6], zones_desservies=result[7], types_projets=result[8],
            abonnement=result[9], credits_restants=result[10], 
            date_inscription=result[11], statut=result[12], certifications=result[13],
            evaluations_moyenne=result[14] if len(result) > 14 else 0.0,
            nombre_evaluations=result[15] if len(result) > 15 else 0
        )
    return None

def get_projets_disponibles() -> List[Dict]:
    """Récupère tous les projets disponibles pour soumission"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*, 
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions
        FROM leads l
        WHERE l.visible_entrepreneurs = 1 AND l.accepte_soumissions = 1
        ORDER BY l.date_creation DESC
    ''')
    
    projets = []
    for row in cursor.fetchall():
        projets.append({
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'plans': row[10], 'documents': row[11], 'date_creation': row[12],
            'statut': row[13], 'numero_reference': row[14],
            'nb_soumissions': row[17] if len(row) > 17 else 0
        })
    
    conn.close()
    return projets

def sauvegarder_soumission(soumission: Soumission) -> bool:
    """Sauvegarde une soumission d'entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO soumissions (lead_id, entrepreneur_id, montant, description_travaux,
                                   delai_execution, validite_offre, inclusions, exclusions,
                                   conditions, documents, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (soumission.lead_id, soumission.entrepreneur_id, soumission.montant,
              soumission.description_travaux, soumission.delai_execution,
              soumission.validite_offre, soumission.inclusions, soumission.exclusions,
              soumission.conditions, soumission.documents, soumission.statut))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Fonctions de gestion des messages
def envoyer_message(lead_id: int, entrepreneur_id: int, expediteur_type: str, expediteur_id: int, destinataire_id: int, message: str, pieces_jointes: str = None) -> bool:
    """Envoie un message entre client et entrepreneur"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (lead_id, entrepreneur_id, expediteur_type, expediteur_id, destinataire_id, message, pieces_jointes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (lead_id, entrepreneur_id, expediteur_type, expediteur_id, destinataire_id, message, pieces_jointes))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi du message: {e}")
        return False

def get_messages_conversation(lead_id: int, entrepreneur_id: int) -> List[Dict]:
    """Récupère tous les messages d'une conversation entre client et entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, 
               CASE 
                   WHEN m.expediteur_type = 'client' THEN l.nom
                   ELSE e.nom_entreprise
               END as nom_expediteur
        FROM messages m
        LEFT JOIN leads l ON m.lead_id = l.id
        LEFT JOIN entrepreneurs e ON m.entrepreneur_id = e.id
        WHERE m.lead_id = ? AND m.entrepreneur_id = ?
        ORDER BY m.date_envoi ASC
    ''', (lead_id, entrepreneur_id))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'lead_id': row[1],
            'entrepreneur_id': row[2],
            'expediteur_type': row[3],
            'expediteur_id': row[4],
            'destinataire_id': row[5],
            'message': row[6],
            'pieces_jointes': row[7],
            'date_envoi': row[8],
            'lu': row[9],
            'nom_expediteur': row[10]
        })
    
    conn.close()
    return messages

def marquer_messages_lus(lead_id: int, entrepreneur_id: int, destinataire_id: int):
    """Marque tous les messages comme lus pour un destinataire"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE messages SET lu = 1 
        WHERE lead_id = ? AND entrepreneur_id = ? AND destinataire_id = ? AND lu = 0
    ''', (lead_id, entrepreneur_id, destinataire_id))
    
    conn.commit()
    conn.close()

def get_conversations_client(client_id: int) -> List[Dict]:
    """Récupère toutes les conversations d'un client"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT m.lead_id, m.entrepreneur_id, e.nom_entreprise, l.type_projet,
               (SELECT COUNT(*) FROM messages m2 WHERE m2.lead_id = m.lead_id AND m2.entrepreneur_id = m.entrepreneur_id AND m2.destinataire_id = ? AND m2.lu = 0) as non_lus,
               (SELECT MAX(date_envoi) FROM messages m3 WHERE m3.lead_id = m.lead_id AND m3.entrepreneur_id = m.entrepreneur_id) as dernier_message
        FROM messages m
        JOIN entrepreneurs e ON m.entrepreneur_id = e.id
        JOIN leads l ON m.lead_id = l.id
        WHERE l.email = (SELECT email FROM leads WHERE id = ?)
        ORDER BY dernier_message DESC
    ''', (client_id, client_id))
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            'lead_id': row[0],
            'entrepreneur_id': row[1],
            'nom_entreprise': row[2],
            'type_projet': row[3],
            'non_lus': row[4],
            'dernier_message': row[5]
        })
    
    conn.close()
    return conversations

def get_conversations_entrepreneur(entrepreneur_id: int) -> List[Dict]:
    """Récupère toutes les conversations d'un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT m.lead_id, m.entrepreneur_id, l.nom as nom_client, l.type_projet,
               (SELECT COUNT(*) FROM messages m2 WHERE m2.lead_id = m.lead_id AND m2.entrepreneur_id = m.entrepreneur_id AND m2.destinataire_id = ? AND m2.lu = 0) as non_lus,
               (SELECT MAX(date_envoi) FROM messages m3 WHERE m3.lead_id = m.lead_id AND m3.entrepreneur_id = m.entrepreneur_id) as dernier_message
        FROM messages m
        JOIN leads l ON m.lead_id = l.id
        WHERE m.entrepreneur_id = ?
        ORDER BY dernier_message DESC
    ''', (entrepreneur_id, entrepreneur_id))
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            'lead_id': row[0],
            'entrepreneur_id': row[1],
            'nom_client': row[2],
            'type_projet': row[3],
            'non_lus': row[4],
            'dernier_message': row[5]
        })
    
    conn.close()
    return conversations

def get_soumissions_pour_projet(lead_id: int) -> List[Dict]:
    """Récupère toutes les soumissions pour un projet"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, e.nom_entreprise, e.numero_rbq, e.certifications,
               e.evaluations_moyenne, e.nombre_evaluations
        FROM soumissions s
        JOIN entrepreneurs e ON s.entrepreneur_id = e.id
        WHERE s.lead_id = ?
        ORDER BY s.date_creation DESC
    ''', (lead_id,))
    
    soumissions = []
    for row in cursor.fetchall():
        soumissions.append({
            'id': row[0],
            'lead_id': row[1],
            'entrepreneur_id': row[2],
            'montant': row[3],
            'description_travaux': row[4],
            'delai_execution': row[5],
            'validite_offre': row[6],
            'inclusions': row[7],
            'exclusions': row[8],
            'conditions': row[9],
            'documents': row[10],
            'statut': row[11],
            'date_creation': row[12],
            'nom_entreprise': row[16],
            'numero_rbq': row[17],
            'certifications': row[18],
            'evaluations_moyenne': row[19],
            'nombre_evaluations': row[20]
        })
    
    conn.close()
    return soumissions

def get_mes_projets(email: str) -> List[Dict]:
    """Récupère les projets d'un client par email"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*,
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions,
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id AND s.statut = 'acceptee') as nb_acceptees
        FROM leads l
        WHERE l.email = ?
        ORDER BY l.date_creation DESC
    ''', (email,))
    
    projets = []
    for row in cursor.fetchall():
        projets.append({
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'plans': row[10], 'documents': row[11], 'date_creation': row[12],
            'statut': row[13], 'numero_reference': row[14],
            'visible_entrepreneurs': row[15], 'accepte_soumissions': row[16],
            'nb_soumissions': row[17], 'nb_acceptees': row[18]
        })
    
    conn.close()
    return projets

# Interface principale
def main():
    init_database()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ SEAOP</h1>
        <p>Système Électronique d'Appel d'Offres Public</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu de navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Sidebar pour navigation
    with st.sidebar:
        st.markdown("### 🏛️ SEAOP")
        st.markdown("*Système Électronique d'Appel d'Offres Public*")
        st.markdown("---")
        
        st.markdown("**🧭 Navigation principale :**")
        page = st.selectbox(
            "Choisissez une section",
            ["🏠 Accueil", 
             "📝 Publier un appel d'offres", 
             "📋 Mes appels d'offres",
             "🏢 Espace soumissionnaires",
             "⚙️ Administration"],
            index=0,
            help="Sélectionnez la section où vous voulez aller"
        )
        
        # Notifications de messages non lus
        if st.session_state.get('entrepreneur_connecte'):
            entrepreneur = st.session_state.entrepreneur_connecte
            conversations = get_conversations_entrepreneur(entrepreneur.id)
            total_non_lus = sum(conv['non_lus'] for conv in conversations)
            
            if total_non_lus > 0:
                st.markdown(f"**💬 Messages non lus : {total_non_lus}**")
                st.markdown("---")
        
        st.markdown("**💡 Instructions :**")
        st.markdown("1. Sélectionnez une option dans le menu ci-dessus")
        st.markdown("2. La page se chargera automatiquement")
        
        if "accueil" in page.lower():
            st.session_state.page = 'accueil'
        elif "publier" in page.lower() or "nouveau projet" in page.lower():
            st.session_state.page = 'nouveau_projet'
        elif "mes" in page.lower() or "mes projets" in page.lower():
            st.session_state.page = 'mes_projets'
        elif "soumissionnaires" in page.lower() or "entrepreneur" in page.lower():
            st.session_state.page = 'entrepreneur'
        elif "administration" in page.lower():
            st.session_state.page = 'admin'
    
    # Debug retiré - navigation par menu uniquement
    
    # Vérifier si on est en mode chat
    if st.session_state.get('mode_chat', False):
        page_chat()
        return
    
    # Routing des pages
    if st.session_state.page == 'accueil':
        page_accueil()
    elif st.session_state.page == 'nouveau_projet':
        page_nouveau_projet()
    elif st.session_state.page == 'mes_projets':
        page_mes_projets()
    elif st.session_state.page == 'entrepreneur':
        page_espace_entrepreneur()
    elif st.session_state.page == 'admin':
        page_administration()

def page_accueil():
    """Page d'accueil avec présentation du service"""
    
    # Navigation uniquement par le menu
    st.info("ℹ️ Utilisez le menu de navigation dans la barre latérale gauche pour accéder aux différentes sections.")
    st.markdown("---")
    
    # Section héro
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Système d'Appel d'Offres Électronique
        
        **Pour les organismes publics et clients:**
        1. 📝 Publiez vos appels d'offres avec tous les détails et plans
        2. 📊 Recevez des soumissions détaillées d'entrepreneurs qualifiés RBQ
        3. 💬 Communiquez directement avec les soumissionnaires
        4. ✅ Sélectionnez la meilleure offre selon vos critères
        
        **Pour les entrepreneurs et fournisseurs:**
        1. 🔍 Consultez les appels d'offres disponibles
        2. 📋 Soumettez vos propositions conformes aux exigences
        3. 💼 Présentez votre expertise et certifications
        4. 🤝 Obtenez de nouveaux contrats publics
        """)
        
        st.markdown("**Pour commencer :**")
        st.markdown("👉 Utilisez le **menu de navigation** dans la barre latérale gauche")
        st.markdown("👉 Sélectionnez **'📝 Publier un appel d'offres'** dans le menu déroulant")
    
    with col2:
        st.markdown("""
        ### 📊 Statistiques
        """)
        
        # Stats fictives pour la démo
        st.metric("Appels d'offres actifs", "127", "+12 cette semaine")
        st.metric("Fournisseurs qualifiés", "342", "+8 cette semaine")
        st.metric("Soumissions reçues", "1,245", "+89 cette semaine")
        st.metric("Taux de conformité", "96%", "+2%")
    
    # Appels d'offres récents
    st.markdown("---")
    st.markdown("### 🆕 Appels d'offres récents")
    
    projets = get_projets_disponibles()[:5]
    
    if projets:
        for projet in projets:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{projet['type_projet']}** - {projet['code_postal']}")
                    st.caption(f"Budget: {projet['budget']} • Délai: {projet['delai_realisation']}")
                
                with col2:
                    st.caption(f"📋 {projet['nb_soumissions']} soumissions")
                
                with col3:
                    st.caption(f"📅 {projet['date_creation'][:10]}")
                
                st.markdown("---")
    else:
        st.info("Aucun appel d'offres disponible pour le moment")

def page_nouveau_projet():
    """Page pour créer un nouvel appel d'offres"""
    
    st.markdown("## 📝 Publier un nouvel appel d'offres")
    st.markdown("Décrivez votre projet en détail pour recevoir des soumissions conformes aux exigences")
    
    with st.form("formulaire_projet"):
        # Informations personnelles
        st.markdown("### 👤 Vos informations")
        
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Jean Tremblay")
            telephone = st.text_input("Téléphone *", placeholder="514-123-4567")
        
        with col2:
            email = st.text_input("Email *", placeholder="jean.tremblay@email.com")
            code_postal = st.text_input("Code postal *", placeholder="H1A 1A1")
        
        # Détails du projet
        st.markdown("### 🏗️ Détails du projet")
        
        col1, col2 = st.columns(2)
        with col1:
            type_projet = st.selectbox(
                "Type de projet *",
                ["", "Rénovation cuisine", "Rénovation salle de bain", "Toiture", 
                 "Revêtement extérieur", "Plancher", "Peinture", "Agrandissement",
                 "Électricité", "Plomberie", "Chauffage/Climatisation", "Isolation",
                 "Fenêtres et portes", "Maçonnerie", "Charpenterie", "Autre"]
            )
            
            budget = st.selectbox(
                "Budget estimé *",
                ["", "Moins de 5 000$", "5 000$ - 15 000$", "15 000$ - 30 000$", 
                 "30 000$ - 50 000$", "Plus de 50 000$", "À déterminer"]
            )
        
        with col2:
            delai_realisation = st.selectbox(
                "Délai de réalisation souhaité *",
                ["", "Dès que possible", "Dans 1 mois", "Dans 2-3 mois", 
                 "Dans 3-6 mois", "Plus de 6 mois", "Flexible"]
            )
        
        description = st.text_area(
            "Description détaillée du projet *",
            placeholder="""Décrivez votre projet en détail :
- Dimensions et superficie
- Matériaux souhaités
- Contraintes particulières
- Accès au chantier
- Préférences spécifiques
- Etc.""",
            height=200
        )
        
        # Upload de fichiers
        st.markdown("### 📎 Documents et plans")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            photos = st.file_uploader(
                "Photos actuelles",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Photos de l'état actuel"
            )
        
        with col2:
            plans = st.file_uploader(
                "Plans et croquis",
                type=['pdf', 'png', 'jpg', 'jpeg', 'dwg'],
                accept_multiple_files=True,
                help="Plans architecturaux, croquis, dessins"
            )
        
        with col3:
            documents = st.file_uploader(
                "Autres documents",
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx'],
                accept_multiple_files=True,
                help="Devis existants, permis, etc."
            )
        
        # Options
        st.markdown("### ⚙️ Options")
        
        col1, col2 = st.columns(2)
        with col1:
            visible_entrepreneurs = st.checkbox(
                "Rendre mon projet visible aux entrepreneurs",
                value=True,
                help="Les entrepreneurs pourront voir et soumissionner sur votre projet"
            )
        
        with col2:
            accepte_soumissions = st.checkbox(
                "Accepter les soumissions",
                value=True,
                help="Vous pourrez fermer les soumissions une fois satisfait"
            )
        
        # Consentement
        consentement = st.checkbox(
            "J'accepte que mes informations soient partagées avec les entrepreneurs pour recevoir des soumissions. *"
        )
        
        # Soumission
        submitted = st.form_submit_button("🚀 Publier mon projet", type="primary")
        
        if submitted:
            # Validation
            erreurs = []
            
            if not nom.strip():
                erreurs.append("Le nom est requis")
            if not email.strip() or not valider_email(email):
                erreurs.append("Email valide requis")
            if not telephone.strip() or not valider_telephone(telephone):
                erreurs.append("Téléphone valide requis")
            if not code_postal.strip() or not valider_code_postal(code_postal):
                erreurs.append("Code postal valide requis")
            if not type_projet:
                erreurs.append("Type de projet requis")
            if not budget:
                erreurs.append("Budget requis")
            if not delai_realisation:
                erreurs.append("Délai requis")
            if not description.strip() or len(description) < 50:
                erreurs.append("Description détaillée requise (min. 50 caractères)")
            if not consentement:
                erreurs.append("Consentement requis")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"❌ {erreur}")
            else:
                # Traitement des fichiers
                photos_data = None
                if photos:
                    photos_base64 = []
                    for photo in photos[:5]:  # Limiter à 5 photos
                        photo_data = base64.b64encode(photo.read()).decode()
                        photos_base64.append(photo_data)
                    photos_data = ",".join(photos_base64)
                
                plans_data = None
                if plans:
                    plans_base64 = []
                    for plan in plans[:3]:  # Limiter à 3 plans
                        plan_data = base64.b64encode(plan.read()).decode()
                        plans_base64.append(plan_data)
                    plans_data = ",".join(plans_base64)
                
                documents_data = None
                if documents:
                    docs_base64 = []
                    for doc in documents[:3]:  # Limiter à 3 documents
                        doc_data = base64.b64encode(doc.read()).decode()
                        docs_base64.append(doc_data)
                    documents_data = ",".join(docs_base64)
                
                # Création du lead
                lead = Lead(
                    nom=nom,
                    email=email,
                    telephone=telephone,
                    code_postal=code_postal,
                    type_projet=type_projet,
                    description=description,
                    budget=budget,
                    delai_realisation=delai_realisation,
                    photos=photos_data,
                    plans=plans_data,
                    documents=documents_data,
                    visible_entrepreneurs=visible_entrepreneurs,
                    accepte_soumissions=accepte_soumissions
                )
                
                # Sauvegarde
                numero_reference = sauvegarder_lead(lead)
                
                # Message de succès
                st.success(f"""
                ✅ **Votre projet a été publié avec succès!**
                
                **Numéro de référence:** {numero_reference}
                
                📧 Un email de confirmation vous a été envoyé.
                
                📋 Les entrepreneurs peuvent maintenant consulter votre projet et soumettre leurs propositions.
                
                💡 **Prochaines étapes:**
                1. Consultez régulièrement vos soumissions dans "Mes projets"
                2. Communiquez avec les entrepreneurs via la messagerie
                3. Comparez les offres et choisissez la meilleure
                """)
                
                # Stocker l'email en session pour accès rapide
                st.session_state.client_email = email
                
                st.balloons()

def page_mes_projets():
    """Page pour consulter ses projets et soumissions"""
    
    st.markdown("## 📋 Mes projets")
    
    # Demander l'email si pas en session
    if 'client_email' not in st.session_state:
        email = st.text_input("Entrez votre email pour voir vos projets:", placeholder="votre@email.com")
        if st.button("Voir mes projets"):
            if email and valider_email(email):
                st.session_state.client_email = email
                st.rerun()
            else:
                st.error("Email invalide")
        return
    
    email = st.session_state.client_email
    st.caption(f"Connecté en tant que: {email}")
    
    # Récupérer les projets
    projets = get_mes_projets(email)
    
    if not projets:
        st.info("Vous n'avez pas encore de projets. Créez votre premier projet!")
        if st.button("📝 Créer un projet"):
            st.session_state.page = 'nouveau_projet'
            st.rerun()
        return
    
    # Afficher les projets
    for projet in projets:
        with st.expander(f"🏗️ {projet['type_projet']} - {projet['numero_reference']}", expanded=True):
            # Infos du projet
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Détails du projet:**")
                st.write(f"Budget: {projet['budget']}")
                st.write(f"Délai: {projet['delai_realisation']}")
                st.write(f"Code postal: {projet['code_postal']}")
            
            with col2:
                st.markdown("**Statut:**")
                if projet['nb_soumissions'] > 0:
                    st.success(f"📋 {projet['nb_soumissions']} soumission(s) reçue(s)")
                else:
                    st.info("En attente de soumissions")
                
                if projet['nb_acceptees'] > 0:
                    st.success("✅ Soumission acceptée")
            
            with col3:
                st.markdown("**Actions:**")
                if projet['accepte_soumissions']:
                    if st.button(f"🔒 Fermer les soumissions", key=f"fermer_{projet['id']}"):
                        # Fermer les soumissions
                        conn = sqlite3.connect(DATABASE_PATH)
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE leads SET accepte_soumissions = 0 WHERE id = ?
                        ''', (projet['id'],))
                        conn.commit()
                        conn.close()
                        st.success("Soumissions fermées")
                        st.rerun()
                else:
                    st.caption("Soumissions fermées")
            
            # Description
            st.markdown("**Description:**")
            st.text_area("", value=projet['description'], height=100, disabled=True, key=f"desc_{projet['id']}")
            
            # Soumissions reçues
            if projet['nb_soumissions'] > 0:
                st.markdown("---")
                st.markdown("### 📊 Soumissions reçues")
                
                soumissions = get_soumissions_pour_projet(projet['id'])
                
                for i, soum in enumerate(soumissions):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{soum['nom_entreprise']}**")
                            if soum['numero_rbq']:
                                st.caption(f"RBQ: {soum['numero_rbq']}")
                            if soum['evaluations_moyenne'] > 0:
                                stars = "⭐" * int(soum['evaluations_moyenne'])
                                st.caption(f"{stars} ({soum['nombre_evaluations']} avis)")
                        
                        with col2:
                            st.metric("Montant", f"{soum['montant']:,.2f}$")
                        
                        with col3:
                            st.caption(f"Délai: {soum['delai_execution']}")
                            st.caption(f"Validité: {soum['validite_offre']}")
                        
                        # Détails de la soumission
                        with st.expander(f"Voir les détails de la soumission"):
                            st.markdown("**Description des travaux:**")
                            st.text_area("", value=soum['description_travaux'], height=200, disabled=True, key=f"travaux_{soum['id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Inclusions:**")
                                st.text_area("", value=soum['inclusions'] or "Non spécifié", height=100, disabled=True, key=f"incl_{soum['id']}")
                            
                            with col2:
                                st.markdown("**Exclusions:**")
                                st.text_area("", value=soum['exclusions'] or "Non spécifié", height=100, disabled=True, key=f"excl_{soum['id']}")
                            
                            st.markdown("**Conditions:**")
                            st.text_area("", value=soum['conditions'] or "Non spécifié", height=80, disabled=True, key=f"cond_{soum['id']}")
                            
                            # Affichage des pièces jointes de la soumission
                            if soum['documents']:
                                st.markdown("---")
                                st.markdown("### 📎 Documents joints à la soumission")
                                
                                try:
                                    # Format: "filename1:base64data1|filename2:base64data2"
                                    documents_list = soum['documents'].split('|')
                                    
                                    cols = st.columns(min(3, len(documents_list)))
                                    
                                    for i, doc_entry in enumerate(documents_list):
                                        if ':' in doc_entry:
                                            filename, doc_base64 = doc_entry.split(':', 1)
                                            
                                            with cols[i % 3]:
                                                try:
                                                    doc_data = base64.b64decode(doc_base64)
                                                    
                                                    # Déterminer le type MIME basé sur l'extension
                                                    if filename.lower().endswith('.pdf'):
                                                        mime_type = "application/pdf"
                                                    elif filename.lower().endswith(('.doc', '.docx')):
                                                        mime_type = "application/msword"
                                                    elif filename.lower().endswith(('.xls', '.xlsx')):
                                                        mime_type = "application/vnd.ms-excel"
                                                    elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                                        mime_type = "image/png"
                                                    else:
                                                        mime_type = "application/octet-stream"
                                                    
                                                    st.download_button(
                                                        f"📄 {filename}",
                                                        data=doc_data,
                                                        file_name=filename,
                                                        mime=mime_type,
                                                        key=f"download_{soum['id']}_{i}",
                                                        use_container_width=True
                                                    )
                                                except Exception as e:
                                                    st.error(f"Erreur lors du chargement de {filename}")
                                except Exception as e:
                                    st.error("Erreur lors du traitement des documents")
                            
                            # Actions sur la soumission
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if soum['statut'] != 'acceptee':
                                    if st.button("✅ Accepter", key=f"accept_{soum['id']}", type="primary"):
                                        conn = sqlite3.connect(DATABASE_PATH)
                                        cursor = conn.cursor()
                                        cursor.execute('''
                                            UPDATE soumissions SET statut = 'acceptee' WHERE id = ?
                                        ''', (soum['id'],))
                                        conn.commit()
                                        conn.close()
                                        st.success("Soumission acceptée!")
                                        st.rerun()
                                else:
                                    st.success("✅ Soumission acceptée")
                            
                            with col2:
                                if soum['statut'] != 'refusee' and soum['statut'] != 'acceptee':
                                    if st.button("❌ Refuser", key=f"refuse_{soum['id']}"):
                                        conn = sqlite3.connect(DATABASE_PATH)
                                        cursor = conn.cursor()
                                        cursor.execute('''
                                            UPDATE soumissions SET statut = 'refusee' WHERE id = ?
                                        ''', (soum['id'],))
                                        conn.commit()
                                        conn.close()
                                        st.info("Soumission refusée")
                                        st.rerun()
                            
                            with col3:
                                if st.button("💬 Chat", key=f"chat_{soum['id']}", help="Discuter avec l'entrepreneur"):
                                    st.session_state.chat_lead_id = projet['id']
                                    st.session_state.chat_entrepreneur_id = soum['entrepreneur_id']
                                    st.session_state.chat_nom_entrepreneur = soum['nom_entreprise']
                                    st.session_state.chat_type_utilisateur = 'client'
                                    st.session_state.mode_chat = True
                                    st.rerun()
                        
                        st.markdown("---")

def page_chat():
    """Interface de chat entre client et entrepreneur"""
    if 'mode_chat' not in st.session_state or not st.session_state.mode_chat:
        return
    
    # Récupérer les informations du chat
    lead_id = st.session_state.get('chat_lead_id')
    entrepreneur_id = st.session_state.get('chat_entrepreneur_id')
    type_utilisateur = st.session_state.get('chat_type_utilisateur', 'client')
    
    if not lead_id or not entrepreneur_id:
        st.error("Erreur: informations de chat manquantes")
        return
    
    # En-tête du chat
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        if type_utilisateur == 'client':
            nom_correspondant = st.session_state.get('chat_nom_entrepreneur', 'Entrepreneur')
            st.markdown(f"## 💬 Chat avec {nom_correspondant}")
        else:
            nom_correspondant = st.session_state.get('chat_nom_client', 'Client')
            st.markdown(f"## 💬 Chat avec {nom_correspondant}")
    
    with col2:
        if st.button("🔄 Actualiser", key="refresh_chat", help="Actualiser les messages"):
            st.rerun()
    
    with col3:
        if st.button("❌ Fermer", key="fermer_chat"):
            st.session_state.mode_chat = False
            for key in ['chat_lead_id', 'chat_entrepreneur_id', 'chat_nom_entrepreneur', 'chat_nom_client', 'chat_type_utilisateur']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Récupérer les messages de la conversation
    messages = get_messages_conversation(lead_id, entrepreneur_id)
    
    # Marquer les messages comme lus
    if type_utilisateur == 'client':
        # Le client lit les messages de l'entrepreneur
        projet = get_projets_par_email("dummy")[0] if get_projets_par_email("dummy") else None
        if projet:
            marquer_messages_lus(lead_id, entrepreneur_id, projet['id'])
    else:
        # L'entrepreneur lit les messages du client
        marquer_messages_lus(lead_id, entrepreneur_id, entrepreneur_id)
    
    # Affichage des messages
    st.markdown("### 📝 Conversation")
    
    # Container pour les messages avec scroll
    chat_container = st.container()
    with chat_container:
        if not messages:
            st.info("💬 Aucun message pour le moment. Commencez la conversation !")
        else:
            for msg in messages:
                date_msg = msg['date_envoi'][:16] if msg['date_envoi'] else ""
                
                if msg['expediteur_type'] == type_utilisateur:
                    # Message de l'utilisateur actuel (à droite)
                    col1, col2 = st.columns([1, 3])
                    with col2:
                        st.markdown(f"""
                        <div style="background-color: #E3F2FD; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                            <strong>Vous</strong> - {date_msg}<br>
                            {msg['message']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Message du correspondant (à gauche)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: #F5F5F5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                            <strong>{msg['nom_expediteur']}</strong> - {date_msg}<br>
                            {msg['message']}
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulaire d'envoi de message
    st.markdown("### ✍️ Envoyer un message")
    with st.form("nouveau_message", clear_on_submit=True):
        message = st.text_area(
            "Votre message",
            placeholder="Tapez votre message ici...",
            height=100,
            key="message_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.form_submit_button("📤 Envoyer", type="primary"):
                if message.strip():
                    # Déterminer les IDs d'expéditeur et destinataire
                    if type_utilisateur == 'client':
                        # Récupérer l'ID du client à partir du projet
                        conn = sqlite3.connect(DATABASE_PATH)
                        cursor = conn.cursor()
                        cursor.execute('SELECT id FROM leads WHERE id = ?', (lead_id,))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            expediteur_id = result[0]
                            destinataire_id = entrepreneur_id
                            expediteur_type = 'client'
                        else:
                            st.error("Erreur: impossible de récupérer les informations du client")
                            st.stop()
                    else:
                        expediteur_id = entrepreneur_id
                        destinataire_id = lead_id
                        expediteur_type = 'entrepreneur'
                    
                    # Envoyer le message
                    if envoyer_message(lead_id, entrepreneur_id, expediteur_type, expediteur_id, destinataire_id, message):
                        st.success("Message envoyé!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de l'envoi du message")
                else:
                    st.warning("Veuillez saisir un message")

def page_espace_entrepreneur():
    """Espace entrepreneur pour consulter projets et soumettre"""
    
    if 'entrepreneur_connecte' not in st.session_state:
        st.session_state.entrepreneur_connecte = None
    
    if st.session_state.entrepreneur_connecte is None:
        # Page de connexion
        st.markdown("## 👷 Espace Entrepreneur")
        
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            with st.form("connexion_entrepreneur"):
                st.markdown("### Connectez-vous")
                
                email = st.text_input("Email", placeholder="votre@entreprise.ca")
                mot_de_passe = st.text_input("Mot de passe", type="password")
                
                if st.form_submit_button("🔐 Se connecter", type="primary"):
                    if email and mot_de_passe:
                        entrepreneur = authentifier_entrepreneur(email, mot_de_passe)
                        if entrepreneur:
                            st.session_state.entrepreneur_connecte = entrepreneur
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                        else:
                            st.error("❌ Email ou mot de passe incorrect")
                    else:
                        st.error("❌ Veuillez remplir tous les champs")
        
        with tab2:
            with st.form("inscription_entrepreneur"):
                st.markdown("### Créer un compte entrepreneur")
                
                col1, col2 = st.columns(2)
                with col1:
                    nom_entreprise = st.text_input("Nom de l'entreprise *")
                    nom_contact = st.text_input("Nom du contact *")
                    email_inscription = st.text_input("Email *")
                    telephone = st.text_input("Téléphone *")
                
                with col2:
                    mot_de_passe = st.text_input("Mot de passe *", type="password")
                    confirmer_mdp = st.text_input("Confirmer mot de passe *", type="password")
                    numero_rbq = st.text_input("Numéro RBQ", placeholder="XXXX-XXXX-XX")
                
                zones_desservies = st.text_area("Zones desservies (codes postaux)")
                
                types_projets = st.multiselect(
                    "Types de projets *",
                    ["Rénovation cuisine", "Rénovation salle de bain", "Toiture", 
                     "Revêtement extérieur", "Plancher", "Peinture", "Agrandissement",
                     "Électricité", "Plomberie", "Chauffage/Climatisation", "Isolation",
                     "Fenêtres et portes", "Maçonnerie", "Charpenterie", "Autre"]
                )
                
                certifications = st.text_area("Certifications et assurances")
                
                if st.form_submit_button("📝 Créer mon compte", type="primary"):
                    if all([nom_entreprise, nom_contact, email_inscription, telephone, mot_de_passe]):
                        if mot_de_passe == confirmer_mdp:
                            # Créer le compte
                            conn = sqlite3.connect(DATABASE_PATH)
                            cursor = conn.cursor()
                            
                            try:
                                cursor.execute('''
                                    INSERT INTO entrepreneurs (nom_entreprise, nom_contact, email, telephone, 
                                                             mot_de_passe_hash, numero_rbq, zones_desservies, 
                                                             types_projets, certifications)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (nom_entreprise, nom_contact, email_inscription, telephone,
                                      hash_password(mot_de_passe), numero_rbq, zones_desservies,
                                      ",".join(types_projets), certifications))
                                
                                conn.commit()
                                st.success("✅ Compte créé! Vous pouvez maintenant vous connecter.")
                            
                            except sqlite3.IntegrityError:
                                st.error("❌ Un compte avec cet email existe déjà")
                            
                            finally:
                                conn.close()
                        else:
                            st.error("❌ Les mots de passe ne correspondent pas")
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires")
    
    else:
        # Dashboard entrepreneur connecté
        entrepreneur = st.session_state.entrepreneur_connecte
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## 👷 Bienvenue, {entrepreneur.nom_entreprise}")
        with col2:
            if st.button("🚪 Déconnexion"):
                st.session_state.entrepreneur_connecte = None
                st.rerun()
        
        # Onglets
        tab1, tab2, tab3 = st.tabs(["🔍 Projets disponibles", "📋 Mes soumissions", "👤 Mon profil"])
        
        with tab1:
            st.markdown("### 🔍 Projets disponibles pour soumission")
            
            projets = get_projets_disponibles()
            
            if not projets:
                st.info("Aucun projet disponible pour le moment")
            else:
                for projet in projets:
                    with st.expander(f"{projet['type_projet']} - {projet['code_postal']} ({projet['budget']})"):
                        # Détails du projet
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**Description du projet:**")
                            st.text_area("", value=projet['description'], height=150, disabled=True, key=f"proj_desc_{projet['id']}")
                        
                        with col2:
                            st.markdown("**Informations:**")
                            st.write(f"📅 Délai: {projet['delai_realisation']}")
                            st.write(f"💰 Budget: {projet['budget']}")
                            st.write(f"📍 Zone: {projet['code_postal']}")
                            st.write(f"📋 {projet['nb_soumissions']} soumission(s)")
                            st.write(f"📆 Publié: {projet['date_creation'][:10]}")
                        
                        # Affichage des pièces jointes
                        st.markdown("---")
                        st.markdown("### 📎 Documents et plans du projet")
                        
                        col_files1, col_files2, col_files3 = st.columns(3)
                        
                        with col_files1:
                            if projet['photos']:
                                st.markdown("**📸 Photos:**")
                                photos_list = projet['photos'].split(',')
                                for i, photo_base64 in enumerate(photos_list):
                                    try:
                                        photo_data = base64.b64decode(photo_base64)
                                        image = Image.open(io.BytesIO(photo_data))
                                        st.image(image, caption=f"Photo {i+1}", use_container_width=True)
                                    except:
                                        st.error(f"Erreur lors du chargement de la photo {i+1}")
                            else:
                                st.info("Aucune photo disponible")
                        
                        with col_files2:
                            if projet['plans']:
                                st.markdown("**📋 Plans:**")
                                plans_list = projet['plans'].split(',')
                                for i, plan_base64 in enumerate(plans_list):
                                    try:
                                        plan_data = base64.b64decode(plan_base64)
                                        st.download_button(
                                            f"📋 Télécharger Plan {i+1}",
                                            data=plan_data,
                                            file_name=f"plan_{i+1}_{projet['numero_reference']}.pdf",
                                            mime="application/pdf",
                                            key=f"plan_{projet['id']}_{i}"
                                        )
                                    except:
                                        st.error(f"Erreur lors du chargement du plan {i+1}")
                            else:
                                st.info("Aucun plan disponible")
                        
                        with col_files3:
                            if projet['documents']:
                                st.markdown("**📄 Documents:**")
                                documents_list = projet['documents'].split(',')
                                for i, doc_base64 in enumerate(documents_list):
                                    try:
                                        doc_data = base64.b64decode(doc_base64)
                                        st.download_button(
                                            f"📄 Télécharger Doc {i+1}",
                                            data=doc_data,
                                            file_name=f"document_{i+1}_{projet['numero_reference']}.pdf",
                                            mime="application/pdf",
                                            key=f"doc_{projet['id']}_{i}"
                                        )
                                    except:
                                        st.error(f"Erreur lors du chargement du document {i+1}")
                            else:
                                st.info("Aucun document disponible")
                        
                        # Vérifier si déjà soumissionné
                        conn = sqlite3.connect(DATABASE_PATH)
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT id FROM soumissions 
                            WHERE lead_id = ? AND entrepreneur_id = ?
                        ''', (projet['id'], entrepreneur.id))
                        deja_soumis = cursor.fetchone()
                        conn.close()
                        
                        if deja_soumis:
                            st.success("✅ Vous avez déjà soumissionné sur ce projet")
                            
                            # Bouton chat pour communiquer avec le client
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("💬 Chat client", key=f"chat_client_{projet['id']}", help="Discuter avec le client"):
                                    st.session_state.chat_lead_id = projet['id']
                                    st.session_state.chat_entrepreneur_id = entrepreneur.id
                                    st.session_state.chat_nom_client = projet['nom']
                                    st.session_state.chat_type_utilisateur = 'entrepreneur'
                                    st.session_state.mode_chat = True
                                    st.rerun()
                        else:
                            # Formulaire de soumission
                            st.markdown("---")
                            st.markdown("### 📝 Soumettre une proposition")
                            
                            with st.form(f"soumission_{projet['id']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    montant = st.number_input(
                                        "Montant de la soumission ($) *",
                                        min_value=0.0,
                                        step=100.0,
                                        key=f"montant_{projet['id']}"
                                    )
                                    
                                    delai_execution = st.text_input(
                                        "Délai d'exécution *",
                                        placeholder="Ex: 3 semaines",
                                        key=f"delai_{projet['id']}"
                                    )
                                
                                with col2:
                                    validite_offre = st.text_input(
                                        "Validité de l'offre *",
                                        value="30 jours",
                                        key=f"validite_{projet['id']}"
                                    )
                                
                                description_travaux = st.text_area(
                                    "Description détaillée des travaux *",
                                    placeholder="""Décrivez en détail:
- Les étapes des travaux
- Les matériaux utilisés
- La méthodologie
- L'équipe assignée
- Le calendrier détaillé""",
                                    height=200,
                                    key=f"travaux_{projet['id']}"
                                )
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    inclusions = st.text_area(
                                        "Inclusions",
                                        placeholder="Ce qui est inclus dans le prix",
                                        height=100,
                                        key=f"inclusions_{projet['id']}"
                                    )
                                
                                with col2:
                                    exclusions = st.text_area(
                                        "Exclusions",
                                        placeholder="Ce qui n'est pas inclus",
                                        height=100,
                                        key=f"exclusions_{projet['id']}"
                                    )
                                
                                conditions = st.text_area(
                                    "Conditions et modalités de paiement",
                                    placeholder="Ex: 30% à la signature, 40% à mi-parcours, 30% à la fin",
                                    key=f"conditions_{projet['id']}"
                                )
                                
                                # Section pièces jointes pour la soumission
                                st.markdown("---")
                                st.markdown("### 📎 Pièces jointes de votre soumission")
                                st.caption("Ajoutez vos documents : devis détaillé, plans, références, catalogue...")
                                
                                col_doc1, col_doc2 = st.columns(2)
                                
                                with col_doc1:
                                    documents_soumission = st.file_uploader(
                                        "Documents de soumission",
                                        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'],
                                        accept_multiple_files=True,
                                        help="Max 5 fichiers - Formats: PDF, DOC, XLS, Images",
                                        key=f"docs_soumission_{projet['id']}"
                                    )
                                
                                with col_doc2:
                                    if documents_soumission:
                                        st.markdown("**Fichiers sélectionnés:**")
                                        for doc in documents_soumission[:5]:  # Limiter à 5 fichiers
                                            st.write(f"📄 {doc.name}")
                                
                                if st.form_submit_button("📤 Envoyer ma soumission", type="primary"):
                                    if montant > 0 and delai_execution and description_travaux:
                                        # Traitement des fichiers uploadés
                                        documents_data = None
                                        if documents_soumission:
                                            docs_base64 = []
                                            for doc in documents_soumission[:5]:  # Limiter à 5 fichiers
                                                doc_data = base64.b64encode(doc.read()).decode()
                                                docs_base64.append(f"{doc.name}:{doc_data}")
                                            documents_data = "|".join(docs_base64)
                                        
                                        soumission = Soumission(
                                            lead_id=projet['id'],
                                            entrepreneur_id=entrepreneur.id,
                                            montant=montant,
                                            description_travaux=description_travaux,
                                            delai_execution=delai_execution,
                                            validite_offre=validite_offre,
                                            inclusions=inclusions,
                                            exclusions=exclusions,
                                            conditions=conditions,
                                            documents=documents_data
                                        )
                                        
                                        if sauvegarder_soumission(soumission):
                                            st.success("✅ Soumission envoyée avec succès!")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Erreur lors de l'envoi")
                                    else:
                                        st.error("❌ Veuillez remplir tous les champs obligatoires")
        
        with tab2:
            st.markdown("### 📋 Mes soumissions")
            
            # Récupérer les soumissions de l'entrepreneur
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*, l.type_projet, l.budget, l.code_postal, l.nom
                FROM soumissions s
                JOIN leads l ON s.lead_id = l.id
                WHERE s.entrepreneur_id = ?
                ORDER BY s.date_creation DESC
            ''', (entrepreneur.id,))
            
            mes_soumissions = cursor.fetchall()
            conn.close()
            
            if not mes_soumissions:
                st.info("Vous n'avez pas encore envoyé de soumissions")
            else:
                for soum in mes_soumissions:
                    statut_emoji = {
                        'envoyee': '📤',
                        'vue': '👁️',
                        'acceptee': '✅',
                        'refusee': '❌'
                    }
                    
                    with st.expander(f"{statut_emoji.get(soum[11], '📋')} {soum[17]} - {soum[16]} - {soum[3]:,.2f}$"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Client:** {soum[20]}")
                            st.write(f"**Projet:** {soum[17]}")
                            st.write(f"**Zone:** {soum[19]}")
                            st.write(f"**Budget client:** {soum[18]}")
                        
                        with col2:
                            st.write(f"**Ma soumission:** {soum[3]:,.2f}$")
                            st.write(f"**Statut:** {soum[11].capitalize()}")
                            st.write(f"**Date:** {soum[12][:10]}")
                        
                        if soum[11] == 'acceptee':
                            st.success("🎉 Félicitations! Votre soumission a été acceptée!")
                            st.info(f"Contactez le client pour finaliser les détails")
                        elif soum[11] == 'refusee':
                            st.error("Cette soumission n'a pas été retenue")
        
        with tab3:
            st.markdown("### 👤 Mon profil d'entreprise")
            
            with st.form("profil_entrepreneur"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom_entreprise = st.text_input("Nom de l'entreprise", value=entrepreneur.nom_entreprise)
                    nom_contact = st.text_input("Nom du contact", value=entrepreneur.nom_contact)
                    email = st.text_input("Email", value=entrepreneur.email, disabled=True)
                
                with col2:
                    telephone = st.text_input("Téléphone", value=entrepreneur.telephone)
                    numero_rbq = st.text_input("Numéro RBQ", value=entrepreneur.numero_rbq or "")
                
                zones_desservies = st.text_area(
                    "Zones desservies",
                    value=entrepreneur.zones_desservies or ""
                )
                
                certifications = st.text_area(
                    "Certifications et assurances",
                    value=entrepreneur.certifications or ""
                )
                
                if st.form_submit_button("💾 Sauvegarder"):
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE entrepreneurs 
                        SET nom_entreprise=?, nom_contact=?, telephone=?, 
                            numero_rbq=?, zones_desservies=?, certifications=?
                        WHERE id=?
                    ''', (nom_entreprise, nom_contact, telephone, numero_rbq,
                          zones_desservies, certifications, entrepreneur.id))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Profil mis à jour!")

def page_administration():
    """Page d'administration"""
    
    if 'admin_connecte' not in st.session_state:
        st.session_state.admin_connecte = False
    
    if not st.session_state.admin_connecte:
        st.markdown("## ⚙️ Administration")
        
        with st.form("connexion_admin"):
            mot_de_passe_admin = st.text_input("Mot de passe administrateur", type="password")
            
            if st.form_submit_button("🔐 Se connecter"):
                # Récupérer le mot de passe admin depuis les variables d'environnement
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Fallback pour développement local
                
                if mot_de_passe_admin == admin_password:
                    st.session_state.admin_connecte = True
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
    
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## ⚙️ Panel d'administration")
        with col2:
            if st.button("🚪 Déconnexion"):
                st.session_state.admin_connecte = False
                st.rerun()
        
        # Statistiques
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_projets = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entrepreneurs")
        total_entrepreneurs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM soumissions")
        total_soumissions = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(montant) FROM soumissions")
        montant_moyen = cursor.fetchone()[0] or 0
        
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projets", total_projets)
        with col2:
            st.metric("Entrepreneurs", total_entrepreneurs)
        with col3:
            st.metric("Soumissions", total_soumissions)
        with col4:
            st.metric("Montant moyen", f"{montant_moyen:,.0f}$")
        
        # Tableaux de données
        tab1, tab2, tab3 = st.tabs(["📋 Projets", "👷 Entrepreneurs", "📊 Soumissions"])
        
        with tab1:
            conn = sqlite3.connect(DATABASE_PATH)
            df_projets = pd.read_sql_query('''
                SELECT id, numero_reference, nom, type_projet, budget, statut, date_creation
                FROM leads
                ORDER BY date_creation DESC
            ''', conn)
            conn.close()
            
            st.dataframe(df_projets, use_container_width=True)
        
        with tab2:
            conn = sqlite3.connect(DATABASE_PATH)
            df_entrepreneurs = pd.read_sql_query('''
                SELECT id, nom_entreprise, email, numero_rbq, abonnement, date_inscription
                FROM entrepreneurs
                ORDER BY date_inscription DESC
            ''', conn)
            conn.close()
            
            st.dataframe(df_entrepreneurs, use_container_width=True)
        
        with tab3:
            conn = sqlite3.connect(DATABASE_PATH)
            df_soumissions = pd.read_sql_query('''
                SELECT s.id, e.nom_entreprise, l.type_projet, s.montant, s.statut, s.date_creation
                FROM soumissions s
                JOIN entrepreneurs e ON s.entrepreneur_id = e.id
                JOIN leads l ON s.lead_id = l.id
                ORDER BY s.date_creation DESC
            ''', conn)
            conn.close()
            
            st.dataframe(df_soumissions, use_container_width=True)

if __name__ == "__main__":
    main()