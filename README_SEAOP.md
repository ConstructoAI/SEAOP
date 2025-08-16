# 🏛️ SEAOP - Système Électronique d'Appel d'Offres Public

## 📋 **Description**

**SEAOP** est un système électronique complet pour la gestion d'appels d'offres publics, permettant aux organismes publics de publier leurs appels d'offres et aux fournisseurs qualifiés de soumettre leurs propositions de manière entièrement dématérialisée.

---

## ✨ **Fonctionnalités Principales**

### 🏛️ **Interface Organismes Publics**
- **Publication d'appels d'offres** avec cahiers des charges détaillés
- **Upload de plans et documents** techniques (PDF, CAD, images)
- **Gestion des critères** de sélection et d'évaluation
- **Consultation des soumissions** reçues en temps réel
- **Système de comparaison** multi-critères des offres
- **Interface de sélection** et d'attribution des contrats
- **Historique complet** de tous les appels d'offres

### 🏢 **Interface Fournisseurs/Entrepreneurs**
- **Consultation des appels d'offres** disponibles par secteur
- **Système de qualification** RBQ et certifications
- **Soumission électronique** sécurisée des propositions
- **Upload de documents** techniques et commerciaux
- **Suivi en temps réel** du statut des soumissions
- **Historique des participations** et taux de succès
- **Notifications automatiques** des nouveaux appels d'offres

### ⚙️ **Administration Système**
- **Dashboard complet** avec statistiques et KPI
- **Gestion des utilisateurs** et des droits d'accès
- **Validation des fournisseurs** et vérification RBQ
- **Rapports d'activité** et d'audit
- **Configuration des paramètres** système
- **Sauvegarde et archivage** automatiques

---

## 🛠️ **Architecture Technique**

### **Stack Technologique**
- **Frontend/Backend** : Streamlit (Python)
- **Base de données** : SQLite (évolutif vers PostgreSQL)
- **Sécurité** : Authentification SHA-256, validation des données
- **Format de données** : Support PDF, CAD, images, documents Office
- **Déploiement** : Compatible serveurs Windows/Linux

### **Structure de la Base de Données**
```sql
-- Appels d'offres (projets)
leads: id, organisme, description, budget, documents, plans, statut

-- Fournisseurs qualifiés
entrepreneurs: id, entreprise, rbq, certifications, zones_service

-- Soumissions électroniques  
soumissions: id, lead_id, montant, proposition, documents, statut

-- Système de messagerie
messages: id, expediteur, destinataire, contenu, pieces_jointes

-- Évaluations et attributions
evaluations: id, criteres, notes, commentaires, decision
```

---

## 🚀 **Installation et Démarrage**

### **Prérequis**
- Python 3.8+ installé
- Navigateur web moderne
- Accès réseau (pour déploiement)

### **Installation Locale**

1. **Télécharger SEAOP**
```bash
git clone [repository-url]
cd SEAOP
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Initialiser la base de données**
```bash
python init_db_v2.py
```

4. **Lancer SEAOP**
```bash
streamlit run app_v2.py
```

### **Installation Simplifiée (Windows)**
Double-cliquez sur `run_seaop.bat`

---

## 👥 **Guide d'Utilisation**

### 🏛️ **Pour les Organismes Publics**

#### **1. Publier un Appel d'Offres**
1. Accédez à **"Nouveau projet"**
2. Complétez les informations :
   - **Organisme** : Nom de l'organisme public
   - **Description** : Cahier des charges détaillé
   - **Budget** : Enveloppe budgétaire estimée
   - **Délais** : Échéances de soumission et réalisation
   
3. **Téléchargez vos documents** :
   - **Plans** : Dessins techniques, plans architecturaux
   - **Cahier des charges** : Spécifications techniques
   - **Documents** : Règlements, normes, contraintes

4. **Configurez les paramètres** :
   - Visibilité aux fournisseurs
   - Date limite de soumission
   - Critères d'évaluation

#### **2. Évaluer les Soumissions**
1. Accédez à **"Mes projets"**
2. Consultez les **soumissions reçues**
3. **Comparez** les offres selon vos critères :
   - Prix proposé
   - Délais d'exécution
   - Qualifications du soumissionnaire
   - Conformité technique

4. **Sélectionnez** la meilleure offre
5. **Attribuez** le contrat au fournisseur retenu

### 🏢 **Pour les Fournisseurs**

#### **1. Créer un Compte Fournisseur**
1. Accédez à **"Espace entrepreneur"**
2. **Inscription** avec :
   - Informations légales de l'entreprise
   - Numéro RBQ (Régie du Bâtiment Québec)
   - Certifications et assurances
   - Zones géographiques desservies
   - Domaines d'expertise

#### **2. Consulter les Appels d'Offres**
1. **Onglet "Projets disponibles"**
2. **Filtrez** par :
   - Type de projet
   - Zone géographique  
   - Budget
   - Date limite

3. **Consultez** les documents fournis
4. **Analysez** la faisabilité du projet

#### **3. Soumettre une Proposition**
1. **Remplissez le formulaire** de soumission :
   - **Montant** total de votre offre
   - **Délais** d'exécution détaillés
   - **Description** technique de votre approche
   - **Inclusions/Exclusions** clairement définies
   - **Conditions** de paiement et garanties

2. **Joignez vos documents** :
   - Plans d'exécution
   - Méthodes de travail
   - Calendrier détaillé
   - Références similaires

3. **Validez** et envoyez votre soumission

#### **4. Suivre vos Soumissions**
- **📤 Envoyée** : Soumission transmise
- **👁️ Vue** : Consultée par l'organisme
- **✅ Acceptée** : Votre offre est retenue
- **❌ Refusée** : Offre non retenue

---

## 🔐 **Comptes de Démonstration**

### **Fournisseurs** (mot de passe: `demo123`)
- **jean@construction-excellence.ca** - Construction Excellence Inc.
- **marie@toitures-pro.ca** - Toitures Pro Québec  
- **pierre@renovations-modernes.ca** - Rénovations Modernes

### **Administrateur**
- **Mot de passe** : `admin123`

### **Appels d'Offres de Démonstration**
- **SEAOP-20240301-ABC12345** - Rénovation cuisine (2 soumissions)
- **SEAOP-20240302-DEF67890** - Toiture urgente (1 soumission acceptée)
- **SEAOP-20240303-GHI23456** - Salle de bain moderne (en cours)

---

## 📊 **Fonctionnalités Avancées**

### **Système de Qualification**
- Vérification automatique des numéros RBQ
- Validation des assurances et certifications
- Historique de performance des fournisseurs
- Système de notation et d'évaluation

### **Conformité Réglementaire**
- Respect des lois sur les contrats publics
- Traçabilité complète des processus
- Archivage sécurisé des documents
- Rapports d'audit automatisés

### **Intégration et API**
- Export des données vers systèmes comptables
- Intégration possible avec ERP existants
- API REST pour développements personnalisés
- Standards d'interopérabilité

---

## 🔒 **Sécurité et Conformité**

### **Mesures de Sécurité**
- ✅ Authentification sécurisée
- ✅ Chiffrement des données sensibles
- ✅ Journalisation des accès
- ✅ Sauvegarde automatique
- ✅ Protection contre les injections SQL

### **Conformité**
- **RGPD/Loi 25** : Protection des données personnelles
- **Standards publics** : Transparence des processus
- **Accessibilité** : Interfaces conformes WCAG
- **Audit** : Traçabilité complète des opérations

---

## 📈 **Avantages SEAOP**

### **Pour les Organismes Publics**
- ⏱️ **Gain de temps** : Processus automatisé et dématérialisé
- 💰 **Économies** : Réduction des coûts administratifs
- 🎯 **Transparence** : Processus équitable et traçable
- 📊 **Efficacité** : Comparaison facilitée des offres
- 🔍 **Contrôle** : Suivi en temps réel des appels d'offres

### **Pour les Fournisseurs**
- 🌐 **Accessibilité** : Consultation 24h/24 des opportunités
- 📋 **Simplicité** : Soumission électronique intuitive
- 💡 **Visibilité** : Accès élargi aux contrats publics
- ⚡ **Rapidité** : Réponse immédiate aux appels d'offres
- 📈 **Croissance** : Développement du portefeuille client

---

## 🛣️ **Roadmap et Évolutions**

### **Version 2.1 (Prochaine)**
- [ ] Système de notifications push
- [ ] Chat en temps réel organisme-fournisseur
- [ ] Module d'évaluation multi-critères avancé
- [ ] Intégration signature électronique

### **Version 2.2 (Moyen terme)**
- [ ] Application mobile native
- [ ] Intelligence artificielle pour pré-qualification
- [ ] Blockchain pour la traçabilité
- [ ] Module de gestion des contrats

### **Version 3.0 (Long terme)**
- [ ] Plateforme multi-organismes
- [ ] Fédération avec autres systèmes publics
- [ ] Analyse prédictive des soumissions
- [ ] Système de réputation avancé

---

## 📞 **Support et Maintenance**

### **Support Technique**
- **Documentation** : Guide utilisateur complet
- **Formation** : Sessions de formation disponibles
- **Assistance** : Support technique dédié
- **Mises à jour** : Évolutions régulières du système

### **Maintenance**
- **Sauvegarde** : Automatique et sécurisée
- **Mise à jour** : Déploiement transparent
- **Monitoring** : Surveillance 24h/24
- **Sécurité** : Patches de sécurité réguliers

---

## 📄 **Licence et Conditions**

SEAOP est un logiciel développé pour les organismes publics du Québec, respectant les standards et réglementations en vigueur pour les systèmes d'appels d'offres électroniques.

---

**🏛️ SEAOP - Modernisons ensemble les appels d'offres publics !**