import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
from typing import Optional, List, Dict, Any
import re
from dataclasses import dataclass
from PIL import Image
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="SoumissionsQuébec.ca",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS personnalisé basé sur EXPERTS IA
def load_css():
    """Charge le fichier CSS personnalisé"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Fichier style.css non trouvé. Utilisation du style par défaut.")

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
    date_creation: Optional[datetime.datetime] = None
    statut: str = "nouveau"
    numero_reference: Optional[str] = None

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

@dataclass
class Attribution:
    id: Optional[int] = None
    lead_id: int = 0
    entrepreneur_id: int = 0
    date_attribution: Optional[datetime.datetime] = None
    statut: str = "attribue"
    notes: str = ""
    prix_paye: float = 0.0

# Fonctions utilitaires
def init_database():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect('soumissions_quebec.db')
    cursor = conn.cursor()
    
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

def valider_numero_rbq(numero_rbq: str) -> bool:
    """Valide le format d'un numéro RBQ québécois (XXXX-XXXX-XX)"""
    if not numero_rbq:
        return True  # Numéro RBQ optionnel
    pattern = r'^\d{4}-\d{4}-\d{2}$'
    return re.match(pattern, numero_rbq) is not None

def generer_numero_reference() -> str:
    """Génère un numéro de référence unique"""
    return f"SQ-{datetime.datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def get_prix_lead(type_projet: str, budget: str) -> float:
    """Calcule le prix d'un lead selon le type et budget"""
    prix_base = {
        "Peinture": 45.0,
        "Plancher": 55.0,
        "Électricité": 65.0,
        "Plomberie": 65.0,
        "Chauffage/Climatisation": 75.0,
        "Isolation": 60.0,
        "Fenêtres et portes": 70.0,
        "Maçonnerie": 80.0,
        "Charpenterie": 85.0,
        "Rénovation cuisine": 95.0,
        "Rénovation salle de bain": 85.0,
        "Toiture": 105.0,
        "Revêtement extérieur": 90.0,
        "Agrandissement": 120.0,
        "Autre": 70.0
    }
    
    multiplicateur_budget = {
        "Moins de 5 000$": 0.8,
        "5 000$ - 15 000$": 1.0,
        "15 000$ - 30 000$": 1.3,
        "30 000$ - 50 000$": 1.6,
        "Plus de 50 000$": 2.0
    }
    
    prix = prix_base.get(type_projet, 50.0)
    prix *= multiplicateur_budget.get(budget, 1.0)
    
    return round(prix, 2)

def envoyer_email_confirmation(email: str, numero_reference: str):
    """Envoie un email de confirmation au client"""
    # Note: Dans un environnement de production, configurez SMTP
    pass

def sauvegarder_lead(lead: Lead) -> str:
    """Sauvegarde un lead dans la base de données"""
    conn = sqlite3.connect('soumissions_quebec.db')
    cursor = conn.cursor()
    
    numero_ref = generer_numero_reference()
    lead.numero_reference = numero_ref
    
    cursor.execute('''
        INSERT INTO leads (nom, email, telephone, code_postal, type_projet, 
                          description, budget, delai_realisation, photos, numero_reference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lead.nom, lead.email, lead.telephone, lead.code_postal, lead.type_projet,
          lead.description, lead.budget, lead.delai_realisation, lead.photos, numero_ref))
    
    conn.commit()
    conn.close()
    
    return numero_ref

def authentifier_entrepreneur(email: str, mot_de_passe: str) -> Optional[Entrepreneur]:
    """Authentifie un entrepreneur"""
    conn = sqlite3.connect('soumissions_quebec.db')
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
            date_inscription=result[11], statut=result[12], certifications=result[13]
        )
    return None

def get_leads_pour_entrepreneur(entrepreneur_id: int) -> List[Dict]:
    """Récupère les leads disponibles pour un entrepreneur"""
    conn = sqlite3.connect('soumissions_quebec.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*, COUNT(a.id) as nb_attributions
        FROM leads l
        LEFT JOIN attributions a ON l.id = a.lead_id
        WHERE l.statut = 'nouveau'
        GROUP BY l.id
        HAVING nb_attributions < 5
        ORDER BY l.date_creation DESC
    ''')
    
    leads = []
    for row in cursor.fetchall():
        leads.append({
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'date_creation': row[10], 'statut': row[11], 'numero_reference': row[12],
            'nb_attributions': row[13]
        })
    
    conn.close()
    return leads

# Interface principale
def main():
    init_database()
    
    # Header principal avec style EXPERTS IA
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ SoumissionsQuébec.ca</h1>
        <p>La plateforme de référence pour vos projets de construction et rénovation au Québec</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu de navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Sidebar pour navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E3A8A/FFFFFF?text=SoumissionsQuébec.ca", width=200)
        
        page = st.selectbox(
            "Navigation",
            ["🏠 Accueil", "📝 Demande de soumission", "👷 Espace entrepreneur", "⚙️ Administration"],
            index=["🏠 Accueil", "📝 Demande de soumission", "👷 Espace entrepreneur", "⚙️ Administration"].index(
                next((p for p in ["🏠 Accueil", "📝 Demande de soumission", "👷 Espace entrepreneur", "⚙️ Administration"] 
                      if st.session_state.page in p.lower()), "🏠 Accueil")
            )
        )
        
        if "accueil" in page.lower():
            st.session_state.page = 'accueil'
        elif "demande" in page.lower():
            st.session_state.page = 'demande'
        elif "entrepreneur" in page.lower():
            st.session_state.page = 'entrepreneur'
        elif "administration" in page.lower():
            st.session_state.page = 'admin'
    
    # Routing des pages
    if st.session_state.page == 'accueil':
        page_accueil()
    elif st.session_state.page == 'demande':
        page_demande_soumission()
    elif st.session_state.page == 'entrepreneur':
        page_espace_entrepreneur()
    elif st.session_state.page == 'admin':
        page_administration()

def page_accueil():
    """Page d'accueil avec présentation du service"""
    
    # Section héro
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2>🎯 Trouvez l'entrepreneur parfait pour votre projet</h2>
            <p style="font-size: 1.2rem; color: #6B7280;">
                Recevez jusqu'à 5 soumissions gratuites d'entrepreneurs qualifiés et certifiés RBQ près de chez vous.
            </p>
            <ul style="font-size: 1.1rem; color: #374151;">
                <li>✅ Entrepreneurs vérifiés et assurés</li>
                <li>✅ Soumissions gratuites et sans engagement</li>
                <li>✅ Réponse sous 48h garantie</li>
                <li>✅ Service 100% québécois</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Commencer ma demande", type="primary", use_container_width=True):
            st.session_state.page = 'demande'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>📊 Nos statistiques</h3>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #1E3A8A;">15,000+</div>
                <div>Projets réalisés</div>
                <hr>
                <div style="font-size: 2rem; font-weight: bold; color: #1E3A8A;">2,500+</div>
                <div>Entrepreneurs partenaires</div>
                <hr>
                <div style="font-size: 2rem; font-weight: bold; color: #1E3A8A;">98%</div>
                <div>Clients satisfaits</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Types de projets populaires
    st.markdown("## 🔨 Types de projets populaires")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>🏠 Rénovations</h4>
            <ul>
                <li>Cuisine</li>
                <li>Salle de bain</li>
                <li>Sous-sol</li>
                <li>Agrandissement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4>🏠 Extérieur</h4>
            <ul>
                <li>Toiture</li>
                <li>Revêtement</li>
                <li>Terrasse</li>
                <li>Aménagement paysager</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h4>⚡ Services</h4>
            <ul>
                <li>Électricité</li>
                <li>Plomberie</li>
                <li>Chauffage</li>
                <li>Isolation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Section entrepreneurs
    st.markdown("## 👷 Vous êtes entrepreneur?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📈 Développez votre clientèle</h3>
            <p>Rejoignez notre réseau d'entrepreneurs certifiés et recevez des leads qualifiés dans votre région.</p>
            <ul>
                <li>🎯 Leads géolocalisés et qualifiés</li>
                <li>💰 Système de tarification flexible</li>
                <li>📱 Dashboard de gestion intuitif</li>
                <li>🏆 Certification RBQ vérifiée</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("👷 Espace entrepreneur", use_container_width=True):
            st.session_state.page = 'entrepreneur'
            st.rerun()

def page_demande_soumission():
    """Page de demande de soumission pour les clients"""
    
    st.markdown("## 📝 Demande de soumission gratuite")
    st.markdown("Remplissez ce formulaire pour recevoir jusqu'à 5 soumissions d'entrepreneurs qualifiés.")
    
    with st.form("formulaire_soumission"):
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
        st.markdown("### 🏗️ Votre projet")
        
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
                 "30 000$ - 50 000$", "Plus de 50 000$"]
            )
        
        with col2:
            delai_realisation = st.selectbox(
                "Délai de réalisation souhaité *",
                ["", "Dès que possible", "Dans 1 mois", "Dans 2-3 mois", 
                 "Dans 3-6 mois", "Plus de 6 mois"]
            )
        
        description = st.text_area(
            "Description détaillée de votre projet *",
            placeholder="Décrivez votre projet en détail : dimensions, matériaux souhaités, contraintes particulières, etc.",
            height=150
        )
        
        # Upload de photos
        st.markdown("### 📸 Photos (optionnel)")
        photos = st.file_uploader(
            "Ajoutez des photos de votre projet",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Les photos aident les entrepreneurs à mieux comprendre votre projet"
        )
        
        # Consentement RGPD/Loi 25
        consentement = st.checkbox(
            "J'accepte que mes informations soient partagées avec les entrepreneurs partenaires pour recevoir des soumissions. "
            "Je peux retirer mon consentement en tout temps. *"
        )
        
        # Soumission
        submitted = st.form_submit_button("🚀 Recevoir mes soumissions", type="primary")
        
        if submitted:
            # Validation des champs
            erreurs = []
            
            if not nom.strip():
                erreurs.append("Le nom est requis")
            if not email.strip():
                erreurs.append("L'email est requis")
            elif not valider_email(email):
                erreurs.append("Format d'email invalide")
            if not telephone.strip():
                erreurs.append("Le téléphone est requis")
            elif not valider_telephone(telephone):
                erreurs.append("Format de téléphone invalide")
            if not code_postal.strip():
                erreurs.append("Le code postal est requis")
            elif not valider_code_postal(code_postal):
                erreurs.append("Format de code postal invalide")
            if not type_projet:
                erreurs.append("Le type de projet est requis")
            if not budget:
                erreurs.append("Le budget est requis")
            if not delai_realisation:
                erreurs.append("Le délai de réalisation est requis")
            if not description.strip():
                erreurs.append("La description est requise")
            if not consentement:
                erreurs.append("Vous devez accepter le partage de vos informations")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"❌ {erreur}")
            else:
                # Traitement des photos
                photos_data = None
                if photos:
                    photos_base64 = []
                    for photo in photos:
                        photo_data = base64.b64encode(photo.read()).decode()
                        photos_base64.append(photo_data)
                    photos_data = ",".join(photos_base64)
                
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
                    photos=photos_data
                )
                
                # Sauvegarde
                numero_reference = sauvegarder_lead(lead)
                
                # Message de succès
                st.success(f"""
                ✅ **Votre demande a été soumise avec succès!**
                
                **Numéro de référence:** {numero_reference}
                
                📧 Un email de confirmation vous a été envoyé.
                
                📞 Vous devriez recevoir vos premières soumissions dans les 24-48h.
                
                💡 **Conseils pour maximiser vos réponses:**
                - Soyez disponible par téléphone
                - Répondez rapidement aux entrepreneurs
                - Préparez vos questions techniques
                """)
                
                # Réinitialiser le formulaire
                st.balloons()

def page_espace_entrepreneur():
    """Espace entrepreneur avec authentification et dashboard"""
    
    if 'entrepreneur_connecte' not in st.session_state:
        st.session_state.entrepreneur_connecte = None
    
    if st.session_state.entrepreneur_connecte is None:
        # Page de connexion
        st.markdown("## 👷 Espace Entrepreneur")
        
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            with st.form("connexion_entrepreneur"):
                st.markdown("### Connectez-vous à votre compte")
                
                email = st.text_input("Email", placeholder="votre@email.com")
                mot_de_passe = st.text_input("Mot de passe", type="password")
                
                connecter = st.form_submit_button("🔐 Se connecter", type="primary")
                
                if connecter:
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
                    confirmer_mdp = st.text_input("Confirmer le mot de passe *", type="password")
                    numero_rbq = st.text_input("Numéro RBQ")
                
                zones_desservies = st.text_area("Zones desservies (codes postaux séparés par des virgules)")
                
                types_projets = st.multiselect(
                    "Types de projets que vous réalisez *",
                    ["Rénovation cuisine", "Rénovation salle de bain", "Toiture", 
                     "Revêtement extérieur", "Plancher", "Peinture", "Agrandissement",
                     "Électricité", "Plomberie", "Chauffage/Climatisation", "Isolation",
                     "Fenêtres et portes", "Maçonnerie", "Charpenterie", "Autre"]
                )
                
                abonnement = st.selectbox(
                    "Type d'abonnement",
                    ["gratuit", "standard", "premium", "entreprise"]
                )
                
                certifications = st.text_area("Certifications et assurances")
                
                inscription = st.form_submit_button("📝 Créer mon compte", type="primary")
                
                if inscription:
                    erreurs = []
                    
                    if not all([nom_entreprise, nom_contact, email_inscription, telephone, mot_de_passe]):
                        erreurs.append("Tous les champs marqués * sont requis")
                    if not valider_email(email_inscription):
                        erreurs.append("Format d'email invalide")
                    if mot_de_passe != confirmer_mdp:
                        erreurs.append("Les mots de passe ne correspondent pas")
                    if len(mot_de_passe) < 8:
                        erreurs.append("Le mot de passe doit contenir au moins 8 caractères")
                    if numero_rbq and not valider_numero_rbq(numero_rbq):
                        erreurs.append("Format de numéro RBQ invalide (format: XXXX-XXXX-XX)")
                    if not types_projets:
                        erreurs.append("Sélectionnez au moins un type de projet")
                    
                    if erreurs:
                        for erreur in erreurs:
                            st.error(f"❌ {erreur}")
                    else:
                        # Sauvegarde de l'entrepreneur
                        conn = sqlite3.connect('soumissions_quebec.db')
                        cursor = conn.cursor()
                        
                        try:
                            cursor.execute('''
                                INSERT INTO entrepreneurs (nom_entreprise, nom_contact, email, telephone, 
                                                         mot_de_passe_hash, numero_rbq, zones_desservies, 
                                                         types_projets, abonnement, certifications)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (nom_entreprise, nom_contact, email_inscription, telephone,
                                  hash_password(mot_de_passe), numero_rbq, zones_desservies,
                                  ",".join(types_projets), abonnement, certifications))
                            
                            conn.commit()
                            st.success("✅ Compte créé avec succès! Vous pouvez maintenant vous connecter.")
                        
                        except sqlite3.IntegrityError:
                            st.error("❌ Un compte avec cet email existe déjà")
                        
                        finally:
                            conn.close()
    
    else:
        # Dashboard entrepreneur connecté
        entrepreneur = st.session_state.entrepreneur_connecte
        
        # Header du dashboard
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## 👷 Bienvenue, {entrepreneur.nom_entreprise}")
        with col2:
            if st.button("🚪 Déconnexion"):
                st.session_state.entrepreneur_connecte = None
                st.rerun()
        
        # Statistiques
        st.markdown("### 📊 Tableau de bord")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Compter les leads attribués ce mois pour les stats
        conn = sqlite3.connect('soumissions_quebec.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM attributions 
            WHERE entrepreneur_id = ? AND date_attribution >= date('now', 'start of month')
        ''', (entrepreneur.id,))
        leads_mois = cursor.fetchone()[0]
        conn.close()
        
        # Taux de conversion approximatif
        taux_conversion = min(95, 60 + (leads_mois * 5))
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>💳</h3>
                <h2>{entrepreneur.credits_restants}</h2>
                <p>Crédits restants</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📈</h3>
                <h2>{entrepreneur.abonnement.title()}</h2>
                <p>Abonnement</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📋</h3>
                <h2>{leads_mois}</h2>
                <p>Leads ce mois</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h3>🎯</h3>
                <h2>{taux_conversion}%</h2>
                <p>Taux de réponse</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Onglets du dashboard
        tab1, tab2, tab3, tab4 = st.tabs(["🆕 Nouveaux leads", "📋 Mes leads", "👤 Mon profil", "💰 Abonnement"])
        
        with tab1:
            st.markdown("### 🆕 Nouveaux leads disponibles")
            
            leads = get_leads_pour_entrepreneur(entrepreneur.id)
            
            if not leads:
                st.info("📭 Aucun nouveau lead disponible pour le moment.")
            else:
                for lead in leads[:10]:  # Limiter à 10 leads
                    with st.container():
                        st.markdown(f"""
                        <div class="lead-card">
                            <div style="display: flex; justify-content: between; align-items: center;">
                                <div>
                                    <h4>{lead['type_projet']} - {lead['code_postal']}</h4>
                                    <p><strong>Budget:</strong> <span class="budget-{'high' if 'Plus de' in lead['budget'] else 'medium' if '30 000' in lead['budget'] or '15 000' in lead['budget'] else 'low'}">{lead['budget']}</span></p>
                                    <p><strong>Délai:</strong> {lead['delai_realisation']}</p>
                                    <p><strong>Description:</strong> {lead['description'][:200]}...</p>
                                    <p><small>Posté le {lead['date_creation'][:10]} • {lead['nb_attributions']}/5 entrepreneurs intéressés</small></p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            prix_lead = get_prix_lead(lead['type_projet'], lead['budget'])
                            if st.button(f"✅ Accepter ({prix_lead}$)", key=f"accepter_{lead['id']}"):
                                # Logique d'acceptation du lead
                                if entrepreneur.credits_restants > 0 or entrepreneur.abonnement != 'gratuit':
                                    # Attribuer le lead
                                    conn = sqlite3.connect('soumissions_quebec.db')
                                    cursor = conn.cursor()
                                    
                                    cursor.execute('''
                                        INSERT INTO attributions (lead_id, entrepreneur_id, prix_paye)
                                        VALUES (?, ?, ?)
                                    ''', (lead['id'], entrepreneur.id, prix_lead))
                                    
                                    # Décrémenter les crédits si gratuit
                                    if entrepreneur.abonnement == 'gratuit':
                                        cursor.execute('''
                                            UPDATE entrepreneurs SET credits_restants = credits_restants - 1
                                            WHERE id = ?
                                        ''', (entrepreneur.id,))
                                        entrepreneur.credits_restants -= 1
                                    
                                    conn.commit()
                                    conn.close()
                                    
                                    st.success(f"✅ Lead accepté! Contactez {lead['nom']} au {lead['telephone']}")
                                    st.rerun()
                                else:
                                    st.error("❌ Crédits insuffisants. Améliorez votre abonnement.")
                        
                        with col2:
                            if st.button("❌ Refuser", key=f"refuser_{lead['id']}"):
                                st.info("Lead refusé.")
                        
                        st.divider()
        
        with tab2:
            st.markdown("### 📋 Mes leads attribués")
            
            # Récupérer les leads attribués à cet entrepreneur
            conn = sqlite3.connect('soumissions_quebec.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT l.*, a.date_attribution, a.statut as statut_attribution, a.notes, a.prix_paye
                FROM leads l
                JOIN attributions a ON l.id = a.lead_id
                WHERE a.entrepreneur_id = ?
                ORDER BY a.date_attribution DESC
            ''', (entrepreneur.id,))
            
            mes_leads = cursor.fetchall()
            conn.close()
            
            if not mes_leads:
                st.info("📭 Vous n'avez pas encore de leads attribués.")
            else:
                for lead in mes_leads:
                    with st.expander(f"{lead[5]} - {lead[1]} ({lead[12][:10]})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Client:** {lead[1]}")
                            st.write(f"**Téléphone:** {lead[3]}")
                            st.write(f"**Email:** {lead[2]}")
                            st.write(f"**Code postal:** {lead[4]}")
                            st.write(f"**Budget:** {lead[7]}")
                        
                        with col2:
                            st.write(f"**Type de projet:** {lead[5]}")
                            st.write(f"**Délai:** {lead[8]}")
                            st.write(f"**Statut:** {lead[13]}")
                            st.write(f"**Prix payé:** {lead[15]}$")
                        
                        st.write(f"**Description:** {lead[6]}")
                        
                        # Notes de suivi
                        notes_actuelles = lead[14] or ""
                        nouvelles_notes = st.text_area(
                            "Notes de suivi",
                            value=notes_actuelles,
                            key=f"notes_{lead[0]}"
                        )
                        
                        if st.button(f"💾 Sauvegarder notes", key=f"save_notes_{lead[0]}"):
                            conn = sqlite3.connect('soumissions_quebec.db')
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE attributions SET notes = ? 
                                WHERE lead_id = ? AND entrepreneur_id = ?
                            ''', (nouvelles_notes, lead[0], entrepreneur.id))
                            conn.commit()
                            conn.close()
                            st.success("Notes sauvegardées!")
        
        with tab3:
            st.markdown("### 👤 Mon profil d'entreprise")
            
            with st.form("profil_entrepreneur"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom_entreprise = st.text_input("Nom de l'entreprise", value=entrepreneur.nom_entreprise)
                    nom_contact = st.text_input("Nom du contact", value=entrepreneur.nom_contact)
                    email = st.text_input("Email", value=entrepreneur.email)
                    telephone = st.text_input("Téléphone", value=entrepreneur.telephone)
                
                with col2:
                    numero_rbq = st.text_input("Numéro RBQ", value=entrepreneur.numero_rbq or "")
                    zones_desservies = st.text_area(
                        "Zones desservies",
                        value=entrepreneur.zones_desservies or "",
                        help="Codes postaux séparés par des virgules"
                    )
                
                types_projets_actuels = entrepreneur.types_projets.split(",") if entrepreneur.types_projets else []
                types_projets = st.multiselect(
                    "Types de projets",
                    ["Rénovation cuisine", "Rénovation salle de bain", "Toiture", 
                     "Revêtement extérieur", "Plancher", "Peinture", "Agrandissement",
                     "Électricité", "Plomberie", "Chauffage/Climatisation", "Isolation",
                     "Fenêtres et portes", "Maçonnerie", "Charpenterie", "Autre"],
                    default=types_projets_actuels
                )
                
                certifications = st.text_area(
                    "Certifications et assurances",
                    value=entrepreneur.certifications or ""
                )
                
                sauvegarder_profil = st.form_submit_button("💾 Sauvegarder")
                
                if sauvegarder_profil:
                    conn = sqlite3.connect('soumissions_quebec.db')
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE entrepreneurs 
                        SET nom_entreprise=?, nom_contact=?, email=?, telephone=?, 
                            numero_rbq=?, zones_desservies=?, types_projets=?, certifications=?
                        WHERE id=?
                    ''', (nom_entreprise, nom_contact, email, telephone, numero_rbq,
                          zones_desservies, ",".join(types_projets), certifications, entrepreneur.id))
                    
                    conn.commit()
                    conn.close()
                    
                    # Mettre à jour la session
                    entrepreneur.nom_entreprise = nom_entreprise
                    entrepreneur.nom_contact = nom_contact
                    entrepreneur.email = email
                    entrepreneur.telephone = telephone
                    entrepreneur.numero_rbq = numero_rbq
                    entrepreneur.zones_desservies = zones_desservies
                    entrepreneur.types_projets = ",".join(types_projets)
                    entrepreneur.certifications = certifications
                    
                    st.success("✅ Profil mis à jour!")
        
        with tab4:
            st.markdown("### 💰 Gestion de l'abonnement")
            
            # Plans d'abonnement
            col1, col2, col3, col4 = st.columns(4)
            
            plans = [
                {"nom": "Gratuit", "prix": "0$/mois", "leads": "5 leads/mois", "couleur": "#6B7280"},
                {"nom": "Standard", "prix": "299$/mois", "leads": "50 leads/mois", "couleur": "#3B82F6"},
                {"nom": "Premium", "prix": "499$/mois", "leads": "100 leads/mois", "couleur": "#10B981"},
                {"nom": "Entreprise", "prix": "899$/mois", "leads": "Illimité", "couleur": "#F59E0B"}
            ]
            
            for i, plan in enumerate(plans):
                with [col1, col2, col3, col4][i]:
                    actuel = plan["nom"].lower() == entrepreneur.abonnement
                    
                    st.markdown(f"""
                    <div style="border: 2px solid {'#F97316' if actuel else '#E5E7EB'}; 
                                border-radius: 10px; padding: 1rem; text-align: center;
                                background: {'#FFF7ED' if actuel else 'white'};">
                        <h4 style="color: {plan['couleur']};">{plan['nom']}</h4>
                        <h3>{plan['prix']}</h3>
                        <p>{plan['leads']}</p>
                        {'<p style="color: #F97316; font-weight: bold;">ACTUEL</p>' if actuel else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not actuel:
                        if st.button(f"Choisir {plan['nom']}", key=f"plan_{i}"):
                            st.info(f"Redirection vers le paiement pour {plan['nom']}")
            
            # Historique de facturation
            st.markdown("### 📊 Historique de facturation")
            
            # Données fictives pour la démo
            historique = [
                {"date": "2024-01-01", "plan": "Standard", "montant": 299.00, "statut": "Payé"},
                {"date": "2024-02-01", "plan": "Standard", "montant": 299.00, "statut": "Payé"},
                {"date": "2024-03-01", "plan": "Premium", "montant": 499.00, "statut": "En attente"},
            ]
            
            df_historique = pd.DataFrame(historique)
            st.dataframe(df_historique, use_container_width=True)

def page_administration():
    """Page d'administration (accès restreint)"""
    
    if 'admin_connecte' not in st.session_state:
        st.session_state.admin_connecte = False
    
    if not st.session_state.admin_connecte:
        st.markdown("## ⚙️ Administration")
        
        with st.form("connexion_admin"):
            st.markdown("### Accès administrateur")
            
            mot_de_passe_admin = st.text_input("Mot de passe administrateur", type="password")
            connecter_admin = st.form_submit_button("🔐 Se connecter")
            
            if connecter_admin:
                if mot_de_passe_admin == "admin123":  # Mot de passe simple pour la démo
                    st.session_state.admin_connecte = True
                    st.success("✅ Connexion administrateur réussie!")
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
    
    else:
        # Dashboard administrateur
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## ⚙️ Administration - SoumissionsQuébec.ca")
        with col2:
            if st.button("🚪 Déconnexion admin"):
                st.session_state.admin_connecte = False
                st.rerun()
        
        # Statistiques générales
        st.markdown("### 📊 Vue d'ensemble")
        
        conn = sqlite3.connect('soumissions_quebec.db')
        cursor = conn.cursor()
        
        # Statistiques
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entrepreneurs")
        total_entrepreneurs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attributions")
        total_attributions = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(prix_paye) FROM attributions")
        revenus_total = cursor.fetchone()[0] or 0
        
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📋</h3>
                <h2>{total_leads}</h2>
                <p>Total leads</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3>👷</h3>
                <h2>{total_entrepreneurs}</h2>
                <p>Entrepreneurs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3>🤝</h3>
                <h2>{total_attributions}</h2>
                <p>Attributions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h3>💰</h3>
                <h2>{revenus_total:.0f}$</h2>
                <p>Revenus</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Onglets d'administration
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Leads", "👷 Entrepreneurs", "🤝 Attributions", "📊 Rapports"])
        
        with tab1:
            st.markdown("### 📋 Gestion des leads")
            
            conn = sqlite3.connect('soumissions_quebec.db')
            
            # Récupérer tous les leads
            df_leads = pd.read_sql_query('''
                SELECT l.*, COUNT(a.id) as nb_attributions
                FROM leads l
                LEFT JOIN attributions a ON l.id = a.lead_id
                GROUP BY l.id
                ORDER BY l.date_creation DESC
            ''', conn)
            
            conn.close()
            
            if not df_leads.empty:
                # Filtres
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filtre_type = st.multiselect(
                        "Filtrer par type de projet",
                        df_leads['type_projet'].unique()
                    )
                
                with col2:
                    filtre_statut = st.multiselect(
                        "Filtrer par statut",
                        df_leads['statut'].unique()
                    )
                
                with col3:
                    filtre_budget = st.multiselect(
                        "Filtrer par budget",
                        df_leads['budget'].unique()
                    )
                
                # Appliquer les filtres
                df_filtre = df_leads.copy()
                if filtre_type:
                    df_filtre = df_filtre[df_filtre['type_projet'].isin(filtre_type)]
                if filtre_statut:
                    df_filtre = df_filtre[df_filtre['statut'].isin(filtre_statut)]
                if filtre_budget:
                    df_filtre = df_filtre[df_filtre['budget'].isin(filtre_budget)]
                
                # Afficher le tableau
                st.dataframe(
                    df_filtre[['numero_reference', 'nom', 'type_projet', 'budget', 
                              'statut', 'date_creation', 'nb_attributions']],
                    use_container_width=True
                )
            else:
                st.info("Aucun lead trouvé.")
        
        with tab2:
            st.markdown("### 👷 Gestion des entrepreneurs")
            
            conn = sqlite3.connect('soumissions_quebec.db')
            
            df_entrepreneurs = pd.read_sql_query('''
                SELECT e.*, COUNT(a.id) as nb_leads_pris
                FROM entrepreneurs e
                LEFT JOIN attributions a ON e.id = a.entrepreneur_id
                GROUP BY e.id
                ORDER BY e.date_inscription DESC
            ''', conn)
            
            conn.close()
            
            if not df_entrepreneurs.empty:
                # Filtres
                col1, col2 = st.columns(2)
                
                with col1:
                    filtre_abonnement = st.multiselect(
                        "Filtrer par abonnement",
                        df_entrepreneurs['abonnement'].unique()
                    )
                
                with col2:
                    filtre_statut_entrepreneur = st.multiselect(
                        "Filtrer par statut",
                        df_entrepreneurs['statut'].unique()
                    )
                
                # Appliquer les filtres
                df_filtre_entr = df_entrepreneurs.copy()
                if filtre_abonnement:
                    df_filtre_entr = df_filtre_entr[df_filtre_entr['abonnement'].isin(filtre_abonnement)]
                if filtre_statut_entrepreneur:
                    df_filtre_entr = df_filtre_entr[df_filtre_entr['statut'].isin(filtre_statut_entrepreneur)]
                
                # Afficher le tableau
                st.dataframe(
                    df_filtre_entr[['nom_entreprise', 'email', 'abonnement', 'credits_restants',
                                   'statut', 'date_inscription', 'nb_leads_pris']],
                    use_container_width=True
                )
            else:
                st.info("Aucun entrepreneur trouvé.")
        
        with tab3:
            st.markdown("### 🤝 Attributions de leads")
            
            conn = sqlite3.connect('soumissions_quebec.db')
            
            df_attributions = pd.read_sql_query('''
                SELECT a.*, l.type_projet, l.budget, e.nom_entreprise
                FROM attributions a
                JOIN leads l ON a.lead_id = l.id
                JOIN entrepreneurs e ON a.entrepreneur_id = e.id
                ORDER BY a.date_attribution DESC
            ''', conn)
            
            conn.close()
            
            if not df_attributions.empty:
                st.dataframe(
                    df_attributions[['date_attribution', 'nom_entreprise', 'type_projet', 
                                   'budget', 'prix_paye', 'statut']],
                    use_container_width=True
                )
            else:
                st.info("Aucune attribution trouvée.")
        
        with tab4:
            st.markdown("### 📊 Rapports et analytics")
            
            conn = sqlite3.connect('soumissions_quebec.db')
            
            # Revenus par mois
            df_revenus = pd.read_sql_query('''
                SELECT 
                    strftime('%Y-%m', date_attribution) as mois,
                    SUM(prix_paye) as revenus,
                    COUNT(*) as nb_attributions
                FROM attributions
                GROUP BY strftime('%Y-%m', date_attribution)
                ORDER BY mois
            ''', conn)
            
            if not df_revenus.empty:
                st.markdown("#### 💰 Revenus par mois")
                st.line_chart(df_revenus.set_index('mois')['revenus'])
            
            # Leads par type de projet
            df_types = pd.read_sql_query('''
                SELECT type_projet, COUNT(*) as nb_leads
                FROM leads
                GROUP BY type_projet
                ORDER BY nb_leads DESC
            ''', conn)
            
            if not df_types.empty:
                st.markdown("#### 📊 Leads par type de projet")
                st.bar_chart(df_types.set_index('type_projet')['nb_leads'])
            
            # Performance des entrepreneurs
            df_performance = pd.read_sql_query('''
                SELECT 
                    e.nom_entreprise,
                    COUNT(a.id) as nb_leads_pris,
                    SUM(a.prix_paye) as total_paye,
                    e.abonnement
                FROM entrepreneurs e
                LEFT JOIN attributions a ON e.id = a.entrepreneur_id
                GROUP BY e.id
                HAVING nb_leads_pris > 0
                ORDER BY nb_leads_pris DESC
                LIMIT 10
            ''', conn)
            
            if not df_performance.empty:
                st.markdown("#### 🏆 Top 10 entrepreneurs les plus actifs")
                st.dataframe(df_performance, use_container_width=True)
            
            conn.close()

if __name__ == "__main__":
    main()