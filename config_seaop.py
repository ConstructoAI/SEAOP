# Configuration SEAOP - Système Électronique d'Appel d'Offres Public

# Version du système
VERSION = "2.0.0"
NOM_SYSTEME = "SEAOP"
DESCRIPTION = "Système Électronique d'Appel d'Offres Public"

# Configuration de la base de données
DATABASE_FILE = "seaop.db"
BACKUP_PREFIX = "seaop_backup"

# Codes de référence
REFERENCE_PREFIX = "SEAOP"

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": "SEAOP - Système Électronique d'Appel d'Offres Public",
    "page_icon": "🏛️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Types de projets d'appels d'offres publics
TYPES_PROJETS = [
    "Travaux de construction",
    "Rénovation de bâtiments publics", 
    "Infrastructure routière",
    "Aménagement urbain",
    "Systèmes informatiques",
    "Services professionnels",
    "Fournitures et équipements",
    "Services d'entretien",
    "Travaux d'ingénierie",
    "Consultations spécialisées",
    "Autre"
]

# Tranches budgétaires pour appels d'offres publics
TRANCHES_BUDGET = [
    "Moins de 25 000$",
    "25 000$ - 100 000$", 
    "100 000$ - 500 000$",
    "500 000$ - 1 000 000$",
    "Plus de 1 000 000$",
    "À déterminer selon soumissions"
]

# Délais standards
DELAIS_REALISATION = [
    "Urgent (moins de 1 mois)",
    "Court terme (1-3 mois)",
    "Moyen terme (3-6 mois)", 
    "Long terme (6-12 mois)",
    "Pluriannuel (plus de 12 mois)",
    "Selon calendrier projet"
]

# Formats de fichiers autorisés
FORMATS_AUTORISES = {
    "plans": ["pdf", "dwg", "dxf", "png", "jpg", "jpeg"],
    "documents": ["pdf", "doc", "docx", "xls", "xlsx", "txt"],
    "photos": ["png", "jpg", "jpeg", "gif", "bmp"]
}

# Paramètres de sécurité
SECURITY_CONFIG = {
    "password_min_length": 8,
    "session_timeout": 3600,  # 1 heure en secondes
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "max_files_per_upload": 5
}

# Messages système
MESSAGES = {
    "welcome": "Bienvenue sur SEAOP - Système Électronique d'Appel d'Offres Public",
    "upload_success": "Fichiers téléchargés avec succès",
    "soumission_sent": "Votre soumission a été envoyée avec succès",
    "access_denied": "Accès refusé - Vérifiez vos identifiants"
}

# Configuration email (à personnaliser)
EMAIL_CONFIG = {
    "smtp_server": "localhost",
    "smtp_port": 587,
    "use_tls": True,
    "from_email": "noreply@seaop.gouv.qc.ca",
    "admin_email": "admin@seaop.gouv.qc.ca"
}

# Statuts des appels d'offres
STATUTS_PROJET = {
    "nouveau": "🆕 Nouveau",
    "en_cours": "📋 En cours",
    "ferme": "🔒 Fermé",
    "attribue": "✅ Attribué",
    "annule": "❌ Annulé"
}

# Statuts des soumissions
STATUTS_SOUMISSION = {
    "envoyee": "📤 Envoyée",
    "vue": "👁️ Vue par l'organisme",
    "en_evaluation": "🔍 En évaluation",
    "acceptee": "✅ Acceptée",
    "refusee": "❌ Refusée"
}

# Critères d'évaluation standards
CRITERES_EVALUATION = [
    "Prix (pondération configurable)",
    "Qualifications techniques",
    "Expérience pertinente", 
    "Délais de livraison",
    "Qualité de la proposition",
    "Références clients",
    "Certifications requises",
    "Capacité financière"
]

# Informations organisme (à personnaliser)
ORGANISME_INFO = {
    "nom": "Organisme Public du Québec",
    "adresse": "1234 Rue Gouvernement, Québec, QC, G1A 1A1",
    "telephone": "(418) 555-0123",
    "email": "info@seaop.gouv.qc.ca",
    "site_web": "https://www.seaop.gouv.qc.ca"
}

# Configuration des rapports
RAPPORTS_CONFIG = {
    "formats_export": ["PDF", "Excel", "CSV"],
    "frequence_backup": "quotidienne",
    "retention_donnees": 365,  # jours
    "audit_trail": True
}