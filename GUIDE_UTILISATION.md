# 📋 GUIDE D'UTILISATION - SoumissionsQuébec.ca V2

## 🏗️ **Vue d'ensemble**

La nouvelle version de SoumissionsQuébec.ca permet maintenant aux clients de recevoir des **soumissions directes** des entrepreneurs, avec une interface complète pour comparer et choisir les meilleures offres.

---

## 👥 **Pour les CLIENTS**

### 📝 **1. Publier un projet**

1. **Accédez à "Nouveau projet"** dans le menu
2. **Remplissez vos informations** (nom, email, téléphone, code postal)
3. **Décrivez votre projet en détail** :
   - Type de projet (cuisine, salle de bain, toiture, etc.)
   - Budget estimé
   - Délai souhaité
   - Description complète avec dimensions, matériaux, contraintes

4. **Ajoutez vos documents** :
   - **Photos** : État actuel des lieux
   - **Plans** : Plans architecturaux, croquis, dessins
   - **Documents** : Devis existants, permis, etc.

5. **Publiez votre projet** → Vous recevez un numéro de référence unique

### 📊 **2. Consulter vos soumissions**

1. **Accédez à "Mes projets"** 
2. **Entrez votre email** pour voir vos projets
3. **Pour chaque projet**, vous pouvez :
   - Voir le nombre de soumissions reçues
   - Consulter les détails de chaque soumission
   - Comparer les prix et prestations
   - **Accepter** ou **refuser** les soumissions
   - **Contacter** les entrepreneurs
   - **Fermer les soumissions** quand vous êtes satisfait

### 📋 **3. Analyser une soumission**

Chaque soumission contient :
- **Montant total** du projet
- **Description détaillée** des travaux
- **Délai d'exécution**
- **Validité de l'offre**
- **Inclusions** (ce qui est compris)
- **Exclusions** (ce qui n'est pas compris)
- **Conditions de paiement**
- **Informations sur l'entrepreneur** (RBQ, évaluations)

---

## 👷 **Pour les ENTREPRENEURS**

### 🔐 **1. Créer un compte**

1. **Accédez à "Espace entrepreneur"**
2. **Onglet "Inscription"** :
   - Nom de l'entreprise
   - Contact principal
   - Email professionnel
   - Téléphone
   - Numéro RBQ (optionnel)
   - Zones desservies
   - Types de projets
   - Certifications et assurances

3. **Connectez-vous** avec vos identifiants

### 🔍 **2. Consulter les projets**

1. **Onglet "Projets disponibles"** :
   - Consultez tous les projets publiés
   - Filtrez par type, zone, budget
   - Lisez les descriptions détaillées
   - Consultez les plans et documents clients

### 📝 **3. Soumettre une proposition**

Pour chaque projet intéressant :

1. **Cliquez sur le projet** pour voir les détails
2. **Remplissez le formulaire de soumission** :
   - **Montant** de votre proposition
   - **Délai d'exécution** réaliste
   - **Validité de l'offre** (ex: 30 jours)
   - **Description détaillée** de vos travaux :
     - Étapes du projet
     - Matériaux utilisés
     - Méthodologie
     - Équipe assignée
     - Planning détaillé

3. **Précisez inclusions/exclusions** :
   - **Inclusions** : Tout ce qui est compris dans le prix
   - **Exclusions** : Ce qui n'est pas inclus (permis, etc.)
   - **Conditions** : Modalités de paiement

4. **Envoyez votre soumission** → Le client la reçoit immédiatement

### 📋 **4. Suivre vos soumissions**

1. **Onglet "Mes soumissions"** :
   - Consultez toutes vos propositions envoyées
   - Statuts possibles :
     - 📤 **Envoyée** : En attente de lecture
     - 👁️ **Vue** : Le client l'a consultée
     - ✅ **Acceptée** : Félicitations! Contactez le client
     - ❌ **Refusée** : Non retenue

---

## ⚙️ **Pour les ADMINISTRATEURS**

### 🔐 **Accès admin**

- **Mot de passe** : `admin123`
- **Fonctionnalités** :
  - Voir toutes les statistiques
  - Gérer les projets et entrepreneurs
  - Consulter toutes les soumissions
  - Rapports et analytics

---

## 🔑 **COMPTES DE DÉMONSTRATION**

### 👷 **Entrepreneurs** (mot de passe: `demo123`)

1. **jean@construction-excellence.ca** - Construction Excellence Inc.
   - Premium
   - Cuisine, salle de bain, agrandissement

2. **marie@toitures-pro.ca** - Toitures Pro Québec
   - Standard  
   - Toiture, revêtement extérieur

3. **pierre@renovations-modernes.ca** - Rénovations Modernes
   - Entreprise
   - Tous types de rénovations

### 📋 **Projets de démonstration**

- **Rénovation cuisine** (Sophie Bergeron) - 2 soumissions
- **Toiture urgente** (Michel Tremblay) - 1 soumission acceptée
- **Salle de bain spa** (Catherine Larose) - En attente

---

## 🆕 **NOUVELLES FONCTIONNALITÉS V2**

✅ **Upload de documents** - Clients peuvent joindre plans et photos
✅ **Soumissions directes** - Entrepreneurs soumettent leurs propositions détaillées
✅ **Interface de comparaison** - Clients comparent facilement les offres
✅ **Système d'acceptation/refus** - Workflow complet de sélection
✅ **Messagerie intégrée** - Communication directe (en développement)
✅ **Évaluations** - Système de notes et commentaires (en développement)
✅ **Gestion avancée** - Fermeture des soumissions, suivi des statuts

---

## 📱 **WORKFLOW COMPLET**

### 🔄 **Cycle de vie d'un projet**

1. **Client** publie son projet avec documents
2. **Entrepreneurs** consultent et soumettent leurs propositions
3. **Client** reçoit les soumissions et les compare
4. **Client** accepte la meilleure offre
5. **Entrepreneur** est notifié et contacte le client
6. **Projet** démarre avec l'entrepreneur choisi

---

## 🚀 **DÉMARRAGE RAPIDE**

### 💻 **Installation locale**

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base de données
python init_db_v2.py

# 3. Lancer l'application
streamlit run app_v2.py
```

### 🖱️ **Ou utilisez le script**

Double-cliquez sur `run_v2.bat` (Windows)

---

## 📞 **Support**

- **Bugs** : Consultez les logs dans la console
- **Questions** : Documentation technique dans le code
- **Améliorations** : Suggérez de nouvelles fonctionnalités

---

**🎯 L'objectif est maintenant atteint : les clients publient leurs projets avec plans, et les entrepreneurs soumettent directement leurs propositions détaillées !**