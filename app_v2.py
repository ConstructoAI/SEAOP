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
    date_limite_soumissions: Optional[str] = None
    date_debut_souhaite: Optional[str] = None
    niveau_urgence: str = "normal"
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
            date_limite_soumissions DATE,
            date_debut_souhaite DATE,
            niveau_urgence TEXT DEFAULT 'normal',
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
    
    # Table des notifications
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
                          description, budget, delai_realisation, 
                          date_limite_soumissions, date_debut_souhaite, niveau_urgence,
                          photos, plans, documents, numero_reference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lead.nom, lead.email, lead.telephone, lead.code_postal, lead.type_projet,
          lead.description, lead.budget, lead.delai_realisation,
          lead.date_limite_soumissions, lead.date_debut_souhaite, lead.niveau_urgence,
          lead.photos, lead.plans, lead.documents, numero_ref))
    
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
    """Récupère tous les projets disponibles pour soumission avec informations d'urgence"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
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
    ''')
    
    projets = []
    for row in cursor.fetchall():
        projet = {
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'plans': row[10], 'documents': row[11], 'date_creation': row[12],
            'statut': row[13], 'numero_reference': row[14],
            'visible_entrepreneurs': row[15], 'accepte_soumissions': row[16],
            'date_limite_soumissions': row[17], 'date_debut_souhaite': row[18],
            'niveau_urgence': row[19], 'nb_soumissions': row[20]
        }
        
        # Calculer les jours restants
        projet['jours_restants_soumissions'] = calculer_jours_restants(projet['date_limite_soumissions'])
        projet['jours_restants_debut'] = calculer_jours_restants(projet['date_debut_souhaite'])
        
        # Mettre à jour l'urgence automatiquement
        mettre_a_jour_urgence_projet(projet['id'])
        
        projets.append(projet)
    
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

# Fonctions de gestion des évaluations
def ajouter_evaluation(soumission_id: int, evaluateur_type: str, note: int, commentaire: str = "") -> bool:
    """Ajoute une évaluation pour une soumission"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO evaluations (soumission_id, evaluateur_type, note, commentaire)
            VALUES (?, ?, ?, ?)
        ''', (soumission_id, evaluateur_type, note, commentaire))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'évaluation: {e}")
        return False

def get_evaluations_entrepreneur(entrepreneur_id: int) -> Dict:
    """Récupère les statistiques d'évaluation d'un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            AVG(e.note) as note_moyenne,
            COUNT(e.note) as nombre_evaluations,
            COUNT(CASE WHEN e.note >= 4 THEN 1 END) as evaluations_positives
        FROM evaluations e
        JOIN soumissions s ON e.soumission_id = s.id
        WHERE s.entrepreneur_id = ? AND e.evaluateur_type = 'client'
    ''', (entrepreneur_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return {
            'note_moyenne': round(result[0], 1),
            'nombre_evaluations': result[1],
            'evaluations_positives': result[2],
            'pourcentage_positif': round((result[2] / result[1] * 100), 1) if result[1] > 0 else 0
        }
    else:
        return {
            'note_moyenne': 0,
            'nombre_evaluations': 0,
            'evaluations_positives': 0,
            'pourcentage_positif': 0
        }

def get_evaluation_soumission(soumission_id: int, evaluateur_type: str) -> Optional[Dict]:
    """Récupère l'évaluation d'une soumission"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT note, commentaire, date_evaluation
        FROM evaluations
        WHERE soumission_id = ? AND evaluateur_type = ?
    ''', (soumission_id, evaluateur_type))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'note': result[0],
            'commentaire': result[1],
            'date_evaluation': result[2]
        }
    return None

def get_derniers_commentaires_entrepreneur(entrepreneur_id: int, limit: int = 5) -> List[Dict]:
    """Récupère les derniers commentaires d'un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.note, e.commentaire, e.date_evaluation, l.type_projet
        FROM evaluations e
        JOIN soumissions s ON e.soumission_id = s.id
        JOIN leads l ON s.lead_id = l.id
        WHERE s.entrepreneur_id = ? AND e.evaluateur_type = 'client' 
        AND e.commentaire IS NOT NULL AND e.commentaire != ''
        ORDER BY e.date_evaluation DESC
        LIMIT ?
    ''', (entrepreneur_id, limit))
    
    commentaires = []
    for row in cursor.fetchall():
        commentaires.append({
            'note': row[0],
            'commentaire': row[1],
            'date_evaluation': row[2][:10] if row[2] else "",
            'type_projet': row[3]
        })
    
    conn.close()
    return commentaires

# Fonctions de gestion des notifications
def creer_notification(utilisateur_type: str, utilisateur_id: int, type_notif: str, titre: str, message: str, lien_id: int = None) -> bool:
    """Crée une nouvelle notification"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (utilisateur_type, utilisateur_id, type_notification, titre, message, lien_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (utilisateur_type, utilisateur_id, type_notif, titre, message, lien_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la création de notification: {e}")
        return False

def get_notifications_utilisateur(utilisateur_type: str, utilisateur_id: int, limit: int = 10) -> List[Dict]:
    """Récupère les notifications d'un utilisateur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, type_notification, titre, message, lien_id, lu, date_creation
        FROM notifications
        WHERE utilisateur_type = ? AND utilisateur_id = ?
        ORDER BY date_creation DESC
        LIMIT ?
    ''', (utilisateur_type, utilisateur_id, limit))
    
    notifications = []
    for row in cursor.fetchall():
        notifications.append({
            'id': row[0],
            'type_notification': row[1],
            'titre': row[2],
            'message': row[3],
            'lien_id': row[4],
            'lu': row[5],
            'date_creation': row[6]
        })
    
    conn.close()
    return notifications

def count_notifications_non_lues(utilisateur_type: str, utilisateur_id: int) -> int:
    """Compte les notifications non lues d'un utilisateur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM notifications
        WHERE utilisateur_type = ? AND utilisateur_id = ? AND lu = 0
    ''', (utilisateur_type, utilisateur_id))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def marquer_notification_lue(notification_id: int) -> bool:
    """Marque une notification comme lue"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications SET lu = 1 WHERE id = ?
        ''', (notification_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors du marquage de notification: {e}")
        return False

def marquer_toutes_notifications_lues(utilisateur_type: str, utilisateur_id: int) -> bool:
    """Marque toutes les notifications d'un utilisateur comme lues"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications SET lu = 1 
            WHERE utilisateur_type = ? AND utilisateur_id = ? AND lu = 0
        ''', (utilisateur_type, utilisateur_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors du marquage de toutes les notifications: {e}")
        return False

# Fonctions spécifiques de création de notifications
def notifier_nouvelle_soumission(lead_id: int):
    """Notifie le client qu'il a reçu une nouvelle soumission"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Récupérer les infos du projet
    cursor.execute('SELECT nom, type_projet FROM leads WHERE id = ?', (lead_id,))
    projet = cursor.fetchone()
    
    if projet:
        titre = "📩 Nouvelle soumission reçue"
        message = f"Vous avez reçu une nouvelle soumission pour votre projet : {projet[1]}"
        creer_notification('client', lead_id, 'nouvelle_soumission', titre, message, lead_id)
    
    conn.close()

def notifier_soumission_acceptee(soumission_id: int):
    """Notifie l'entrepreneur que sa soumission a été acceptée"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Récupérer les infos de la soumission
    cursor.execute('''
        SELECT s.entrepreneur_id, l.type_projet, s.montant
        FROM soumissions s
        JOIN leads l ON s.lead_id = l.id
        WHERE s.id = ?
    ''', (soumission_id,))
    
    result = cursor.fetchone()
    if result:
        entrepreneur_id, type_projet, montant = result
        titre = "🎉 Soumission acceptée !"
        message = f"Félicitations ! Votre soumission de {montant:,.2f}$ pour le projet '{type_projet}' a été acceptée."
        creer_notification('entrepreneur', entrepreneur_id, 'soumission_acceptee', titre, message, soumission_id)
    
    conn.close()

def notifier_soumission_refusee(soumission_id: int):
    """Notifie l'entrepreneur que sa soumission a été refusée"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Récupérer les infos de la soumission
    cursor.execute('''
        SELECT s.entrepreneur_id, l.type_projet
        FROM soumissions s
        JOIN leads l ON s.lead_id = l.id
        WHERE s.id = ?
    ''', (soumission_id,))
    
    result = cursor.fetchone()
    if result:
        entrepreneur_id, type_projet = result
        titre = "❌ Soumission non retenue"
        message = f"Votre soumission pour le projet '{type_projet}' n'a pas été retenue. Continuez à soumissionner !"
        creer_notification('entrepreneur', entrepreneur_id, 'soumission_refusee', titre, message, soumission_id)
    
    conn.close()

def notifier_nouveau_message(lead_id: int, entrepreneur_id: int, expediteur_type: str):
    """Notifie qu'un nouveau message a été reçu"""
    if expediteur_type == 'client':
        # Notifier l'entrepreneur
        titre = "💬 Nouveau message client"
        message = "Vous avez reçu un nouveau message d'un client"
        creer_notification('entrepreneur', entrepreneur_id, 'nouveau_message', titre, message, lead_id)
    else:
        # Notifier le client
        titre = "💬 Nouveau message entrepreneur"
        message = "Vous avez reçu un nouveau message d'un entrepreneur"
        creer_notification('client', lead_id, 'nouveau_message', titre, message, lead_id)

# Fonctions de statistiques et dashboard
def get_stats_client(client_email: str) -> Dict:
    """Récupère les statistiques d'un client"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Projets du client
    cursor.execute('''
        SELECT COUNT(*) as nb_projets,
               AVG(nb_soumissions) as moy_soumissions_par_projet
        FROM (
            SELECT l.id, COUNT(s.id) as nb_soumissions
            FROM leads l
            LEFT JOIN soumissions s ON l.id = s.lead_id
            WHERE l.email = ?
            GROUP BY l.id
        )
    ''', (client_email,))
    
    projets_stats = cursor.fetchone()
    
    # Montant moyen des soumissions
    cursor.execute('''
        SELECT AVG(s.montant) as montant_moyen,
               COUNT(s.id) as total_soumissions,
               COUNT(CASE WHEN s.statut = 'acceptee' THEN 1 END) as soumissions_acceptees
        FROM soumissions s
        JOIN leads l ON s.lead_id = l.id
        WHERE l.email = ?
    ''', (client_email,))
    
    soumissions_stats = cursor.fetchone()
    
    # Évolution mensuelle
    cursor.execute('''
        SELECT strftime('%Y-%m', l.date_creation) as mois,
               COUNT(l.id) as nb_projets,
               COUNT(s.id) as nb_soumissions
        FROM leads l
        LEFT JOIN soumissions s ON l.id = s.lead_id
        WHERE l.email = ?
        GROUP BY strftime('%Y-%m', l.date_creation)
        ORDER BY mois DESC
        LIMIT 6
    ''', (client_email,))
    
    evolution_mensuelle = cursor.fetchall()
    
    conn.close()
    
    return {
        'nb_projets': projets_stats[0] if projets_stats else 0,
        'moy_soumissions_par_projet': round(projets_stats[1], 1) if projets_stats[1] else 0,
        'montant_moyen_soumissions': round(soumissions_stats[0], 2) if soumissions_stats[0] else 0,
        'total_soumissions': soumissions_stats[1] if soumissions_stats else 0,
        'soumissions_acceptees': soumissions_stats[2] if soumissions_stats else 0,
        'taux_acceptation': round((soumissions_stats[2] / soumissions_stats[1] * 100), 1) if soumissions_stats[1] and soumissions_stats[1] > 0 else 0,
        'evolution_mensuelle': evolution_mensuelle
    }

def get_stats_entrepreneur(entrepreneur_id: int) -> Dict:
    """Récupère les statistiques d'un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Statistiques générales des soumissions
    cursor.execute('''
        SELECT COUNT(*) as total_soumissions,
               COUNT(CASE WHEN statut = 'acceptee' THEN 1 END) as soumissions_acceptees,
               COUNT(CASE WHEN statut = 'refusee' THEN 1 END) as soumissions_refusees,
               AVG(montant) as montant_moyen,
               SUM(CASE WHEN statut = 'acceptee' THEN montant ELSE 0 END) as ca_total
        FROM soumissions
        WHERE entrepreneur_id = ?
    ''', (entrepreneur_id,))
    
    soumissions_stats = cursor.fetchone()
    
    # Évolution mensuelle
    cursor.execute('''
        SELECT strftime('%Y-%m', date_creation) as mois,
               COUNT(*) as nb_soumissions,
               COUNT(CASE WHEN statut = 'acceptee' THEN 1 END) as nb_acceptees,
               SUM(CASE WHEN statut = 'acceptee' THEN montant ELSE 0 END) as ca_mois
        FROM soumissions
        WHERE entrepreneur_id = ?
        GROUP BY strftime('%Y-%m', date_creation)
        ORDER BY mois DESC
        LIMIT 6
    ''', (entrepreneur_id,))
    
    evolution_mensuelle = cursor.fetchall()
    
    # Note moyenne actuelle
    stats_eval = get_evaluations_entrepreneur(entrepreneur_id)
    
    conn.close()
    
    total_soum = soumissions_stats[0] if soumissions_stats else 0
    acceptees = soumissions_stats[1] if soumissions_stats else 0
    
    return {
        'total_soumissions': total_soum,
        'soumissions_acceptees': acceptees,
        'soumissions_refusees': soumissions_stats[2] if soumissions_stats else 0,
        'taux_succes': round((acceptees / total_soum * 100), 1) if total_soum > 0 else 0,
        'montant_moyen': round(soumissions_stats[3], 2) if soumissions_stats[3] else 0,
        'ca_total': round(soumissions_stats[4], 2) if soumissions_stats[4] else 0,
        'note_moyenne': stats_eval['note_moyenne'],
        'nb_evaluations': stats_eval['nombre_evaluations'],
        'evolution_mensuelle': evolution_mensuelle
    }

def get_stats_admin() -> Dict:
    """Récupère les statistiques globales de la plateforme"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Statistiques générales
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM leads) as total_projets,
            (SELECT COUNT(*) FROM entrepreneurs) as total_entrepreneurs,
            (SELECT COUNT(*) FROM soumissions) as total_soumissions,
            (SELECT SUM(CASE WHEN statut = 'acceptee' THEN montant ELSE 0 END) FROM soumissions) as ca_total
    ''')
    
    stats_generales = cursor.fetchone()
    
    # Top entrepreneurs du mois
    cursor.execute('''
        SELECT e.nom_entreprise,
               COUNT(s.id) as nb_soumissions,
               COUNT(CASE WHEN s.statut = 'acceptee' THEN 1 END) as nb_acceptees,
               SUM(CASE WHEN s.statut = 'acceptee' THEN s.montant ELSE 0 END) as ca_mois,
               AVG(ev.note) as note_moyenne
        FROM entrepreneurs e
        LEFT JOIN soumissions s ON e.id = s.entrepreneur_id 
            AND strftime('%Y-%m', s.date_creation) = strftime('%Y-%m', 'now')
        LEFT JOIN evaluations ev ON s.id = ev.soumission_id AND ev.evaluateur_type = 'client'
        GROUP BY e.id, e.nom_entreprise
        HAVING nb_soumissions > 0
        ORDER BY nb_acceptees DESC, ca_mois DESC
        LIMIT 5
    ''')
    
    top_entrepreneurs = cursor.fetchall()
    
    # Évolution mensuelle globale
    cursor.execute('''
        SELECT strftime('%Y-%m', date_creation) as mois,
               COUNT(*) as nb_projets
        FROM leads
        GROUP BY strftime('%Y-%m', date_creation)
        ORDER BY mois DESC
        LIMIT 6
    ''')
    
    evolution_projets = cursor.fetchall()
    
    cursor.execute('''
        SELECT strftime('%Y-%m', date_creation) as mois,
               COUNT(*) as nb_soumissions,
               SUM(CASE WHEN statut = 'acceptee' THEN montant ELSE 0 END) as ca_mois
        FROM soumissions
        GROUP BY strftime('%Y-%m', date_creation)
        ORDER BY mois DESC
        LIMIT 6
    ''')
    
    evolution_soumissions = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_projets': stats_generales[0] if stats_generales else 0,
        'total_entrepreneurs': stats_generales[1] if stats_generales else 0,
        'total_soumissions': stats_generales[2] if stats_generales else 0,
        'ca_total': round(stats_generales[3], 2) if stats_generales[3] else 0,
        'top_entrepreneurs': top_entrepreneurs,
        'evolution_projets': evolution_projets,
        'evolution_soumissions': evolution_soumissions
    }

# Fonctions de recherche et filtrage
def filtrer_projets_pour_entrepreneurs(
    type_projet: str = None,
    budget_min: float = None,
    budget_max: float = None,
    code_postal: str = None,
    delai_max: str = None,
    recherche_texte: str = None
) -> List[Dict]:
    """Filtre les projets disponibles selon les critères"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Construction de la requête dynamique
    query = '''
        SELECT l.*, 
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions
        FROM leads l
        WHERE l.visible_entrepreneurs = 1 AND l.accepte_soumissions = 1
    '''
    params = []
    
    if type_projet and type_projet != "Tous":
        query += " AND l.type_projet = ?"
        params.append(type_projet)
    
    if budget_min is not None:
        # Extraire le montant numérique du budget (format: "10 000 - 25 000 $")
        query += " AND CAST(REPLACE(REPLACE(SUBSTR(l.budget, 1, INSTR(l.budget, ' ') - 1), ' ', ''), '$', '') AS INTEGER) >= ?"
        params.append(budget_min)
    
    if budget_max is not None:
        query += " AND CAST(REPLACE(REPLACE(SUBSTR(l.budget, 1, INSTR(l.budget, ' ') - 1), ' ', ''), '$', '') AS INTEGER) <= ?"
        params.append(budget_max)
    
    if code_postal:
        query += " AND l.code_postal LIKE ?"
        params.append(f"{code_postal}%")
    
    if recherche_texte:
        query += " AND (l.description LIKE ? OR l.type_projet LIKE ? OR l.nom LIKE ?)"
        params.extend([f"%{recherche_texte}%", f"%{recherche_texte}%", f"%{recherche_texte}%"])
    
    query += " ORDER BY l.date_creation DESC"
    
    cursor.execute(query, params)
    
    projets = []
    for row in cursor.fetchall():
        projets.append({
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'plans': row[10], 'documents': row[11], 'date_creation': row[12],
            'statut': row[13], 'numero_reference': row[14],
            'visible_entrepreneurs': row[15], 'accepte_soumissions': row[16],
            'nb_soumissions': row[17]
        })
    
    conn.close()
    return projets

def filtrer_mes_projets(
    email: str,
    statut: str = None,
    periode: str = None,
    type_projet: str = None,
    recherche_texte: str = None
) -> List[Dict]:
    """Filtre les projets d'un client selon les critères"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT l.*,
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions,
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id AND s.statut = 'acceptee') as nb_acceptees
        FROM leads l
        WHERE l.email = ?
    '''
    params = [email]
    
    if statut and statut != "Tous":
        if statut == "Avec soumissions":
            query += " AND (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) > 0"
        elif statut == "Sans soumissions":
            query += " AND (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) = 0"
        elif statut == "Projet terminé":
            query += " AND (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id AND s.statut = 'acceptee') > 0"
    
    if periode and periode != "Toutes":
        if periode == "Cette semaine":
            query += " AND l.date_creation >= date('now', '-7 days')"
        elif periode == "Ce mois":
            query += " AND l.date_creation >= date('now', 'start of month')"
        elif periode == "Ce trimestre":
            query += " AND l.date_creation >= date('now', '-3 months')"
    
    if type_projet and type_projet != "Tous":
        query += " AND l.type_projet = ?"
        params.append(type_projet)
    
    if recherche_texte:
        query += " AND (l.description LIKE ? OR l.type_projet LIKE ? OR l.numero_reference LIKE ?)"
        params.extend([f"%{recherche_texte}%", f"%{recherche_texte}%", f"%{recherche_texte}%"])
    
    query += " ORDER BY l.date_creation DESC"
    
    cursor.execute(query, params)
    
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

def filtrer_soumissions_entrepreneur(
    entrepreneur_id: int,
    statut: str = None,
    periode: str = None,
    montant_min: float = None,
    montant_max: float = None
) -> List[Dict]:
    """Filtre les soumissions d'un entrepreneur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT s.*, l.type_projet, l.nom as nom_client, l.numero_reference
        FROM soumissions s
        JOIN leads l ON s.lead_id = l.id
        WHERE s.entrepreneur_id = ?
    '''
    params = [entrepreneur_id]
    
    if statut and statut != "Tous":
        query += " AND s.statut = ?"
        params.append(statut)
    
    if periode and periode != "Toutes":
        if periode == "Ce mois":
            query += " AND s.date_creation >= date('now', 'start of month')"
        elif periode == "Ce trimestre":
            query += " AND s.date_creation >= date('now', '-3 months')"
        elif periode == "Cette année":
            query += " AND s.date_creation >= date('now', 'start of year')"
    
    if montant_min is not None:
        query += " AND s.montant >= ?"
        params.append(montant_min)
    
    if montant_max is not None:
        query += " AND s.montant <= ?"
        params.append(montant_max)
    
    query += " ORDER BY s.date_creation DESC"
    
    cursor.execute(query, params)
    
    soumissions = []
    for row in cursor.fetchall():
        soumissions.append({
            'id': row[0], 'lead_id': row[1], 'entrepreneur_id': row[2],
            'montant': row[3], 'description_travaux': row[4], 'delai_execution': row[5],
            'validite_offre': row[6], 'inclusions': row[7], 'exclusions': row[8],
            'conditions': row[9], 'documents': row[10], 'statut': row[11],
            'date_creation': row[12], 'type_projet': row[14],
            'nom_client': row[15], 'numero_reference': row[16]
        })
    
    conn.close()
    return soumissions

def get_soumissions_pour_projet(lead_id: int) -> List[Dict]:
    """Récupère toutes les soumissions pour un projet"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, e.nom_entreprise, e.numero_rbq, e.certifications,
               COALESCE(AVG(ev.note), 0) as note_moyenne,
               COUNT(ev.note) as nombre_evaluations
        FROM soumissions s
        JOIN entrepreneurs e ON s.entrepreneur_id = e.id
        LEFT JOIN soumissions s2 ON s2.entrepreneur_id = e.id
        LEFT JOIN evaluations ev ON ev.soumission_id = s2.id AND ev.evaluateur_type = 'client'
        WHERE s.lead_id = ?
        GROUP BY s.id, e.nom_entreprise, e.numero_rbq, e.certifications
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
            'nom_entreprise': row[14],
            'numero_rbq': row[15],
            'certifications': row[16],
            'evaluations_moyenne': round(row[17], 1) if row[17] else 0,
            'nombre_evaluations': row[18]
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
        
        # Notifications de messages non lus et notifications générales
        if st.session_state.get('entrepreneur_connecte'):
            entrepreneur = st.session_state.entrepreneur_connecte
            conversations = get_conversations_entrepreneur(entrepreneur.id)
            total_non_lus = sum(conv['non_lus'] for conv in conversations)
            
            # Notifications générales
            notifs_non_lues = count_notifications_non_lues('entrepreneur', entrepreneur.id)
            
            if total_non_lus > 0:
                st.markdown(f"**💬 Messages non lus : {total_non_lus}**")
            
            if notifs_non_lues > 0:
                st.markdown(f"**🔔 Notifications : {notifs_non_lues}**")
                if st.button("📱 Voir notifications", key="voir_notifs_entrepreneur"):
                    st.session_state.mode_notifications = True
                    st.session_state.notif_type_utilisateur = 'entrepreneur'
                    st.session_state.notif_utilisateur_id = entrepreneur.id
                    st.rerun()
            
            if total_non_lus > 0 or notifs_non_lues > 0:
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
    
    # Vérifier si on est en mode notifications
    if st.session_state.get('mode_notifications', False):
        page_notifications()
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
            # Obtenir les informations d'urgence
            icone_urgence, couleur_urgence, libelle_urgence = get_couleur_urgence(projet['niveau_urgence'])
            jours_min = min(projet['jours_restants_soumissions'], projet['jours_restants_debut'])
            message_urgence = get_message_urgence(projet['niveau_urgence'], jours_min)
            
            with st.container():
                # Afficher un badge d'urgence visible
                if projet['niveau_urgence'] in ['critique', 'eleve']:
                    st.markdown(f"""
                        <div style="background-color: {couleur_urgence}; color: white; padding: 8px; border-radius: 4px; margin-bottom: 10px; text-align: center; font-weight: bold;">
                            {icone_urgence} {message_urgence}
                        </div>
                    """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{projet['type_projet']}** - {projet['code_postal']}")
                    st.caption(f"Budget: {projet['budget']} • Délai: {projet['delai_realisation']}")
                
                with col2:
                    st.caption(f"📋 {projet['nb_soumissions']} soumissions")
                
                with col3:
                    st.caption(f"📅 {projet['date_creation'][:10]}")
                
                with col4:
                    # Indicateur d'urgence compact
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 24px;">{icone_urgence}</span><br>
                            <small style="color: {couleur_urgence}; font-weight: bold;">{libelle_urgence}</small>
                        </div>
                    """, unsafe_allow_html=True)
                
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
            
            niveau_urgence = st.selectbox(
                "Niveau d'urgence",
                ["normal", "faible", "eleve", "critique"],
                format_func=lambda x: {
                    'faible': '🟢 Faible - Pas pressé',
                    'normal': '🟡 Normal - Dans les temps',
                    'eleve': '🟠 Élevé - Assez urgent',
                    'critique': '🔴 Critique - Très urgent'
                }[x],
                help="Indiquez le niveau d'urgence de votre projet"
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
        
        # Délais et échéances
        st.markdown("### ⏰ Délais et échéances")
        
        col1, col2 = st.columns(2)
        with col1:
            date_limite_soumissions = st.date_input(
                "Date limite pour recevoir les soumissions",
                value=datetime.date.today() + datetime.timedelta(days=14),
                min_value=datetime.date.today() + datetime.timedelta(days=1),
                help="Date après laquelle aucune nouvelle soumission ne sera acceptée"
            )
        
        with col2:
            date_debut_souhaite = st.date_input(
                "Date de début souhaitée des travaux",
                value=datetime.date.today() + datetime.timedelta(days=30),
                min_value=datetime.date.today() + datetime.timedelta(days=1),
                help="Date à laquelle vous souhaitez que les travaux commencent"
            )
        
        # Afficher un aperçu de l'urgence basé sur les dates sélectionnées
        if date_limite_soumissions and date_debut_souhaite:
            urgence_calculee = determiner_niveau_urgence_automatique(
                str(date_limite_soumissions), 
                str(date_debut_souhaite)
            )
            icone_calc, couleur_calc, libelle_calc = get_couleur_urgence(urgence_calculee)
            
            st.info(f"""
                **Urgence calculée automatiquement :** {icone_calc} {libelle_calc}
                
                Basé sur vos dates, le système recommande un niveau d'urgence **{libelle_calc.lower()}**.
                Vous pouvez ajuster manuellement ci-dessus si nécessaire.
            """)
        
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
                    date_limite_soumissions=str(date_limite_soumissions),
                    date_debut_souhaite=str(date_debut_souhaite),
                    niveau_urgence=niveau_urgence,
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
    
    # En-tête avec notifications
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("## 📋 Mes projets")
    
    with col2:
        # Afficher notifications si client connecté
        if 'client_email' in st.session_state:
            # Utiliser l'ID du premier projet comme référence client (pas optimal mais fonctionnel)
            projets = get_mes_projets(st.session_state.client_email)
            if projets:
                client_id = projets[0]['id']
                notifs_non_lues = count_notifications_non_lues('client', client_id)
                
                if notifs_non_lues > 0:
                    if st.button(f"🔔 Notifications ({notifs_non_lues})", key="voir_notifs_client"):
                        st.session_state.mode_notifications = True
                        st.session_state.notif_type_utilisateur = 'client'
                        st.session_state.notif_utilisateur_id = client_id
                        st.rerun()
    
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
    
    # Onglets pour séparer projets et dashboard
    tab1, tab2 = st.tabs(["📋 Mes projets", "📊 Dashboard"])
    
    with tab1:
        st.markdown("### 🏗️ Vos projets actifs")
        
        # Interface de filtrage pour les projets clients
        with st.expander("🔍 Filtres mes projets", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                recherche_client = st.text_input(
                    "🔍 Recherche",
                    placeholder="Description, type, référence...",
                    key="recherche_client_projets"
                )
                
                statut_client_filtre = st.selectbox(
                    "📊 Statut",
                    ["Tous", "Avec soumissions", "Sans soumissions", "Projet terminé"],
                    key="statut_client_filtre"
                )
            
            with col2:
                periode_client_filtre = st.selectbox(
                    "📅 Période",
                    ["Toutes", "Cette semaine", "Ce mois", "Ce trimestre"],
                    key="periode_client_filtre"
                )
                
                type_projet_client_filtre = st.selectbox(
                    "🏗️ Type de projet",
                    ["Tous", "Rénovation résidentielle", "Construction neuve", "Rénovation commerciale", 
                     "Toiture", "Plomberie", "Électricité", "Paysagement", "Autres"],
                    key="type_projet_client_filtre"
                )
            
            with col3:
                trier_projets_client = st.selectbox(
                    "📊 Trier par",
                    ["Date (plus récent)", "Date (plus ancien)", "Nb soumissions (décroissant)", "Nb soumissions (croissant)"],
                    key="tri_projets_client"
                )
        
        # Application des filtres
        projets_filtres = filtrer_mes_projets(
            email=email,
            statut=statut_client_filtre if statut_client_filtre != "Tous" else None,
            periode=periode_client_filtre if periode_client_filtre != "Toutes" else None,
            type_projet=type_projet_client_filtre if type_projet_client_filtre != "Tous" else None,
            recherche_texte=recherche_client if recherche_client else None
        )
        
        # Affichage des résultats
        st.markdown(f"**{len(projets_filtres)} projet(s) trouvé(s)**")
        
        # Afficher les projets filtrés
        for projet in projets_filtres:
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
                                    st.caption(f"{stars} {soum['evaluations_moyenne']}/5 ({soum['nombre_evaluations']} avis)")
                                else:
                                    st.caption("Aucune évaluation encore")
                            
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
                                        
                                        # Créer notification pour l'entrepreneur
                                        notifier_soumission_acceptee(soum['id'])
                                        
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
                                        
                                        # Créer notification pour l'entrepreneur
                                        notifier_soumission_refusee(soum['id'])
                                        
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
                            
                            # Section évaluation (visible seulement si soumission acceptée)
                            if soum['statut'] == 'acceptee':
                                st.markdown("---")
                                st.markdown("### ⭐ Évaluer cet entrepreneur")
                                
                                # Vérifier si déjà évalué
                                evaluation_existante = get_evaluation_soumission(soum['id'], 'client')
                                
                                if evaluation_existante:
                                    st.success(f"✅ Vous avez déjà évalué : {evaluation_existante['note']}/5 ⭐")
                                    if evaluation_existante['commentaire']:
                                        st.info(f"💬 Votre commentaire : {evaluation_existante['commentaire']}")
                                else:
                                    with st.form(f"evaluation_{soum['id']}"):
                                        col_eval1, col_eval2 = st.columns([1, 2])
                                        
                                        with col_eval1:
                                            note = st.selectbox(
                                                "Note sur 5",
                                                options=[5, 4, 3, 2, 1],
                                                format_func=lambda x: f"{x} ⭐" + (" - Excellent" if x==5 else " - Très bon" if x==4 else " - Correct" if x==3 else " - Moyen" if x==2 else " - Décevant"),
                                                key=f"note_{soum['id']}"
                                            )
                                        
                                        with col_eval2:
                                            commentaire = st.text_area(
                                                "Commentaire (optionnel)",
                                                placeholder="Décrivez votre expérience avec cet entrepreneur...",
                                                height=100,
                                                key=f"comment_{soum['id']}"
                                            )
                                        
                                        if st.form_submit_button("📝 Publier l'évaluation", type="primary"):
                                            if ajouter_evaluation(soum['id'], 'client', note, commentaire):
                                                st.success("✅ Évaluation publiée avec succès!")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("❌ Erreur lors de la publication de l'évaluation")
                        
                        st.markdown("---")
    
    with tab2:
        st.markdown("### 📊 Tableau de bord client")
        
        # Récupérer les statistiques
        stats = get_stats_client(email)
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projets publiés", stats['nb_projets'])
        
        with col2:
            st.metric("Soumissions reçues", stats['total_soumissions'])
        
        with col3:
            st.metric("Soumissions acceptées", stats['soumissions_acceptees'])
        
        with col4:
            st.metric("Taux d'acceptation", f"{stats['taux_acceptation']}%")
        
        st.markdown("---")
        
        # Statistiques détaillées
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Analyse financière")
            if stats['montant_moyen_soumissions'] > 0:
                st.metric("Montant moyen des soumissions", f"{stats['montant_moyen_soumissions']:,.2f} $")
                st.metric("Soumissions par projet (moyenne)", stats['moy_soumissions_par_projet'])
            else:
                st.info("Aucune soumission reçue encore")
        
        with col2:
            st.markdown("### 📈 Performance")
            if stats['evolution_mensuelle']:
                st.markdown("**Évolution mensuelle :**")
                for mois, nb_projets, nb_soumissions in stats['evolution_mensuelle'][:3]:
                    st.write(f"**{mois}** : {nb_projets} projet(s), {nb_soumissions} soumission(s)")
            else:
                st.info("Pas encore d'historique disponible")
        
        # Conseils et recommandations
        st.markdown("---")
        st.markdown("### 💡 Recommandations")
        
        if stats['nb_projets'] == 0:
            st.info("🚀 Commencez par publier votre premier appel d'offres !")
        elif stats['total_soumissions'] == 0:
            st.warning("📢 Vos projets n'ont pas encore reçu de soumissions. Vérifiez vos descriptions et budgets.")
        elif stats['taux_acceptation'] < 50 and stats['soumissions_acceptees'] > 0:
            st.warning("⚡ Votre taux d'acceptation est bas. Considérez réviser vos critères de sélection.")
        else:
            st.success("✅ Excellent ! Votre utilisation de SEAOP est optimale.")

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
        projet = get_mes_projets("dummy")[0] if get_mes_projets("dummy") else None
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
                        # Créer notification pour le destinataire
                        notifier_nouveau_message(lead_id, entrepreneur_id, expediteur_type)
                        
                        st.success("Message envoyé!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de l'envoi du message")
                else:
                    st.warning("Veuillez saisir un message")

def page_notifications():
    """Centre de notifications"""
    if 'mode_notifications' not in st.session_state or not st.session_state.mode_notifications:
        return
    
    type_utilisateur = st.session_state.get('notif_type_utilisateur')
    utilisateur_id = st.session_state.get('notif_utilisateur_id')
    
    if not type_utilisateur or not utilisateur_id:
        st.error("Erreur: informations de notification manquantes")
        return
    
    # En-tête
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        st.markdown("## 🔔 Centre de notifications")
    
    with col2:
        if st.button("✅ Tout marquer lu", key="marquer_tout_lu"):
            if marquer_toutes_notifications_lues(type_utilisateur, utilisateur_id):
                st.success("Toutes les notifications marquées comme lues")
                st.rerun()
    
    with col3:
        if st.button("❌ Fermer", key="fermer_notifications"):
            st.session_state.mode_notifications = False
            for key in ['notif_type_utilisateur', 'notif_utilisateur_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Récupérer les notifications
    notifications = get_notifications_utilisateur(type_utilisateur, utilisateur_id, 20)
    
    if not notifications:
        st.info("🎉 Aucune notification pour le moment !")
    else:
        st.markdown(f"📋 **{len(notifications)} notification(s)**")
        st.markdown("---")
        
        for notif in notifications:
            # Style différent pour les notifications non lues
            if not notif['lu']:
                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196F3;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{notif['titre']}</strong><br>
                            {notif['message']}<br>
                            <small style="color: #666;">{notif['date_creation'][:16] if notif['date_creation'] else ""}</small>
                        </div>
                        <div>
                            <span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">NOUVEAU</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Bouton pour marquer comme lu
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("✅ Lu", key=f"marquer_lu_{notif['id']}"):
                        if marquer_notification_lue(notif['id']):
                            st.rerun()
            else:
                st.markdown(f"""
                <div style="background-color: #F5F5F5; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <div>
                        <strong>{notif['titre']}</strong><br>
                        {notif['message']}<br>
                        <small style="color: #666;">{notif['date_creation'][:16] if notif['date_creation'] else ""}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")

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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Projets disponibles", "📋 Mes soumissions", "⭐ Mes évaluations", "📊 Dashboard", "👤 Mon profil"])
        
        with tab1:
            st.markdown("### 🔍 Projets disponibles pour soumission")
            
            # Interface de filtrage
            with st.expander("🔍 Filtres de recherche", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    recherche_texte = st.text_input(
                        "🔍 Recherche textuelle",
                        placeholder="Mots-clés dans la description...",
                        key="recherche_projets"
                    )
                    
                    type_projet_filtre = st.selectbox(
                        "🏗️ Type de projet",
                        ["Tous", "Rénovation résidentielle", "Construction neuve", "Rénovation commerciale", 
                         "Toiture", "Plomberie", "Électricité", "Paysagement", "Autres"],
                        key="type_projet_filtre"
                    )
                
                with col2:
                    code_postal_filtre = st.text_input(
                        "📍 Code postal (début)",
                        placeholder="Ex: H1A, G1V...",
                        key="code_postal_filtre"
                    )
                    
                    budget_range = st.select_slider(
                        "💰 Gamme de budget",
                        options=["Tous", "< 5K", "5K-15K", "15K-50K", "50K-100K", "> 100K"],
                        value="Tous",
                        key="budget_range_filtre"
                    )
                
                with col3:
                    delai_filtre = st.selectbox(
                        "⏰ Délai souhaité",
                        ["Tous", "Urgent (< 1 mois)", "Court (1-3 mois)", "Normal (3-6 mois)", "Long (> 6 mois)"],
                        key="delai_filtre"
                    )
                    
                    trier_par = st.selectbox(
                        "📊 Trier par",
                        ["Date (plus récent)", "Date (plus ancien)", "Budget (croissant)", "Budget (décroissant)", "Nb soumissions"],
                        key="tri_projets"
                    )
            
            # Application des filtres
            budget_min, budget_max = None, None
            if budget_range != "Tous":
                if budget_range == "< 5K":
                    budget_max = 5000
                elif budget_range == "5K-15K":
                    budget_min, budget_max = 5000, 15000
                elif budget_range == "15K-50K":
                    budget_min, budget_max = 15000, 50000
                elif budget_range == "50K-100K":
                    budget_min, budget_max = 50000, 100000
                elif budget_range == "> 100K":
                    budget_min = 100000
            
            # Récupération des projets filtrés
            projets = filtrer_projets_pour_entrepreneurs(
                type_projet=type_projet_filtre if type_projet_filtre != "Tous" else None,
                budget_min=budget_min,
                budget_max=budget_max,
                code_postal=code_postal_filtre if code_postal_filtre else None,
                recherche_texte=recherche_texte if recherche_texte else None
            )
            
            # Affichage des résultats
            st.markdown(f"**{len(projets)} projet(s) trouvé(s)**")
            
            if not projets:
                st.info("Aucun projet ne correspond à vos critères. Essayez d'ajuster les filtres.")
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
                                            # Créer notification pour le client
                                            notifier_nouvelle_soumission(projet['id'])
                                            
                                            st.success("✅ Soumission envoyée avec succès!")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Erreur lors de l'envoi")
                                    else:
                                        st.error("❌ Veuillez remplir tous les champs obligatoires")
        
        with tab2:
            st.markdown("### 📋 Mes soumissions")
            
            # Interface de filtrage pour les soumissions
            with st.expander("🔍 Filtres mes soumissions", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    statut_filtre = st.selectbox(
                        "📊 Statut",
                        ["Tous", "envoyee", "acceptee", "refusee"],
                        format_func=lambda x: {"Tous": "Tous", "envoyee": "En attente", "acceptee": "Acceptée", "refusee": "Refusée"}[x],
                        key="statut_soumissions_filtre"
                    )
                
                with col2:
                    periode_filtre = st.selectbox(
                        "📅 Période",
                        ["Toutes", "Ce mois", "Ce trimestre", "Cette année"],
                        key="periode_soumissions_filtre"
                    )
                
                with col3:
                    col3a, col3b = st.columns(2)
                    with col3a:
                        montant_min = st.number_input(
                            "💰 Montant min ($)",
                            min_value=0,
                            value=0,
                            step=1000,
                            key="montant_min_filtre"
                        )
                    with col3b:
                        montant_max = st.number_input(
                            "💰 Montant max ($)",
                            min_value=0,
                            value=0,
                            step=1000,
                            key="montant_max_filtre"
                        )
            
            # Application des filtres
            mes_soumissions = filtrer_soumissions_entrepreneur(
                entrepreneur_id=entrepreneur.id,
                statut=statut_filtre if statut_filtre != "Tous" else None,
                periode=periode_filtre if periode_filtre != "Toutes" else None,
                montant_min=montant_min if montant_min > 0 else None,
                montant_max=montant_max if montant_max > 0 else None
            )
            
            # Affichage des résultats
            st.markdown(f"**{len(mes_soumissions)} soumission(s) trouvée(s)**")
            
            if not mes_soumissions:
                if statut_filtre != "Tous" or periode_filtre != "Toutes" or montant_min > 0 or montant_max > 0:
                    st.info("Aucune soumission ne correspond à vos critères")
                else:
                    st.info("Vous n'avez pas encore envoyé de soumissions")
            else:
                for soum in mes_soumissions:
                    statut_emoji = {
                        'envoyee': '📤',
                        'vue': '👁️',
                        'acceptee': '✅',
                        'refusee': '❌'
                    }
                    
                    with st.expander(f"{statut_emoji.get(soum['statut'], '📋')} {soum['type_projet']} - {soum['nom_client']} - {soum['montant']:,.2f}$"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Client:** {soum['nom_client']}")
                            st.write(f"**Projet:** {soum['type_projet']}")
                            st.write(f"**Référence:** {soum['numero_reference']}")
                            st.write(f"**Délai proposé:** {soum['delai_execution']}")
                        
                        with col2:
                            st.write(f"**Ma soumission:** {soum['montant']:,.2f}$")
                            st.write(f"**Statut:** {soum['statut'].capitalize()}")
                            st.write(f"**Date:** {soum['date_creation'][:10]}")
                        
                        if soum['statut'] == 'acceptee':
                            st.success("🎉 Félicitations! Votre soumission a été acceptée!")
                            st.info(f"Contactez le client pour finaliser les détails")
                        elif soum['statut'] == 'refusee':
                            st.error("Cette soumission n'a pas été retenue")
        
        with tab3:
            st.markdown("### ⭐ Mes évaluations clients")
            
            # Récupérer les statistiques d'évaluation
            stats_eval = get_evaluations_entrepreneur(entrepreneur.id)
            
            # Affichage des statistiques générales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Note moyenne", f"{stats_eval['note_moyenne']}/5" if stats_eval['note_moyenne'] > 0 else "Aucune", 
                         f"⭐" * int(stats_eval['note_moyenne']) if stats_eval['note_moyenne'] > 0 else "")
            
            with col2:
                st.metric("Total évaluations", stats_eval['nombre_evaluations'])
            
            with col3:
                st.metric("Évaluations positives", f"{stats_eval['evaluations_positives']}")
            
            with col4:
                st.metric("% de satisfaction", f"{stats_eval['pourcentage_positif']}%")
            
            if stats_eval['nombre_evaluations'] > 0:
                st.markdown("---")
                st.markdown("### 💬 Derniers commentaires clients")
                
                commentaires = get_derniers_commentaires_entrepreneur(entrepreneur.id)
                
                if commentaires:
                    for commentaire in commentaires:
                        with st.container():
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                stars = "⭐" * commentaire['note']
                                st.markdown(f"**{stars}**")
                                st.caption(f"{commentaire['date_evaluation']}")
                                st.caption(f"Projet: {commentaire['type_projet']}")
                            
                            with col2:
                                st.markdown(f"*\"{commentaire['commentaire']}\"*")
                            
                            st.markdown("---")
                else:
                    st.info("Aucun commentaire détaillé encore")
            else:
                st.info("Aucune évaluation reçue pour le moment. Continuez à fournir un excellent service pour recevoir vos premières évaluations !")
        
        with tab4:
            st.markdown("### 📊 Tableau de bord entrepreneur")
            
            # Récupérer les statistiques
            stats = get_stats_entrepreneur(entrepreneur.id)
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Soumissions envoyées", stats['total_soumissions'])
            
            with col2:
                st.metric("Projets remportés", stats['soumissions_acceptees'], 
                         f"{stats['taux_succes']}%" if stats['taux_succes'] > 0 else "0%")
            
            with col3:
                st.metric("Chiffre d'affaires", f"{stats['ca_total']:,.2f} $")
            
            with col4:
                st.metric("Note moyenne", f"{stats['note_moyenne']}/5 ⭐" if stats['note_moyenne'] > 0 else "Aucune note")
            
            st.markdown("---")
            
            # Statistiques détaillées
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💰 Performance financière")
                if stats['total_soumissions'] > 0:
                    st.metric("Montant moyen par soumission", f"{stats['montant_moyen']:,.2f} $")
                    st.metric("Taux de succès", f"{stats['taux_succes']}%")
                    if stats['taux_succes'] >= 70:
                        st.success("🎯 Excellent taux de succès !")
                    elif stats['taux_succes'] >= 40:
                        st.warning("⚡ Taux de succès moyen")
                    else:
                        st.info("💪 Continuez vos efforts !")
                else:
                    st.info("Aucune soumission envoyée encore")
            
            with col2:
                st.markdown("### 📈 Évolution mensuelle")
                if stats['evolution_mensuelle']:
                    st.markdown("**Activité récente :**")
                    for mois, nb_soumissions, nb_acceptees, ca_mois in stats['evolution_mensuelle'][:3]:
                        taux_mois = round((nb_acceptees / nb_soumissions * 100), 1) if nb_soumissions > 0 else 0
                        st.write(f"**{mois}** : {nb_soumissions} soumission(s), {nb_acceptees} acceptée(s) ({taux_mois}%)")
                        if ca_mois > 0:
                            st.write(f"   💰 CA: {ca_mois:,.2f} $")
                else:
                    st.info("Pas encore d'historique disponible")
            
            # Conseils et recommandations
            st.markdown("---")
            st.markdown("### 💡 Recommandations pour améliorer vos performances")
            
            if stats['total_soumissions'] == 0:
                st.info("🚀 Commencez par soumissionner sur vos premiers projets !")
            elif stats['taux_succes'] < 30:
                st.warning("📝 Votre taux de succès est bas. Considérez :")
                st.write("- Réviser vos prix pour être plus compétitif")
                st.write("- Améliorer la qualité de vos descriptions")
                st.write("- Cibler des projets plus adaptés à votre expertise")
            elif stats['note_moyenne'] > 0 and stats['note_moyenne'] < 3.5:
                st.warning("⭐ Votre note moyenne est perfectible. Focalisez sur :")
                st.write("- La qualité de votre service client")
                st.write("- Le respect des délais annoncés")
                st.write("- La communication avec vos clients")
            else:
                st.success("✅ Excellente performance ! Continuez sur cette lancée.")
                if stats['nb_evaluations'] < 5:
                    st.info("💬 Encouragez vos clients à vous évaluer pour augmenter votre visibilité.")
        
        with tab5:
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
        
        # Dashboard administrateur avec onglets
        tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "👥 Gestion des entrepreneurs", "📋 Gestion des soumissions"])
        
        with tab1:
            st.markdown("### 📊 Statistiques globales de SEAOP")
            
            # Récupérer les statistiques complètes
            stats = get_stats_admin()
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total projets", stats['total_projets'])
            with col2:
                st.metric("Entrepreneurs inscrits", stats['total_entrepreneurs'])
            with col3:
                st.metric("Soumissions envoyées", stats['total_soumissions'])
            with col4:
                st.metric("Volume d'affaires", f"{stats['ca_total']:,.2f} $")
            
            st.markdown("---")
            
            # Top entrepreneurs du mois
            st.markdown("### 🏆 Top entrepreneurs du mois")
            if stats['top_entrepreneurs']:
                for i, (nom, nb_soum, nb_acc, ca, note) in enumerate(stats['top_entrepreneurs'], 1):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                        st.write(f"{medal} **{nom}**")
                    with col2:
                        st.write(f"{nb_acc}/{nb_soum} projets")
                    with col3:
                        st.write(f"{ca:,.0f} $" if ca else "0 $")
                    with col4:
                        st.write(f"⭐ {note:.1f}" if note else "Pas de note")
            else:
                st.info("Aucune activité ce mois-ci")
            
            # Évolution de la plateforme
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Évolution des projets")
                if stats['evolution_projets']:
                    for mois, nb_projets in stats['evolution_projets'][:6]:
                        st.write(f"**{mois}** : {nb_projets} projet(s)")
                else:
                    st.info("Pas d'historique disponible")
            
            with col2:
                st.markdown("### 💰 Évolution du chiffre d'affaires")
                if stats['evolution_soumissions']:
                    for mois, nb_soum, ca in stats['evolution_soumissions'][:6]:
                        st.write(f"**{mois}** : {nb_soum} soumission(s)")
                        if ca > 0:
                            st.write(f"   💰 {ca:,.2f} $")
                else:
                    st.info("Pas d'historique disponible")
        
        with tab2:
            st.markdown("### 👥 Gestion des entrepreneurs")
            
            # Afficher le tableau des entrepreneurs
            conn = sqlite3.connect(DATABASE_PATH)
            df_entrepreneurs = pd.read_sql_query('''
                SELECT id, nom_entreprise, email, numero_rbq, abonnement, date_inscription
                FROM entrepreneurs
                ORDER BY date_inscription DESC
            ''', conn)
            conn.close()
            
            st.dataframe(df_entrepreneurs, use_container_width=True)
            
            # Statistiques des entrepreneurs
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                actifs_ce_mois = len([e for e in stats['top_entrepreneurs'] if e[1] > 0])
                st.metric("Entrepreneurs actifs ce mois", actifs_ce_mois)
            
            with col2:
                if df_entrepreneurs is not None and len(df_entrepreneurs) > 0:
                    nouveaux_ce_mois = len(df_entrepreneurs[df_entrepreneurs['date_inscription'].str.startswith(datetime.datetime.now().strftime('%Y-%m'))])
                    st.metric("Nouveaux ce mois", nouveaux_ce_mois)
                else:
                    st.metric("Nouveaux ce mois", 0)
            
            with col3:
                # Calcul de la note moyenne globale
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT AVG(note) FROM evaluations WHERE evaluateur_type = "client"')
                note_moyenne_globale = cursor.fetchone()[0] or 0
                conn.close()
                st.metric("Note moyenne plateforme", f"{note_moyenne_globale:.1f}/5 ⭐" if note_moyenne_globale > 0 else "Aucune")
        
        with tab3:
            st.markdown("### 📋 Gestion des soumissions et projets")
            
            # Afficher le tableau des projets d'abord
            st.markdown("#### 🏗️ Projets récents")
            conn = sqlite3.connect(DATABASE_PATH)
            df_projets = pd.read_sql_query('''
                SELECT id, numero_reference, nom, type_projet, budget, statut, date_creation
                FROM leads
                ORDER BY date_creation DESC
                LIMIT 10
            ''', conn)
            conn.close()
            
            st.dataframe(df_projets, use_container_width=True)
            
            st.markdown("#### 📊 Soumissions récentes")
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

# ================== SYSTÈME DE DÉLAIS/URGENCE ==================

def calculer_jours_restants(date_limite: str) -> int:
    """Calcule le nombre de jours restants jusqu'à une date limite"""
    if not date_limite:
        return 999  # Pas de limite définie
    
    try:
        date_limite_obj = datetime.datetime.strptime(date_limite, '%Y-%m-%d').date()
        aujourd_hui = datetime.date.today()
        jours_restants = (date_limite_obj - aujourd_hui).days
        return jours_restants
    except:
        return 999

def determiner_niveau_urgence_automatique(date_limite_soumissions: str, date_debut_souhaite: str) -> str:
    """Détermine automatiquement le niveau d'urgence basé sur les délais"""
    jours_soumissions = calculer_jours_restants(date_limite_soumissions)
    jours_debut = calculer_jours_restants(date_debut_souhaite)
    
    # Urgence basée sur les délais les plus courts
    jours_min = min(jours_soumissions, jours_debut)
    
    if jours_min < 0:
        return 'critique'  # Échéance dépassée
    elif jours_min <= 3:
        return 'critique'  # Moins de 3 jours
    elif jours_min <= 7:
        return 'eleve'     # Moins d'une semaine
    elif jours_min <= 14:
        return 'normal'    # Moins de 2 semaines
    else:
        return 'faible'    # Plus de 2 semaines

def get_couleur_urgence(niveau_urgence: str) -> tuple:
    """Retourne la couleur et l'icône pour un niveau d'urgence"""
    couleurs = {
        'faible': ('🟢', '#28a745', 'Faible'),
        'normal': ('🟡', '#ffc107', 'Normal'),
        'eleve': ('🟠', '#fd7e14', 'Élevé'),
        'critique': ('🔴', '#dc3545', 'Critique')
    }
    return couleurs.get(niveau_urgence, couleurs['normal'])

def get_message_urgence(niveau_urgence: str, jours_restants: int) -> str:
    """Génère un message d'urgence approprié"""
    if niveau_urgence == 'critique':
        if jours_restants < 0:
            return f"⚠️ ÉCHÉANCE DÉPASSÉE de {abs(jours_restants)} jour(s) !"
        else:
            return f"🚨 URGENT - Plus que {jours_restants} jour(s) !"
    elif niveau_urgence == 'eleve':
        return f"⚡ PRIORITAIRE - {jours_restants} jour(s) restant(s)"
    elif niveau_urgence == 'normal':
        return f"📅 {jours_restants} jour(s) restant(s)"
    else:
        return f"✅ {jours_restants} jour(s) - Délai confortable"

def mettre_a_jour_urgence_projet(projet_id: int):
    """Met à jour automatiquement le niveau d'urgence d'un projet"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Récupérer les dates du projet
    cursor.execute('''
        SELECT date_limite_soumissions, date_debut_souhaite, niveau_urgence
        FROM leads WHERE id = ?
    ''', (projet_id,))
    
    result = cursor.fetchone()
    if result:
        date_limite_soumissions, date_debut_souhaite, niveau_actuel = result
        
        # Calculer le nouveau niveau d'urgence
        nouveau_niveau = determiner_niveau_urgence_automatique(date_limite_soumissions, date_debut_souhaite)
        
        # Mettre à jour seulement si le niveau a changé
        if nouveau_niveau != niveau_actuel:
            cursor.execute('''
                UPDATE leads SET niveau_urgence = ? WHERE id = ?
            ''', (nouveau_niveau, projet_id))
            conn.commit()
            
            # Créer une notification si l'urgence augmente
            if niveau_actuel in ['faible', 'normal'] and nouveau_niveau in ['eleve', 'critique']:
                notifier_urgence_projet(projet_id, nouveau_niveau)
    
    conn.close()

def notifier_urgence_projet(projet_id: int, niveau_urgence: str):
    """Crée des notifications d'urgence pour un projet"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Récupérer les infos du projet
    cursor.execute('''
        SELECT nom, email, type_projet, numero_reference, date_limite_soumissions
        FROM leads WHERE id = ?
    ''', (projet_id,))
    
    projet = cursor.fetchone()
    if not projet:
        conn.close()
        return
    
    nom_client, email_client, type_projet, numero_ref, date_limite = projet
    jours_restants = calculer_jours_restants(date_limite)
    
    # Message selon le niveau d'urgence
    if niveau_urgence == 'critique':
        titre = f"🚨 URGENT - Projet {numero_ref}"
        message = f"Le projet '{type_projet}' arrive à échéance dans {jours_restants} jour(s) !"
    else:
        titre = f"⚡ PRIORITAIRE - Projet {numero_ref}"
        message = f"Le projet '{type_projet}' nécessite une attention prioritaire"
    
    # Notifier le client
    cursor.execute('''
        INSERT INTO notifications (utilisateur_type, utilisateur_id, type_notification, 
                                 titre, message, lien_id)
        VALUES ('client', ?, 'urgence_projet', ?, ?, ?)
    ''', (projet_id, titre, message, projet_id))
    
    # Notifier tous les entrepreneurs qui ont soumissionné
    cursor.execute('''
        SELECT DISTINCT entrepreneur_id FROM soumissions WHERE lead_id = ?
    ''', (projet_id,))
    
    entrepreneurs = cursor.fetchall()
    for (entrepreneur_id,) in entrepreneurs:
        cursor.execute('''
            INSERT INTO notifications (utilisateur_type, utilisateur_id, type_notification, 
                                     titre, message, lien_id)
            VALUES ('entrepreneur', ?, 'urgence_projet', ?, ?, ?)
        ''', (entrepreneur_id, titre, f"Projet urgent : {message}", projet_id))
    
    conn.commit()
    conn.close()

def get_projets_par_urgence() -> Dict[str, List[Dict]]:
    """Récupère tous les projets groupés par niveau d'urgence"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*, 
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id) as nb_soumissions,
               (SELECT COUNT(*) FROM soumissions s WHERE s.lead_id = l.id AND s.statut = 'acceptee') as nb_acceptees
        FROM leads l
        WHERE l.visible_entrepreneurs = 1 AND l.accepte_soumissions = 1
        ORDER BY 
            CASE l.niveau_urgence 
                WHEN 'critique' THEN 1 
                WHEN 'eleve' THEN 2 
                WHEN 'normal' THEN 3 
                WHEN 'faible' THEN 4 
            END,
            l.date_limite_soumissions ASC
    ''')
    
    projets_par_urgence = {
        'critique': [],
        'eleve': [],
        'normal': [],
        'faible': []
    }
    
    for row in cursor.fetchall():
        projet = {
            'id': row[0], 'nom': row[1], 'email': row[2], 'telephone': row[3],
            'code_postal': row[4], 'type_projet': row[5], 'description': row[6],
            'budget': row[7], 'delai_realisation': row[8], 'photos': row[9],
            'plans': row[10], 'documents': row[11], 'date_creation': row[12],
            'statut': row[13], 'numero_reference': row[14],
            'visible_entrepreneurs': row[15], 'accepte_soumissions': row[16],
            'date_limite_soumissions': row[17], 'date_debut_souhaite': row[18],
            'niveau_urgence': row[19], 'nb_soumissions': row[20], 'nb_acceptees': row[21]
        }
        
        # Calculer les jours restants
        projet['jours_restants_soumissions'] = calculer_jours_restants(projet['date_limite_soumissions'])
        projet['jours_restants_debut'] = calculer_jours_restants(projet['date_debut_souhaite'])
        
        # Mettre à jour l'urgence automatiquement
        mettre_a_jour_urgence_projet(projet['id'])
        
        niveau = projet['niveau_urgence']
        if niveau in projets_par_urgence:
            projets_par_urgence[niveau].append(projet)
    
    conn.close()
    return projets_par_urgence

if __name__ == "__main__":
    main()