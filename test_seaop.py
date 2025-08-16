#!/usr/bin/env python3
# Test rapide SEAOP
import sqlite3
import os

DATA_DIR = os.getenv("DATA_DIR", "/opt/render/project/data")  
DATABASE_PATH = os.path.join(DATA_DIR, "seaop.db")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Test colonnes leads
cursor.execute("PRAGMA table_info(leads)")
columns = [col[1] for col in cursor.fetchall()]
required = ["date_limite_soumissions", "date_debut_souhaite", "niveau_urgence"]
missing = [col for col in required if col not in columns]

if missing:
    print(f"ERREUR: Colonnes manquantes: {missing}")
else:
    print("OK: Toutes les colonnes urgence présentes")

# Test requête urgence  
try:
    cursor.execute("SELECT COUNT(*) FROM leads WHERE niveau_urgence IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"OK: {count} projets avec urgence définie")
except Exception as e:
    print(f"ERREUR: {e}")

conn.close()
