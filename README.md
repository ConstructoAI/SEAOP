# 🏛️ SEAOP - Système Électronique d'Appel d'Offres Public

Une plateforme web complète et moderne de gestion d'appels d'offres publics et mise en relation entre clients et entrepreneurs en construction au Québec, développée avec Streamlit.

## 📋 Description

SEAOP (Système Électronique d'Appel d'Offres Public) est une application web avancée qui permet aux clients de publier des appels d'offres et de recevoir des soumissions d'entrepreneurs qualifiés et certifiés RBQ. La plateforme offre un système complet de gestion de projets avec délais, urgence, évaluations, chat en temps réel et notifications.

## ✨ Fonctionnalités principales

### 🏠 Interface Client
- **Formulaire d'appel d'offres avancé** avec gestion des délais et urgence
- **Upload de documents** : photos, plans, PDF et autres fichiers
- **Système de délais intelligent** : dates limites et calcul automatique d'urgence
- **Gestion des soumissions reçues** avec comparaison détaillée
- **Chat en temps réel** avec les entrepreneurs
- **Système d'évaluations** 5 étoiles avec commentaires
- **Notifications avancées** pour le suivi des projets
- **Dashboard client** avec statistiques et KPIs

### 👷 Espace Entrepreneur
- **Projets priorisés par urgence** avec indicateurs visuels (🟢🟡🟠🔴)
- **Soumissions directes** avec upload de documents
- **Chat intégré** pour communication directe avec clients
- **Système d'évaluations** pour construire sa réputation
- **Filtres avancés** : région, budget, type de projet, urgence
- **Dashboard complet** avec métriques de performance
- **Notifications en temps réel** pour nouvelles opportunités
- **Gestion de profil** avec certifications et zones desservies

### ⚙️ Panel Administrateur
- **Vue d'ensemble complète** du système
- **Gestion des utilisateurs** et validation RBQ
- **Analytics avancées** avec graphiques et rapports
- **Système de notifications** globales
- **Gestion des urgences** et escalades automatiques
- **Monitoring en temps réel** des activités

## 🚨 Système de Délais/Urgence

### Niveaux d'urgence automatiques
- 🟢 **Faible** : Plus de 14 jours (délai confortable)
- 🟡 **Normal** : 7-14 jours (dans les temps)
- 🟠 **Élevé** : 3-7 jours (assez urgent)
- 🔴 **Critique** : Moins de 3 jours ou échéance dépassée

### Fonctionnalités
- **Calcul automatique** basé sur les délais de soumission et début des travaux
- **Badges visuels** sur tous les projets
- **Priorisation intelligente** : projets urgents en premier
- **Notifications automatiques** quand l'urgence augmente
- **Interface de délais** dans le formulaire de création de projet

## 💬 Système de Chat et Communication

### Chat en temps réel
- **Messages instantanés** entre clients et entrepreneurs
- **Upload de pièces jointes** dans les conversations
- **Indicateurs de lecture** et notifications
- **Historique complet** des échanges

### Notifications avancées
- 🔔 **Nouvelles soumissions** reçues
- ⚡ **Projets urgents** détectés automatiquement
- 💬 **Nouveaux messages** dans le chat
- ✅ **Soumissions acceptées/refusées**
- 📊 **Nouvelles évaluations** reçues

## ⭐ Système d'Évaluations

### Évaluations mutuelles
- **Notes 5 étoiles** avec commentaires détaillés
- **Moyennes automatiques** calculées en temps réel
- **Historique complet** des évaluations
- **Impact sur la réputation** et visibilité des profils

## 🚀 Installation et démarrage

### Prérequis
- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)

### Méthode rapide (recommandée)
1. **Cloner le projet**
```bash
git clone <url-du-repo>
cd SEAOP
```

2. **Lancer le script de démarrage**
```bash
# Windows
run.bat

# Ou manuellement
py -m streamlit run app_v2.py
```

### Installation manuelle
1. **Installer les dépendances**
```bash
pip install streamlit pandas pillow
```

2. **Initialiser la base de données**
```bash
python init_db_v2.py
```

3. **Lancer l'application**
```bash
streamlit run app_v2.py
```

4. **Accéder à SEAOP**
- URL : `http://localhost:8501`

## 🔐 Comptes de démonstration

### Entrepreneurs (mot de passe: `demo123`)
- **jean@construction-excellence.ca** - Construction Excellence Inc. (Premium)
- **marie@toitures-pro.ca** - Toitures Pro Québec (Standard)
- **pierre@renovations-modernes.ca** - Rénovations Modernes (Entreprise)

### Administrateur
- **Mot de passe** : `admin123`

## 📊 Données de démonstration

L'application inclut des données réalistes :
- ✅ **3 entrepreneurs** avec profils complets et certifications
- ✅ **3 projets détaillés** avec différents niveaux d'urgence
- ✅ **3 soumissions complètes** avec documents
- ✅ **Historique de messages** de démonstration
- ✅ **Système d'évaluations** pré-rempli

## 🛠️ Architecture technique

### Stack technologique
- **Frontend/Backend** : Streamlit 1.28+
- **Base de données** : SQLite avec support de stockage persistant
- **Gestion des fichiers** : Encodage Base64 intégré
- **Sécurité** : Hashage SHA-256 des mots de passe
- **Notifications** : Système intégré en temps réel
- **Déploiement** : Compatible Render, Heroku, et autres platforms

### Nouvelles tables
- **leads** : Projets avec délais et urgence
- **soumissions** : Offres des entrepreneurs avec documents
- **messages** : Chat en temps réel
- **evaluations** : Système de notation 5 étoiles
- **notifications** : Alertes et notifications
- **entrepreneurs** : Profils étendus avec métriques

## 🌐 Déploiement sur Render

### Configuration recommandée
- **Instance** : Standard (2 GB RAM, 1 CPU) - 25$/mois
- **Stockage persistant** : 10 GB configuré
- **Variables d'environnement** :
  - `ADMIN_PASSWORD` : Mot de passe admin sécurisé
  - `DATA_DIR` : `/opt/render/project/data`

### Étapes de déploiement
1. **Connecter le repository** à Render
2. **Configurer les variables** d'environnement
3. **Ajouter le disque persistant** (10 GB)
4. **Déployer** automatiquement

Voir `RENDER_DEPLOYMENT.md` pour les instructions détaillées.

## 🔧 Configuration avancée

### Stockage persistant
- **Local** : Utilise le répertoire `./data/`
- **Production** : Utilise `DATA_DIR` environnement variable
- **Backup automatique** : Lors des migrations de base de données

### Personnalisation
- **Couleurs et thème** : Modifiables dans `app_v2.py`
- **Types de projets** : Configurables dans les formulaires
- **Niveaux d'urgence** : Ajustables dans les fonctions de calcul
- **Notifications** : Templates modifiables

## 📈 Fonctionnalités avancées

### Intelligence artificielle
- **Calcul automatique d'urgence** basé sur les délais
- **Recommandations de projets** pour entrepreneurs
- **Détection d'anomalies** dans les soumissions
- **Optimisation des correspondances** client-entrepreneur

### Analytics et reporting
- **Dashboards clients** : Taux d'acceptation, analyse financière
- **Métriques entrepreneurs** : Performance, évaluations moyennes
- **Analytics administrateur** : Revenus, utilisation, tendances
- **Rapports exportables** : PDF et Excel

### Filtres et recherche
- **Filtres multicritères** : Budget, région, type, urgence, dates
- **Recherche textuelle** dans les descriptions
- **Tri intelligent** : Priorité aux projets urgents
- **Sauvegarde des préférences** de filtrage

## 🚨 Nouveautés Version 2.0

### ✅ Récemment ajouté
- 🎯 **Système de délais/urgence complet**
- 💬 **Chat en temps réel intégré**
- ⭐ **Système d'évaluations mutuelles**
- 🔔 **Notifications automatiques avancées**
- 📊 **Dashboards avec KPIs détaillés**
- 🔍 **Filtres et recherche avancée**
- 📎 **Upload de documents pour soumissions**
- 🎨 **Indicateurs visuels d'urgence**

## 🐛 Dépannage

### Problèmes courants

**L'application ne démarre pas**
```bash
# Vérifier Python
py --version

# Installer les dépendances
py -m pip install streamlit pandas pillow

# Utiliser le script de démarrage
run.bat
```

**Erreur de base de données**
```bash
# Réinitialiser la base
py init_db_v2.py
```

**Port déjà utilisé**
```bash
# Utiliser un autre port
py -m streamlit run app_v2.py --server.port 8502
```

### Messages d'erreur fréquents
- **"notifications table not found"** → Exécuter `py init_db_v2.py`
- **"get_projets_par_email not defined"** → Utiliser la dernière version
- **"IndentationError"** → Vérifier la syntaxe Python

## 🎯 Roadmap

### Version 2.1 (en cours)
- [ ] **API REST** pour intégrations tierces
- [ ] **Webhooks** pour notifications externes
- [ ] **Système de paiements** intégré
- [ ] **Multi-langue** (français/anglais)

### Version 2.2 (futur)
- [ ] **Application mobile** (React Native)
- [ ] **Géolocalisation GPS** avancée
- [ ] **Intelligence artificielle** pour matching
- [ ] **Intégration comptable** (QuickBooks, Sage)

## 📞 Support et documentation

### Démarrage rapide
- **README** : Ce fichier
- **Instructions de démarrage** : `INSTRUCTIONS_DEMARRAGE.md`
- **Déploiement Render** : `RENDER_DEPLOYMENT.md`

### Scripts utiles
- **`run.bat`** : Démarrage automatique Windows
- **`init_db_v2.py`** : Initialisation base de données
- **`app_v2.py`** : Application principale

## 🤝 Contribution

1. Fork le projet SEAOP
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements avec des messages clairs
4. Tester localement avec `py -m streamlit run app_v2.py`
5. Ouvrir une Pull Request détaillée

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🏆 **SEAOP v2.0 - Système d'appels d'offres nouvelle génération**

**Développé avec ❤️ pour moderniser les appels d'offres publics au Québec**

### Statistiques du projet
- **3,000+ lignes de code** Python optimisé
- **15+ fonctionnalités** avancées
- **100% fonctionnel** avec données de démonstration
- **Production-ready** pour déploiement immédiat

### Technologies utilisées
- ⚡ **Streamlit** - Interface web moderne
- 💾 **SQLite** - Base de données robuste  
- 🔐 **SHA-256** - Sécurité des mots de passe
- 📱 **Responsive** - Compatible mobile
- 🎨 **CSS personnalisé** - Design professionnel
- 🔔 **Notifications temps réel** - Communication fluide