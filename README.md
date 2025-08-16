# 🏗️ SoumissionsQuébec.ca

Une plateforme web complète de mise en relation entre clients et entrepreneurs en construction au Québec, développée avec Streamlit.

## 📋 Description

SoumissionsQuébec.ca est une application web qui permet aux clients de recevoir jusqu'à 5 soumissions gratuites d'entrepreneurs qualifiés et certifiés RBQ pour leurs projets de construction et rénovation. La plateforme offre également aux entrepreneurs un système de génération de leads ciblés selon leur expertise et zone géographique.

## ✨ Fonctionnalités principales

### 🏠 Interface Client
- Formulaire de demande de soumission intuitive
- 10 types de projets supportés (cuisine, salle de bain, toiture, etc.)
- Upload de photos pour illustrer le projet
- Système de budgets par tranches
- Numéro de référence unique pour chaque demande
- Validation des données (email, téléphone, code postal canadien)

### 👷 Espace Entrepreneur
- Système d'authentification sécurisé
- Dashboard avec statistiques personnalisées
- Visualisation des nouveaux leads disponibles
- Système de crédits et d'abonnements flexibles
- Gestion de profil d'entreprise
- Historique des leads attribués
- Notes de suivi client

### ⚙️ Panel Administrateur
- Vue d'ensemble du système
- Gestion des entrepreneurs et validation RBQ
- Suivi des leads et attributions
- Rapports et analytics détaillés
- Gestion des abonnements et facturation

## 🚀 Installation et démarrage

### Prérequis
- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le projet**
```bash
git clone <url-du-repo>
cd soum-web
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Initialiser la base de données avec des données de démonstration**
```bash
python init_db.py
```

4. **Lancer l'application**
```bash
streamlit run app.py
```

5. **Accéder à l'application**
- Ouvrir votre navigateur à l'adresse : `http://localhost:8501`

## 🎯 Utilisation

### Pour les clients
1. Accéder à la page "Demande de soumission"
2. Remplir le formulaire avec les détails du projet
3. Recevoir un numéro de référence unique
4. Attendre les appels des entrepreneurs (24-48h)

### Pour les entrepreneurs
1. Créer un compte ou se connecter
2. Consulter les nouveaux leads dans le dashboard
3. Accepter les leads pertinents (coût selon le type de projet)
4. Contacter les clients et faire le suivi

### Pour les administrateurs
- Mot de passe par défaut : `admin123`
- Accéder via l'onglet "Administration"

## 🔐 Comptes de démonstration

### Entrepreneurs (mot de passe: `demo123`)
- `jean@constructiontremblay.ca` - Construction Tremblay Inc. (Premium)
- `marie@electrique-qc.ca` - Électricité Moderne Québec (Standard)  
- `pierre@plomberie-excellence.ca` - Plomberie Excellence (Standard)
- `sylvie@toitures-qc-pro.ca` - Toitures Québec Pro (Premium)
- `robert@cuisine-design-plus.ca` - Cuisine Design Plus (Entreprise)
- `louise@peinture-artistique-mtl.ca` - Peinture Artistique Montréal (Gratuit)
- `francois@revetement-durable.ca` - Revêtement Extérieur Durable (Standard)
- `annie@planchers-nobles-qc.ca` - Planchers Nobles Québec (Standard)
- `marc@solutions-batiment.ca` - Solutions Bâtiment Global (Premium)
- `caroline@renovation-express.ca` - Rénovation Express 24h (Gratuit)

### Administrateur
- Mot de passe : `admin123`

## 💰 Modèle d'affaires

### Plans d'abonnement
- **Gratuit** : 5 leads/mois (0$/mois)
- **Standard** : 50 leads/mois (299$/mois)  
- **Premium** : 100 leads/mois (499$/mois)
- **Entreprise** : Illimité (899$/mois)

### Tarification par lead
- Petits travaux (peinture, plancher) : 25-35$/lead
- Travaux moyens (électricité, plomberie) : 45$/lead  
- Gros projets (cuisine, toiture, agrandissement) : 65-100$/lead

## 🛠️ Architecture technique

### Stack technologique
- **Frontend/Backend** : Streamlit
- **Base de données** : SQLite
- **Gestion d'état** : Session State Streamlit
- **Sécurité** : Hashage SHA-256 des mots de passe
- **Déploiement** : Compatible Hugging Face Spaces

### Structure des données
- **Leads** : Demandes de soumission des clients
- **Entrepreneurs** : Profils des entreprises de construction  
- **Attributions** : Liens entre leads et entrepreneurs avec suivi

### Fonctionnalités de sécurité
- Validation des entrées utilisateur
- Protection contre l'injection SQL
- Hashage sécurisé des mots de passe
- Conformité RGPD/Loi 25 (consentement explicite)

## 📊 Données de démonstration

L'application inclut :
- 10 entrepreneurs avec profils complets
- 50 leads réalistes sur 3 mois
- Attributions et historique de suivi
- Statistiques et métriques de performance

## 🎨 Design et UX

- Interface moderne et professionnelle
- Responsive design (compatible mobile)
- Couleurs corporatives : Bleu (#1E3A8A) et Orange (#F97316)
- Messages d'erreur et de succès clairs
- Navigation intuitive avec sidebar

## 🚀 Déploiement sur Hugging Face Spaces

1. Créer un nouveau Space sur Hugging Face
2. Sélectionner "Streamlit" comme SDK
3. Uploader tous les fichiers du projet
4. Le Space se déploiera automatiquement

## 🔧 Configuration

### Variables d'environnement (optionnel)
- `SMTP_SERVER` : Serveur SMTP pour les emails
- `SMTP_USER` : Utilisateur SMTP
- `SMTP_PASSWORD` : Mot de passe SMTP

### Personnalisation
- Modifier les couleurs dans le CSS du fichier `app.py`
- Ajuster les prix des leads dans la fonction `get_prix_lead()`
- Personnaliser les types de projets et budgets

## 📈 Fonctionnalités avancées

### Automatisations
- Distribution intelligente des leads
- Notifications par email (à configurer)
- Relances automatiques après 48h
- Limitation à 5 entrepreneurs par lead

### Analytics
- Taux de conversion par type de projet
- Performance par entrepreneur
- Revenus par période
- Statistiques d'engagement

## 🐛 Dépannage

### Problèmes courants

**L'application ne démarre pas**
- Vérifier que Python 3.8+ est installé
- Installer les dépendances : `pip install -r requirements.txt`

**Base de données vide**
- Exécuter : `python init_db.py`

**Erreurs de connexion**
- Vérifier les identifiants de démonstration
- Réinitialiser la base de données si nécessaire

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support :
- Email : support@soumissionsquebec.ca
- Documentation : Ce fichier README
- Issues : Utiliser le système d'issues du repository

## 🎯 Roadmap

### Version 1.1 (à venir)
- [ ] Système de notifications push
- [ ] API REST pour intégrations tierces
- [ ] Chat en temps réel entrepreneur-client
- [ ] Système de reviews et évaluations

### Version 1.2 (futur)
- [ ] Application mobile
- [ ] Géolocalisation avancée
- [ ] Intelligence artificielle pour matching
- [ ] Intégration systèmes comptables

---

**Développé avec ❤️ pour les entrepreneurs québécois**