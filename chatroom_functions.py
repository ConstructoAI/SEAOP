#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions pour le Chat Room Public SEAOP
"""

import streamlit as st
import sqlite3
import datetime
import os

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '.')
DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def page_chat_room_public():
    """Page Chat Room Public - Style commentaires Facebook"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💬 Chat Room SEAOP</h1>
        <p>Espace de discussion communautaire pour clients et entrepreneurs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Connexion à la base de données
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Créer les tables si elles n'existent pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_room (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL,
            user_id INTEGER,
            message TEXT NOT NULL,
            parent_id INTEGER,
            likes INTEGER DEFAULT 0,
            is_pinned BOOLEAN DEFAULT 0,
            is_deleted BOOLEAN DEFAULT 0,
            deleted_by TEXT,
            edited BOOLEAN DEFAULT 0,
            edited_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_badge TEXT,
            FOREIGN KEY (parent_id) REFERENCES chat_room (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_room_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES chat_room (id),
            UNIQUE(message_id, user_email)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_room_online (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_typing BOOLEAN DEFAULT 0,
            UNIQUE(user_email)
        )
    ''')
    
    conn.commit()
    
    # Identifier l'utilisateur actuel
    user_type = "visiteur"
    user_name = "Visiteur"
    user_email = ""
    user_id = None
    user_badge = None
    
    # Vérifier si entrepreneur connecté
    if st.session_state.get('entrepreneur_connecte'):
        entrepreneur = st.session_state.entrepreneur_connecte
        user_type = "entrepreneur"
        user_name = f"{entrepreneur.nom_contact} - {entrepreneur.nom_entreprise}"
        user_email = entrepreneur.email
        user_id = entrepreneur.id
        # Déterminer le badge
        if entrepreneur.abonnement == "premium":
            user_badge = "premium"
        elif entrepreneur.numero_rbq:
            user_badge = "verified"
    # Sinon vérifier si client (par email en session)
    elif st.session_state.get('client_email'):
        user_type = "client"
        user_email = st.session_state.client_email
        user_name = st.session_state.get('client_nom', user_email.split('@')[0])
    
    # Mise à jour statut en ligne
    if user_email:
        cursor.execute('''
            INSERT OR REPLACE INTO chat_room_online 
            (user_type, user_name, user_email, last_seen) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_type, user_name, user_email))
        conn.commit()
    
    # Layout en colonnes
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        st.markdown("### 👥 En ligne")
        
        # Récupérer utilisateurs en ligne (actifs dans les 5 dernières minutes)
        cursor.execute('''
            SELECT user_type, user_name, user_email
            FROM chat_room_online
            WHERE datetime(last_seen) > datetime('now', '-5 minutes')
            ORDER BY last_seen DESC
            LIMIT 20
        ''')
        online_users = cursor.fetchall()
        
        if online_users:
            for u_type, u_name, u_email in online_users:
                if u_type == "admin":
                    st.markdown(f"🔴 **{u_name}**")
                elif u_type == "entrepreneur":
                    st.markdown(f"🟢 {u_name}")
                else:
                    st.markdown(f"⚪ {u_name}")
        else:
            st.info("Soyez le premier en ligne!")
        
        st.markdown("---")
        st.markdown("### 📊 Stats")
        
        # Stats du chat
        cursor.execute("SELECT COUNT(*) FROM chat_room WHERE is_deleted = 0")
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_email) FROM chat_room")
        total_participants = cursor.fetchone()[0]
        
        st.metric("Messages", total_messages)
        st.metric("Participants", total_participants)
        
        # Bouton rafraîchir
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    
    with col_main:
        # Zone de saisie de message en haut
        if user_email:
            st.success(f"✅ Connecté en tant que: **{user_name}**")
            
            with st.form("new_message_form", clear_on_submit=True):
                message_input = st.text_area(
                    "💬 Votre message",
                    placeholder="Partagez vos questions, conseils ou expériences...",
                    height=80,
                    key="chat_message_input"
                )
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col3:
                    submit_button = st.form_submit_button("📤 Envoyer", use_container_width=True, type="primary")
                
                if submit_button and message_input:
                    # Insérer le message
                    cursor.execute('''
                        INSERT INTO chat_room 
                        (user_type, user_name, user_email, user_id, message, user_badge)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_type, user_name, user_email, user_id, message_input, user_badge))
                    conn.commit()
                    st.success("✅ Message publié!")
                    st.rerun()
        else:
            # Formulaire d'identification pour visiteurs
            st.info("👋 **Identifiez-vous pour participer**")
            
            with st.form("identify_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nom_visiteur = st.text_input("Votre nom *")
                with col2:
                    email_visiteur = st.text_input("Votre email *")
                
                submit_id = st.form_submit_button("✅ Participer à la discussion", use_container_width=True, type="primary")
                
                if submit_id:
                    if nom_visiteur and email_visiteur:
                        st.session_state.client_email = email_visiteur
                        st.session_state.client_nom = nom_visiteur
                        st.success("✅ Bienvenue dans la discussion!")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")
        
        st.markdown("---")
        
        # Affichage des messages
        st.markdown("### 📝 Messages récents")
        
        # Messages épinglés d'abord
        cursor.execute('''
            SELECT id, user_type, user_name, user_email, message, likes, 
                   created_at, user_badge, is_pinned
            FROM chat_room
            WHERE is_deleted = 0 AND is_pinned = 1
            ORDER BY created_at DESC
        ''')
        pinned_messages = cursor.fetchall()
        
        if pinned_messages:
            for msg in pinned_messages:
                display_chat_message(msg, cursor, conn, user_email, is_pinned=True)
            st.markdown("---")
        
        # Messages normaux
        cursor.execute('''
            SELECT id, user_type, user_name, user_email, message, likes, 
                   created_at, user_badge, is_pinned
            FROM chat_room
            WHERE is_deleted = 0 AND is_pinned = 0
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        messages = cursor.fetchall()
        
        if messages:
            for msg in messages:
                display_chat_message(msg, cursor, conn, user_email)
        else:
            st.info("💬 Aucun message pour le moment. Soyez le premier à écrire!")
    
    conn.close()

def display_chat_message(msg, cursor, conn, current_user_email, is_pinned=False):
    """Affiche un message du chat avec style Facebook"""
    msg_id, u_type, u_name, u_email, message, likes, created_at, badge, _ = msg
    
    # Container pour le message
    with st.container():
        # Créer un style de boîte pour le message
        bg_color = "#FFF4E6" if is_pinned else "#F8F9FA"
        border_color = "#FFA500" if is_pinned else "#DEE2E6"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; border: 1px solid {border_color}; 
                    border-radius: 10px; padding: 15px; margin-bottom: 10px;">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Nom avec badge et type
            name_display = f"**{u_name}**"
            if badge == "admin":
                name_display += " 👑 Admin"
            elif badge == "verified":
                name_display += " ✅ Vérifié RBQ"
            elif badge == "premium":
                name_display += " ⭐ Premium"
            elif u_type == "entrepreneur":
                name_display += " 🔨 Entrepreneur"
            elif u_type == "client":
                name_display += " 🏠 Client"
            
            # Date formatée
            try:
                date_obj = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                time_diff = datetime.datetime.now() - date_obj
                if time_diff.days > 0:
                    time_str = f"il y a {time_diff.days}j"
                elif time_diff.seconds > 3600:
                    time_str = f"il y a {time_diff.seconds // 3600}h"
                elif time_diff.seconds > 60:
                    time_str = f"il y a {time_diff.seconds // 60}m"
                else:
                    time_str = "à l'instant"
            except:
                time_str = created_at
            
            st.markdown(f"{name_display} · *{time_str}*")
            
            # Message avec style
            if is_pinned:
                st.info(f"📌 **Message épinglé:** {message}")
            else:
                st.markdown(f"{message}")
        
        with col2:
            # Actions
            if current_user_email:
                # Vérifier si déjà liké
                cursor.execute('''
                    SELECT COUNT(*) FROM chat_room_likes 
                    WHERE message_id = ? AND user_email = ?
                ''', (msg_id, current_user_email))
                already_liked = cursor.fetchone()[0] > 0
                
                like_label = f"👍 {likes}" if likes > 0 else "👍"
                
                if not already_liked:
                    if st.button(like_label, key=f"like_{msg_id}"):
                        cursor.execute('''
                            INSERT INTO chat_room_likes (message_id, user_email)
                            VALUES (?, ?)
                        ''', (msg_id, current_user_email))
                        cursor.execute('''
                            UPDATE chat_room SET likes = likes + 1 WHERE id = ?
                        ''', (msg_id,))
                        conn.commit()
                        st.rerun()
                else:
                    st.button(f"✅ {likes}", key=f"liked_{msg_id}", disabled=True)
                
                # Supprimer si c'est son message
                if current_user_email == u_email:
                    if st.button("🗑️", key=f"delete_{msg_id}"):
                        cursor.execute('''
                            UPDATE chat_room 
                            SET is_deleted = 1, deleted_by = 'user'
                            WHERE id = ?
                        ''', (msg_id,))
                        conn.commit()
                        st.rerun()
            else:
                if likes > 0:
                    st.markdown(f"👍 {likes}")
        
        st.markdown("</div>", unsafe_allow_html=True)