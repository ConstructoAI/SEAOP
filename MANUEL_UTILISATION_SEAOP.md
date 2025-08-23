# 📚 MANUEL D'UTILISATION COMPLET - SEAOP v2.0

## 🏛️ Système Électronique d'Appel d'Offres Public

---

## 📋 TABLE DES MATIÈRES

1. [Introduction](#introduction)
2. [Démarrage Rapide](#demarrage-rapide)
3. [Guide Client - Publier un Appel d'Offres](#guide-client)
4. [Guide Entrepreneur - Répondre aux Appels d'Offres](#guide-entrepreneur)
5. [Guide Administrateur](#guide-administrateur)
6. [Fonctionnalités Avancées](#fonctionnalites-avancees)
7. [Dépannage](#depannage)
8. [FAQ](#faq)
9. [Support et Contact](#support-contact)

---

## 🎯 INTRODUCTION {#introduction}

### Qu'est-ce que SEAOP ?

SEAOP (Système Électronique d'Appel d'Offres Public) est une plateforme web moderne qui facilite la mise en relation entre :
- **Organismes publics** qui publient des appels d'offres
- **Entrepreneurs certifiés RBQ** qui soumissionnent sur les projets
- **Administrateurs** qui gèrent et supervisent le système

### Objectifs de SEAOP

✅ **Simplifier** le processus d'appel d'offres public  
✅ **Centraliser** toutes les soumissions en un seul endroit  
✅ **Garantir** la transparence et l'équité  
✅ **Accélérer** les délais de traitement  
✅ **Sécuriser** les échanges et documents  

### Prérequis Techniques

- **Navigateur web** : Chrome, Firefox, Safari ou Edge (dernières versions)
- **Connexion Internet** stable
- **Résolution d'écran** : Minimum 1024x768 (optimal 1920x1080)
- **JavaScript** activé dans le navigateur

---

## 🚀 DÉMARRAGE RAPIDE {#demarrage-rapide}

### Première Connexion

1. **Accédez à SEAOP** :
   - URL locale : `http://localhost:8501`
   - URL production : `https://seaop-xxx.onrender.com`

2. **Choisissez votre profil** :
   - 🏢 **Client/Organisme** : Pour publier des appels d'offres
   - 👷 **Entrepreneur** : Pour soumissionner sur des projets
   - ⚙️ **Administrateur** : Pour gérer le système

3. **Créez votre compte ou connectez-vous** :
   - Nouveaux utilisateurs → "Créer un compte"
   - Utilisateurs existants → "Se connecter"

### Comptes de Démonstration

Pour tester SEAOP sans créer de compte :

#### Entrepreneurs (mot de passe : `demo123`)
- `jean@construction-excellence.ca` - Abonnement Premium
- `marie@toitures-pro.ca` - Abonnement Standard
- `pierre@renovations-modernes.ca` - Abonnement Entreprise

#### Administrateur
- Mot de passe : `admin123`

---

## 🏢 GUIDE CLIENT - PUBLIER UN APPEL D'OFFRES {#guide-client}

### 1. Créer un Nouvel Appel d'Offres

#### Étape 1 : Accédez au formulaire
1. Cliquez sur **"📋 Publier un appel d'offres"** dans le menu
2. Le formulaire de création s'affiche

#### Étape 2 : Informations de base
Remplissez les champs obligatoires :

**Identification du projet**
- **Nom du projet** : Titre descriptif (ex: "Rénovation École Saint-Jean")
- **Type de projet** : Sélectionnez dans la liste déroulante
  - Travaux de construction
  - Rénovation de bâtiments publics
  - Infrastructure routière
  - Aménagement urbain
  - Systèmes informatiques
  - Etc.

**Coordonnées de l'organisme**
- **Nom de l'organisme** : Nom officiel complet
- **Personne contact** : Responsable du projet
- **Courriel** : Adresse de contact principale
- **Téléphone** : Numéro avec indicatif régional

**Localisation du projet**
- **Adresse complète** : Lieu d'exécution des travaux
- **Ville** : Municipalité
- **Code postal** : Format A1A 1A1

#### Étape 3 : Détails du projet

**Description détaillée**
```
Décrivez précisément :
- Nature des travaux à réaliser
- Objectifs du projet
- Contraintes particulières
- Exigences spécifiques
- Critères de qualité attendus
```

**Budget et échéancier**
- **Tranche budgétaire** :
  - Moins de 25 000$
  - 25 000$ - 100 000$
  - 100 000$ - 500 000$
  - 500 000$ - 1 000 000$
  - Plus de 1 000 000$
  - À déterminer selon soumissions

- **Délai de réalisation** :
  - Urgent (moins de 1 mois)
  - Court terme (1-3 mois)
  - Moyen terme (3-6 mois)
  - Long terme (6-12 mois)
  - Pluriannuel (plus de 12 mois)

#### Étape 4 : Dates importantes

⚠️ **IMPORTANT** : Ces dates déterminent l'urgence automatique du projet

- **Date limite de soumission** : Dernier jour pour recevoir les offres
- **Date de début souhaitée** : Début prévu des travaux

**Calcul automatique de l'urgence** :
- 🟢 **Faible** : Plus de 14 jours restants
- 🟡 **Normal** : Entre 7 et 14 jours
- 🟠 **Élevé** : Entre 3 et 7 jours  
- 🔴 **Critique** : Moins de 3 jours

#### Étape 5 : Documents à joindre

**Types de fichiers acceptés** :
- 📷 **Photos** : JPG, PNG, GIF (max 10 MB)
- 📄 **Plans** : PDF, DWG, DXF
- 📑 **Documents** : PDF, DOC, DOCX, XLS, XLSX

**Comment uploader** :
1. Cliquez sur "Parcourir"
2. Sélectionnez jusqu'à 5 fichiers
3. Attendez le téléchargement complet
4. Vérifiez l'aperçu des fichiers

#### Étape 6 : Validation et publication

1. **Vérifiez** toutes les informations saisies
2. **Cliquez** sur "Publier l'appel d'offres"
3. **Notez** le numéro de référence généré (SEAOP-YYYYMMDD-XXXXXX)
4. **Recevez** la confirmation par courriel

### 2. Gérer vos Appels d'Offres

#### Accéder à vos projets
1. Menu → **"📊 Mes appels d'offres"**
2. Entrez votre courriel
3. Cliquez sur "Voir mes projets"

#### Tableau de bord client

**Informations affichées** :
- Liste de tous vos projets
- Statut de chaque projet
- Nombre de soumissions reçues
- Niveau d'urgence
- Actions disponibles

**Statuts possibles** :
- 🆕 **Nouveau** : Récemment publié
- 📋 **En cours** : Accepte les soumissions
- 🔒 **Fermé** : Date limite dépassée
- ✅ **Attribué** : Entrepreneur sélectionné
- ❌ **Annulé** : Projet annulé

### 3. Consulter les Soumissions Reçues

#### Voir les détails d'une soumission

1. **Cliquez** sur "Voir les soumissions" pour un projet
2. **Consultez** la liste des offres reçues
3. **Pour chaque soumission**, vous verrez :
   - Nom de l'entrepreneur
   - Montant proposé
   - Délai d'exécution
   - Date de soumission
   - Documents joints

#### Analyser une soumission

**Éléments à examiner** :
- 💰 **Montant** : Prix total proposé
- 📅 **Délai** : Temps d'exécution prévu
- 📋 **Description des travaux** : Approche proposée
- ✅ **Inclusions** : Ce qui est compris
- ❌ **Exclusions** : Ce qui n'est pas inclus
- 📎 **Documents** : Devis, plans, certifications

#### Comparer les soumissions

**Tableau comparatif automatique** :
- Classement par prix (croissant/décroissant)
- Comparaison des délais
- Vérification des certifications RBQ
- Notes et évaluations des entrepreneurs

### 4. Communication avec les Entrepreneurs

#### Utiliser le chat intégré

1. **Accédez** au chat depuis la soumission
2. **Envoyez** des messages directs
3. **Partagez** des documents supplémentaires
4. **Posez** des questions de clarification
5. **Négociez** les termes si nécessaire

**Bonnes pratiques** :
- Soyez précis dans vos questions
- Répondez rapidement aux demandes
- Documentez tous les échanges
- Restez professionnel

### 5. Sélectionner un Entrepreneur

#### Processus de sélection

1. **Évaluez** toutes les soumissions selon vos critères
2. **Contactez** les finalistes pour clarifications
3. **Sélectionnez** l'entrepreneur retenu
4. **Cliquez** sur "Accepter cette soumission"
5. **Confirmez** votre choix

#### Après la sélection

- ✅ L'entrepreneur est notifié automatiquement
- ✅ Les autres soumissionnaires sont informés
- ✅ Le projet passe au statut "Attribué"
- ✅ Vous recevez les coordonnées complètes

### 6. Évaluer l'Entrepreneur

#### Quand évaluer ?

Après la **complétion des travaux** :
1. Menu → "Mes projets"
2. Sélectionnez le projet complété
3. Cliquez sur "Évaluer l'entrepreneur"

#### Critères d'évaluation

**Note globale** (1 à 5 étoiles) :
- ⭐ Très insatisfaisant
- ⭐⭐ Insatisfaisant  
- ⭐⭐⭐ Satisfaisant
- ⭐⭐⭐⭐ Très satisfaisant
- ⭐⭐⭐⭐⭐ Excellent

**Aspects à évaluer** :
- Respect des délais
- Qualité du travail
- Communication
- Respect du budget
- Professionnalisme

---

## 👷 GUIDE ENTREPRENEUR - RÉPONDRE AUX APPELS D'OFFRES {#guide-entrepreneur}

### 1. Créer votre Compte Entrepreneur

#### Inscription initiale

1. **Accédez** à "Espace Entrepreneur"
2. **Cliquez** sur "Créer un compte entrepreneur"
3. **Remplissez** le formulaire :

**Informations de l'entreprise** :
- Nom de l'entreprise
- Numéro RBQ (obligatoire)
- Adresse complète
- Site web (optionnel)

**Contact principal** :
- Nom du responsable
- Courriel professionnel
- Téléphone direct
- Cellulaire (optionnel)

**Capacités et services** :
- Types de projets réalisés
- Zones géographiques desservies
- Certifications détenues
- Assurances et cautionnements

#### Choisir votre abonnement

| Plan | Prix/mois | Crédits | Avantages |
|------|-----------|---------|-----------|
| **Gratuit** | 0$ | 5/mois | Accès de base |
| **Standard** | 49$ | 20/mois | + Notifications prioritaires |
| **Premium** | 99$ | 50/mois | + Badge Premium + Support prioritaire |
| **Entreprise** | 199$ | Illimités | + Gestionnaire de compte dédié |

### 2. Naviguer dans l'Espace Entrepreneur

#### Tableau de bord principal

**Sections disponibles** :
- 📊 **Vue d'ensemble** : KPIs et statistiques
- 🔔 **Notifications** : Alertes et messages
- 📋 **Projets disponibles** : Nouveaux appels d'offres
- 📤 **Mes soumissions** : Suivi de vos offres
- 💬 **Messages** : Communications avec clients
- ⭐ **Évaluations** : Notes reçues

#### Indicateurs de performance (KPIs)

**Métriques affichées** :
- Nombre de soumissions envoyées
- Taux de succès (%)
- Évaluation moyenne (⭐)
- Projets en cours
- Revenus générés

### 3. Rechercher des Projets

#### Utiliser les filtres

**Filtres disponibles** :
- **Type de projet** : Votre spécialité
- **Budget** : Tranche qui vous convient
- **Localisation** : Zone géographique
- **Urgence** : Niveau de priorité
- **Date limite** : Temps restant

#### Comprendre les indicateurs d'urgence

Les projets sont **automatiquement triés** par urgence :
- 🔴 **Critique** : Répondez immédiatement !
- 🟠 **Élevé** : Action rapide requise
- 🟡 **Normal** : Délai standard
- 🟢 **Faible** : Temps confortable

### 4. Soumettre une Offre

#### Préparer votre soumission

**Avant de commencer** :
1. ✅ Lisez **entièrement** l'appel d'offres
2. ✅ Téléchargez tous les documents fournis
3. ✅ Vérifiez votre éligibilité (RBQ, zone, etc.)
4. ✅ Calculez précisément vos coûts
5. ✅ Préparez vos documents

#### Remplir le formulaire de soumission

**Section 1 : Montant et délais**
- **Montant total** : Prix ferme en $ CAD
- **Délai d'exécution** : En jours ouvrables
- **Validité de l'offre** : Généralement 30-60 jours

**Section 2 : Description technique**
```
Détaillez votre approche :
- Méthodologie proposée
- Équipe assignée
- Équipements utilisés
- Planning détaillé
- Mesures de sécurité
```

**Section 3 : Inclusions/Exclusions**

*Inclusions (ce qui est compris)* :
- Main d'œuvre
- Matériaux spécifiés
- Équipements
- Permis et autorisations
- Nettoyage du site

*Exclusions (ce qui n'est PAS inclus)* :
- Travaux supplémentaires
- Modifications au devis
- Conditions de sol imprévues
- Augmentation des matériaux

**Section 4 : Conditions**
- Modalités de paiement
- Garanties offertes
- Assurances fournies
- Clauses particulières

#### Joindre vos documents

**Documents recommandés** :
- 📄 **Devis détaillé** (PDF)
- 📋 **CV de l'équipe** 
- 🏗️ **Portfolio de projets similaires**
- 📜 **Certifications et licences**
- 🛡️ **Preuves d'assurance**
- 💰 **Cautionnement** (si requis)

#### Vérifier avant envoi

**Check-list finale** :
- [ ] Montant vérifié et compétitif
- [ ] Délais réalistes
- [ ] Description complète
- [ ] Documents tous attachés
- [ ] Coordonnées à jour
- [ ] Crédit disponible pour soumission

### 5. Suivre vos Soumissions

#### États des soumissions

- 📤 **Envoyée** : Transmission réussie
- 👁️ **Vue** : Le client a consulté
- 🔍 **En évaluation** : Analyse en cours
- ✅ **Acceptée** : Vous avez gagné !
- ❌ **Refusée** : Non retenue

#### Actions possibles

**Tant que "En évaluation"** :
- Modifier votre offre
- Ajouter des documents
- Envoyer des messages
- Retirer votre soumission

### 6. Communication avec les Clients

#### Chat intégré

**Utilisation optimale** :
1. **Répondez rapidement** (< 24h)
2. **Soyez professionnel**
3. **Clarifiez les ambiguïtés**
4. **Proposez des alternatives**
5. **Documentez les échanges**

#### Notifications

**Types d'alertes** :
- 🔔 Nouveau projet dans votre domaine
- 💬 Message d'un client
- ✅ Soumission acceptée
- ⭐ Nouvelle évaluation reçue
- 🔴 Projet urgent publié

### 7. Gérer votre Réputation

#### Système d'évaluation

**Impact des évaluations** :
- ⭐⭐⭐⭐⭐ : Visibilité maximale
- ⭐⭐⭐⭐ : Bon positionnement
- ⭐⭐⭐ : Position standard
- < ⭐⭐⭐ : Visibilité réduite

**Améliorer votre note** :
- Respectez vos engagements
- Communiquez proactivement
- Dépassez les attentes
- Résolvez rapidement les problèmes
- Demandez des évaluations

---

## ⚙️ GUIDE ADMINISTRATEUR {#guide-administrateur}

### 1. Accès au Panel d'Administration

#### Connexion sécurisée

1. **Accédez** au menu "⚙️ Administration"
2. **Entrez** le mot de passe administrateur
3. **Validez** l'accès

**Sécurité** :
- Mot de passe fort requis
- Session expire après 1 heure
- Historique des connexions enregistré

### 2. Tableau de Bord Administrateur

#### Vue d'ensemble système

**Statistiques globales** :
- 👥 Nombre total d'utilisateurs
- 📋 Projets actifs
- 💰 Volume de soumissions
- 📊 Taux d'attribution
- ⭐ Satisfaction moyenne

**Graphiques temps réel** :
- Évolution des inscriptions
- Activité par région
- Répartition par type de projet
- Performance du système

### 3. Gestion des Utilisateurs

#### Validation des entrepreneurs

**Processus de vérification** :
1. **Vérifier** le numéro RBQ
2. **Valider** les assurances
3. **Contrôler** les certifications
4. **Approuver** ou **Rejeter**

**Actions disponibles** :
- ✅ Activer un compte
- ⏸️ Suspendre temporairement
- ❌ Bannir définitivement
- 📧 Envoyer un message
- 🔄 Réinitialiser mot de passe

#### Gestion des clients

**Surveillance** :
- Historique des projets
- Taux d'attribution
- Délais moyens
- Litiges en cours

### 4. Modération du Contenu

#### Projets publiés

**Vérifications** :
- Conformité légale
- Clarté des exigences
- Budget réaliste
- Délais appropriés

**Actions possibles** :
- ✅ Approuver
- ✏️ Demander modifications
- ⏸️ Mettre en attente
- ❌ Rejeter

#### Chat et messages

**Modération** :
- Surveillance des échanges
- Détection de spam
- Résolution de conflits
- Archivage légal

### 5. Gestion des Abonnements

#### Plans et facturation

**Gestion des plans** :
- Modifier les tarifs
- Créer des promotions
- Offrir des crédits
- Générer des rapports

**Suivi financier** :
- Revenus mensuels
- Taux de conversion
- Churn rate
- Lifetime value

### 6. Configuration Système

#### Paramètres généraux

**Personnalisation** :
- Nom de l'organisme
- Logo et couleurs
- Messages système
- Notifications email

**Paramètres techniques** :
- Limites d'upload
- Timeout sessions
- Backup automatique
- Maintenance planifiée

#### Gestion des catégories

**Types de projets** :
- Ajouter/Modifier/Supprimer
- Réorganiser l'ordre
- Définir les codes

**Zones géographiques** :
- Régions administratives
- Codes postaux
- Zones de service

### 7. Rapports et Analytics

#### Rapports standards

**Disponibles** :
- 📊 Rapport mensuel d'activité
- 💰 Analyse financière
- 👥 Statistiques utilisateurs
- 🏆 Top entrepreneurs
- 📈 Tendances du marché

#### Export de données

**Formats supportés** :
- Excel (.xlsx)
- CSV
- PDF
- JSON

**Conformité** :
- RGPD / Loi 25
- Archivage légal
- Audit trail complet

### 8. Support et Urgences

#### Gestion des tickets

**Priorités** :
- 🔴 **Critique** : Système down
- 🟠 **Haute** : Fonction majeure KO
- 🟡 **Moyenne** : Bug mineur
- 🟢 **Basse** : Amélioration

#### Procédures d'urgence

**En cas de problème majeur** :
1. Activer le mode maintenance
2. Notifier les utilisateurs
3. Créer un backup
4. Appliquer le correctif
5. Tester en staging
6. Déployer en production

---

## 🚀 FONCTIONNALITÉS AVANCÉES {#fonctionnalites-avancees}

### 1. Services Spécialisés

#### Service d'Architecture

**Pour projets > 6000 pi²** :
1. Menu → "🏛️ Service d'architecture"
2. Remplir le formulaire détaillé
3. Joindre certificat de localisation
4. Recevoir devis automatique

**Tarification automatique** :
- Base : 15 000$ - 60 000$
- Par pi² : 0.85$ - 1.50$
- Options : Structure, Mécanique, Électrique

#### Service d'Estimation

**Estimation professionnelle** :
1. Soumettre plans et devis
2. Analyse par experts
3. Rapport détaillé sous 48h
4. Précision ±5%

### 2. Chat Room Communautaire

#### Participer aux discussions

**Fonctionnalités** :
- 💬 Messages publics
- 👍 Système de likes
- 💭 Réponses threadées
- 📌 Messages épinglés
- 🏆 Badges utilisateurs

**Règles de conduite** :
- Respect et professionnalisme
- Pas de sollicitation directe
- Partage de connaissances
- Entraide communautaire

### 3. Notifications Intelligentes

#### Configuration personnalisée

**Types d'alertes** :
- Email instantané
- Résumé quotidien
- Bulletin hebdomadaire
- SMS (premium)

**Filtres disponibles** :
- Type de projet
- Budget minimum
- Zone géographique
- Niveau d'urgence

### 4. API et Intégrations

#### Webhooks disponibles

**Événements** :
- Nouveau projet publié
- Soumission reçue
- Projet attribué
- Évaluation reçue

**Format** :
```json
{
  "event": "new_project",
  "data": {
    "id": "SEAOP-20240101-ABC123",
    "type": "construction",
    "budget": "100000-500000",
    "urgency": "high"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 5. Rapports Personnalisés

#### Création de rapports

**Étapes** :
1. Sélectionner les métriques
2. Définir la période
3. Appliquer les filtres
4. Choisir le format
5. Planifier l'envoi

**Métriques disponibles** :
- Taux de succès
- Temps de réponse moyen
- ROI par type de projet
- Analyse concurrentielle
- Prévisions de marché

---

## 🔧 DÉPANNAGE {#depannage}

### Problèmes de Connexion

#### "Impossible de se connecter"

**Solutions** :
1. Vérifiez votre courriel (casse exacte)
2. Réinitialisez votre mot de passe
3. Videz le cache du navigateur
4. Essayez un autre navigateur
5. Vérifiez votre connexion Internet

#### "Session expirée"

**Causes et solutions** :
- Inactivité > 1 heure → Reconnectez-vous
- Connexion multiple → Utilisez une seule session
- Cookies bloqués → Autorisez les cookies

### Problèmes d'Upload

#### "Échec du téléchargement"

**Vérifications** :
- Taille < 10 MB par fichier
- Format autorisé (PDF, JPG, PNG, etc.)
- Maximum 5 fichiers simultanés
- Connexion Internet stable

**Solutions** :
1. Réduisez la taille des images
2. Convertissez en PDF
3. Uploadez un par un
4. Utilisez une connexion filaire

### Problèmes d'Affichage

#### "Page mal affichée"

**Actions correctives** :
1. **Ctrl+F5** : Rafraîchir complètement
2. Vider le cache navigateur
3. Désactiver extensions navigateur
4. Vérifier zoom à 100%
5. Mettre à jour le navigateur

#### "Boutons non cliquables"

**Solutions** :
- Activez JavaScript
- Désactivez bloqueur de publicités
- Autorisez les pop-ups pour SEAOP
- Essayez mode incognito

### Problèmes de Soumission

#### "Crédit insuffisant"

**Options** :
1. Vérifiez votre solde de crédits
2. Mettez à niveau votre abonnement
3. Attendez le renouvellement mensuel
4. Contactez le support

#### "Soumission non envoyée"

**Vérifications** :
- Tous les champs obligatoires remplis
- Documents correctement uploadés
- Date limite non dépassée
- Crédit disponible

### Problèmes de Notification

#### "Je ne reçois pas d'emails"

**Vérifications** :
1. Vérifiez les **spams/indésirables**
2. Ajoutez `noreply@seaop.gouv.qc.ca` aux contacts
3. Vérifiez l'adresse email dans votre profil
4. Activez les notifications dans les paramètres

---

## ❓ FAQ - FOIRE AUX QUESTIONS {#faq}

### Questions Générales

**Q : SEAOP est-il gratuit ?**
R : L'inscription et la consultation sont gratuites. Les entrepreneurs ont des plans payants pour soumissionner.

**Q : Qui peut utiliser SEAOP ?**
R : Tous les organismes publics du Québec et les entrepreneurs certifiés RBQ.

**Q : Les données sont-elles sécurisées ?**
R : Oui, chiffrement SSL, mots de passe hashés SHA-256, backups quotidiens.

### Questions Clients

**Q : Combien de temps pour recevoir des soumissions ?**
R : Généralement 24-48h pour les premiers, selon l'urgence et l'attractivité du projet.

**Q : Puis-je modifier un appel d'offres publié ?**
R : Oui, tant qu'aucune soumission n'a été reçue. Sinon, contactez le support.

**Q : Comment comparer efficacement les soumissions ?**
R : Utilisez le tableau comparatif automatique et les filtres de tri.

### Questions Entrepreneurs

**Q : Combien coûte une soumission ?**
R : 1 crédit par soumission. Les crédits varient selon votre abonnement.

**Q : Puis-je modifier ma soumission ?**
R : Oui, tant que le client ne l'a pas encore acceptée ou refusée.

**Q : Comment améliorer mes chances ?**
R : Profil complet, réponse rapide, prix compétitif, bonnes évaluations.

### Questions Techniques

**Q : Quels navigateurs sont supportés ?**
R : Chrome, Firefox, Safari, Edge (dernières versions).

**Q : Puis-je utiliser SEAOP sur mobile ?**
R : Oui, l'interface est responsive et s'adapte aux écrans mobiles.

**Q : Y a-t-il une API disponible ?**
R : API REST en développement, webhooks disponibles.

---

## 📞 SUPPORT ET CONTACT {#support-contact}

### Canaux de Support

#### Support Technique
- 📧 Email : support@seaop.gouv.qc.ca
- 📞 Téléphone : 1-866-SEAOP-01 (1-866-732-6701)
- 💬 Chat en ligne : Disponible 8h-17h EST

#### Support Commercial
- 📧 Email : ventes@seaop.gouv.qc.ca
- 📞 Téléphone : 1-866-SEAOP-02 (1-866-732-6702)

### Horaires de Support

| Service | Lundi-Vendredi | Samedi | Dimanche |
|---------|---------------|---------|----------|
| **Téléphone** | 8h-20h EST | 9h-17h | Fermé |
| **Email** | 24/7 (réponse < 24h) | 24/7 | 24/7 |
| **Chat** | 8h-17h EST | Fermé | Fermé |
| **Urgences** | 24/7 | 24/7 | 24/7 |

### Ressources Supplémentaires

#### Documentation
- 📚 [Guide de démarrage rapide](INSTRUCTIONS_DEMARRAGE.md)
- 🔧 [Guide technique](README.md)
- 🚀 [Guide de déploiement](RENDER_DEPLOYMENT.md)

#### Formation
- 🎥 Vidéos tutoriels sur YouTube
- 📖 Webinaires mensuels gratuits
- 🏫 Formation sur site disponible

#### Communauté
- 💬 Forum SEAOP : forum.seaop.gouv.qc.ca
- 🐦 Twitter : @SEAOP_Quebec
- 💼 LinkedIn : SEAOP Québec

### Signaler un Problème

#### Information à fournir :
1. **Description détaillée** du problème
2. **Étapes pour reproduire**
3. **Captures d'écran** si possible
4. **Navigateur** et version
5. **Système d'exploitation**
6. **Numéro de référence** du projet (si applicable)

### Suggestions et Améliorations

Nous sommes toujours à l'écoute !

**Envoyez vos suggestions à** :
- 📧 Email : ameliorations@seaop.gouv.qc.ca
- 📝 Formulaire en ligne : seaop.gouv.qc.ca/suggestions

---

## 📜 INFORMATIONS LÉGALES

### Conditions d'Utilisation
L'utilisation de SEAOP implique l'acceptation des conditions générales disponibles sur seaop.gouv.qc.ca/legal

### Protection des Données
Conforme à la Loi 25 sur la protection des renseignements personnels du Québec.

### Propriété Intellectuelle
© 2024 Gouvernement du Québec. Tous droits réservés.

---

## 🎯 CONCLUSION

SEAOP révolutionne la gestion des appels d'offres publics au Québec en offrant une plateforme moderne, sécurisée et efficace. 

**Points clés à retenir** :
- ✅ Interface intuitive et responsive
- ✅ Processus automatisés
- ✅ Communication intégrée
- ✅ Transparence totale
- ✅ Support disponible

**Commencez dès maintenant** :
1. Créez votre compte
2. Explorez les fonctionnalités
3. Publiez ou soumissionnez
4. Développez votre réseau

---

**Merci d'utiliser SEAOP !**

*Pour une administration publique moderne et efficace* 🏛️

---

*Version du manuel : 2.0.0*  
*Dernière mise à jour : Janvier 2024*  
*SEAOP - Système Électronique d'Appel d'Offres Public*