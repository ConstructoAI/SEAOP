# 🚀 DÉPLOIEMENT SEAOP SUR RENDER

## 📋 **Configuration requise sur Render**

### **Paramètres de base :**

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `SEAOP` |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | *(laisser vide)* |

### **Commandes de build et démarrage :**

**Build Command :**
```bash
pip install -r requirements.txt
```

**Start Command :**
```bash
streamlit run app_v2.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

---

## 🔐 **VARIABLES D'ENVIRONNEMENT OBLIGATOIRES**

### **1. Mot de passe administrateur (SÉCURISÉ) :**

| Variable | Valeur | Description |
|----------|--------|-------------|
| `ADMIN_PASSWORD` | `[VOTRE_MOT_DE_PASSE_SÉCURISÉ]` | Mot de passe admin SEAOP |

**⚠️ IMPORTANT :** Remplacez par un mot de passe fort (ex: `SEAOP_2024_Admin_Secure!`)

### **2. Stockage persistant (OBLIGATOIRE) :**

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DATA_DIR` | `/opt/render/project/data` | Répertoire de stockage persistant |

### **3. Configuration Streamlit :**

| Variable | Valeur |
|----------|--------|
| `STREAMLIT_SERVER_HEADLESS` | `true` |
| `STREAMLIT_SERVER_ENABLE_CORS` | `false` |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | `false` |

---

## 💾 **CONFIGURATION STOCKAGE PERSISTANT**

### **Disque persistant (OBLIGATOIRE pour SEAOP) :**
- **Taille** : 10 GB (configuré)
- **Point de montage** : `/opt/render/project/data`
- **Usage** : Stockage de la base de données SQLite et fichiers uploadés

**⚠️ CRITIQUE :** Sans disque persistant, toutes les données SEAOP seraient perdues à chaque redéploiement !

### **Avantages du stockage persistant :**
- ✅ Conservation des appels d'offres et soumissions
- ✅ Persistance des comptes utilisateurs
- ✅ Sauvegarde des documents uploadés
- ✅ Historique complet des projets

---

## 💾 **Choix d'instance recommandé :**

### **Pour débuter :**
- **Starter** - $7/mois (512 MB RAM, 0.5 CPU)
- Parfait pour tests et utilisation modérée

### **Pour production :**
- **Standard** - $25/mois (2 GB RAM, 1 CPU)
- Recommandé pour utilisation professionnelle

---

## 🔧 **ÉTAPES DE CONFIGURATION SUR RENDER**

### **1. Paramètres de base :**
1. ✅ Name: `SEAOP`
2. ✅ Language: `Python 3`
3. ✅ Branch: `main`
4. ✅ Build Command: `pip install -r requirements.txt`
5. ✅ Start Command: `streamlit run app_v2.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

### **2. Variables d'environnement :**
1. Cliquez **"Add Environment Variable"**
2. Ajoutez **ADMIN_PASSWORD** avec votre mot de passe sécurisé
3. Ajoutez **DATA_DIR** avec la valeur `/opt/render/project/data`
4. Ajoutez les autres variables Streamlit

### **3. Déploiement :**
1. Cliquez **"Create Web Service"**
2. Attendez le build (5-10 minutes)
3. Votre SEAOP sera accessible sur `https://seaop-xxx.onrender.com`

---

## 🎯 **APRÈS LE DÉPLOIEMENT**

### **Accès administrateur :**
- URL : `https://votre-seaop.onrender.com`
- Navigation : ⚙️ Administration
- Mot de passe : Celui configuré dans `ADMIN_PASSWORD`

### **Comptes de démonstration :**
- **Fournisseurs** : `jean@construction-excellence.ca` (mot de passe: `demo123`)
- **Autres fournisseurs** : voir README_SEAOP.md

---

## 🔒 **SÉCURITÉ EN PRODUCTION**

### **Recommandations :**
1. ✅ **Mot de passe admin fort** (configuré via ADMIN_PASSWORD)
2. ✅ **HTTPS automatique** (fourni par Render)
3. ✅ **Variables d'environnement sécurisées** (non visibles dans le code)
4. ⚠️ **Changez les mots de passe de démonstration** pour la production

### **Optionnel - Ajout de sécurité :**
- Limitez l'accès par IP si nécessaire
- Configurez des backups réguliers de la base de données
- Surveillez les logs d'accès

---

## 📊 **SURVEILLANCE**

### **Render Dashboard :**
- CPU/RAM usage
- Logs en temps réel  
- Métriques de performance
- Gestion des déploiements

### **SEAOP Analytics :**
- Panel administrateur intégré
- Statistiques d'utilisation
- Gestion des utilisateurs

---

## 🆘 **DÉPANNAGE**

### **Erreurs courantes :**

**Build failed :**
- Vérifiez `requirements.txt`
- Logs de build disponibles sur Render

**App crash :**
- Vérifiez les variables d'environnement
- Consultez les logs d'application

**Accès admin impossible :**
- Vérifiez la variable `ADMIN_PASSWORD`
- Respectez la casse exacte

---

**🏛️ SEAOP déployé avec succès sur Render !**

URL d'accès : `https://seaop-[random].onrender.com`