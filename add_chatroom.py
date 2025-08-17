#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter la fonctionnalité Chat Room à SEAOP
"""

import sqlite3
import os
import datetime

# Configuration du stockage persistant
DATA_DIR = os.getenv('DATA_DIR', '.')
DATABASE_PATH = os.path.join(DATA_DIR, 'seaop.db')

def add_chatroom_table():
    """Ajoute la table chat_room à la base de données"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Créer la table chat_room
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_room (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_type TEXT NOT NULL,  -- 'client', 'entrepreneur', 'admin', 'visiteur'
                user_name TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_id INTEGER,  -- ID de l'entrepreneur si applicable
                message TEXT NOT NULL,
                parent_id INTEGER,  -- Pour les réponses à un message
                likes INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT 0,  -- Messages épinglés par admin
                is_deleted BOOLEAN DEFAULT 0,
                deleted_by TEXT,  -- 'user' ou 'admin'
                edited BOOLEAN DEFAULT 0,
                edited_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,  -- Pour modération si nécessaire
                user_badge TEXT,  -- 'verified', 'premium', 'expert', etc.
                FOREIGN KEY (parent_id) REFERENCES chat_room (id)
            )
        ''')
        
        # Créer la table des likes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_room_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES chat_room (id),
                UNIQUE(message_id, user_email)  -- Un seul like par utilisateur par message
            )
        ''')
        
        # Créer la table des utilisateurs en ligne
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
        
        # Créer les index pour performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chatroom_created ON chat_room(created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chatroom_parent ON chat_room(parent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chatroom_user ON chat_room(user_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chatroom_online ON chat_room_online(last_seen)')
        
        # Ajouter quelques messages de bienvenue
        messages_demo = [
            {
                'user_type': 'admin',
                'user_name': 'Admin SEAOP',
                'user_email': 'admin@seaop.ca',
                'message': '🎉 Bienvenue dans le Chat Room SEAOP! Cet espace est dédié aux discussions entre clients et entrepreneurs. Respectez les règles de courtoisie.',
                'is_pinned': 1,
                'user_badge': 'admin'
            },
            {
                'user_type': 'entrepreneur',
                'user_name': 'Jean Tremblay - Construction Excellence',
                'user_email': 'jean@construction-excellence.ca',
                'user_id': 1,
                'message': 'Bonjour à tous! Ravi de faire partie de cette communauté. N\'hésitez pas si vous avez des questions sur vos projets de rénovation! 🏗️',
                'user_badge': 'verified'
            },
            {
                'user_type': 'client',
                'user_name': 'Sophie Bergeron',
                'user_email': 'sophie.bergeron@email.com',
                'message': 'Super initiative ce chat! J\'ai justement des questions sur les prix moyens pour une rénovation de cuisine. Quelqu\'un peut m\'éclairer?',
                'user_badge': None
            },
            {
                'user_type': 'entrepreneur',
                'user_name': 'Marie Lavoie - Toitures Pro',
                'user_email': 'marie@toitures-pro.ca',
                'user_id': 2,
                'message': '@Sophie Bergeron Pour une cuisine, comptez entre 15,000$ et 50,000$ selon la taille et les matériaux. Je peux vous référer à des collègues spécialisés!',
                'parent_id': 3,
                'user_badge': 'premium'
            }
        ]
        
        # Insérer les messages de démonstration
        for msg in messages_demo:
            cursor.execute('''
                INSERT INTO chat_room (
                    user_type, user_name, user_email, user_id, message, 
                    parent_id, is_pinned, user_badge
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                msg['user_type'], msg['user_name'], msg['user_email'], 
                msg.get('user_id'), msg['message'], msg.get('parent_id'),
                msg.get('is_pinned', 0), msg.get('user_badge')
            ))
        
        conn.commit()
        print("Table chat_room creee avec succes!")
        print("Tables chat_room_likes et chat_room_online creees!")
        print("4 messages de demonstration ajoutes")
        print("Index de performance crees")
        
    except sqlite3.Error as e:
        print(f"Erreur lors de la creation de la table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Ajout de la fonctionnalite Chat Room a SEAOP...")
    add_chatroom_table()
    print("\nInstructions pour activer le Chat Room:")
    print("1. Redemarrez l'application avec: py -m streamlit run app_v2.py")
    print("2. Le bouton 'Chat Room' apparaitra dans le menu")
    print("3. Les utilisateurs pourront discuter en temps reel")