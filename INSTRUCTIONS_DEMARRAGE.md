# 🚀 INSTRUCTIONS DE DÉMARRAGE SEAOP

## ⚡ **MÉTHODE RAPIDE (Recommandée)**

1. **Ouvrez l'invite de commandes** (Windows + R, tapez `cmd`)
2. **Naviguez vers le dossier** :
   ```
   cd C:\IA\SEAOP
   ```
3. **Lancez SEAOP** :
   ```
   py -m streamlit run app_v2.py
   ```

---

## 🔧 **SI LE SCRIPT .BAT NE FONCTIONNE PAS**

### **Étapes manuelles :**

1. **Initialiser la base de données** (première fois uniquement) :
   ```
   py init_db_v2.py
   ```

2. **Installer les dépendances** (première fois uniquement) :
   ```
   py -m pip install streamlit pandas pillow
   ```

3. **Lancer SEAOP** :
   ```
   py -m streamlit run app_v2.py
   ```

---

## 🌐 **Accès à SEAOP**

Une fois lancé, SEAOP sera accessible sur :
- **URL locale** : http://localhost:8501
- **URL réseau** : http://[votre-ip]:8501

---

## 🔑 **COMPTES DE DÉMONSTRATION**

### **Fournisseurs** (mot de passe: `demo123`)
- jean@construction-excellence.ca
- marie@toitures-pro.ca  
- pierre@renovations-modernes.ca

### **Administrateur**
- Mot de passe : `admin123`

---

## ❌ **RÉSOLUTION DE PROBLÈMES**

### **"Python n'est pas reconnu"**
```
# Vérifiez l'installation Python :
python --version
# ou
py --version

# Si ça ne fonctionne pas, réinstallez Python depuis python.org
# et cochez "Add Python to PATH"
```

### **"Module streamlit introuvable"**
```
py -m pip install streamlit pandas pillow
```

### **"Base de données introuvable"**
```
py init_db_v2.py
```

### **Port déjà utilisé**
```
py -m streamlit run app_v2.py --server.port 8502
```

---

## 🛑 **ARRÊTER SEAOP**

- **Dans le terminal** : Appuyez sur `Ctrl + C`
- **Fermer la fenêtre** du navigateur ne suffit pas
- **Fermer le terminal** arrête complètement SEAOP

---

## 📞 **SUPPORT**

Si aucune méthode ne fonctionne :
1. Vérifiez que Python 3.8+ est installé
2. Vérifiez que vous êtes dans le bon dossier `C:\IA\SEAOP`
3. Essayez la méthode manuelle ligne par ligne
4. Vérifiez les messages d'erreur dans le terminal