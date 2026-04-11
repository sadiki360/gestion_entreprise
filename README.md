# 🚀 Plateforme de Gestion Entreprise Intelligente (ERP & BI)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-6.0-green.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Science-red.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

Une plateforme ERP (Enterprise Resource Planning) moderne, centralisée et intelligente, développée avec **Django** et enrichie d'un moteur d'**Intelligence Artificielle** natif. Ce projet couvre l'intégralité du cycle de vie commercial d'une entreprise : de la gestion des clients et des stocks à l'analyse prédictive et l'assistance conversationnelle (NLP).

---

## 🌟 Vision du Projet

Dans un environnement économique compétitif, la gestion manuelle (tableurs Excel, bases de données isolées) est un obstacle stratégique. Ce projet répond à la problématique en proposant une solution web capable non seulement de **stocker et d'afficher les données**, mais également de les **analyser**, les **prédire** et d'émettre des **recommandations automatiques** pour la prise de décision.

---

## 🧱 Architecture et Modules

L'architecture repose sur le patron **MVT (Modèle - Vue - Template)** de Django pour une séparation stricte des responsabilités. L'application est divisée en 5 modules interdépendants :

### 1. 📊 Dashboard (`dashboard`)
Le centre de contrôle général en temps réel.
* **KPIs temps réel :** Nombre de clients, ventes, produits et chiffre d'affaires global.
* **Graphiques temporels :** Histogrammes interactifs (via Chart.js) sur l'évolution des ventes des 7 derniers jours.
* **Notifications :** Alertes de ruptures de stock critiques pushées directement sur le panneau de contrôle.

### 2. 👥 Gestion de la Relation Client (`clients` - CRM)
Le socle relationnel de la plateforme.
* **CRUD Complet :** Création, lecture, modification et suppression sécurisée de fiches clients.
* **Intégrité :** Validation de données en temps réel (unicité des emails, formats conformes).

### 3. 📦 Logistique et Stocks (`stock`)
Gestion en temps réel de votre inventaire.
* **Catalogue dynamique :** Suivi des produits et des prix associés.
* **Système d'alertes :** Badges de statuts dynamiques et identification immédiate des stocks bas ou épuisés selon des seuils personnalisables.

### 4. 💳 Transactions Commerciales (`ventes`)
Historique et facturation.
* **Journalisation :** Enregistrement des ventes avec liaison aux fiches clients.
* **Impact direct :** Décrémentation automatique des stocks lors d'une transaction validée.
* **Export PDF :** Génération instantanée de reportings et factures via ReportLab.

### 5. 🧠 Moteur d'Intelligence Artificielle (`ai_engine`)
L'avantage comparatif du projet. Basé sur **Pandas** et **NumPy**.
* **Prédiction des ventes :** Modèle prédictif (Moyenne Mobile) évaluant le CA futur estimé de la semaine avec indice de fiabilité.
* **Segmentation Client RFM Automatique :** Évaluation de la valeur client selon Récence, Fréquence et Montant. Classification en 5 segments (VIP, Loyal, Nouveau, À réactiver, Inactif).
* **Marketing Ciblé :** Attribution automatique de promotions adaptées au segment RFM.
* **Recommandations logistiques :** Analyse et conseil ("Rupture: Commandez", "Stock Bas: Réapprovisionner", "Surplus: Envisager une promo").
* **Chatbot NLP :** Assistant virtuel intégré répondant en langage naturel aux requêtes des utilisateurs sur l'état des statistiques, des stocks ou des ventes du jour.

---

## 🛠️ Stack Technique

### Backend & Data Science
* **Python 3.11+**
* **Django 6.0** - Framework Web principal
* **Pandas & NumPy** - Algorithmes Data Science (Pipeline RFM, Séries temporelles)
* **SQLite / PostgreSQL** - Base de données

### Frontend
* **HTML5 / Vanilla CSS**
* **Bootstrap 5.3** - Grille responsive & Composants UI
* **Chart.js** - Visualisations de données
* **Bootstrap Icons** - Iconographie

### Déploiement & Outils Cloud
* **Railway** - Hébergement cloud
* **WhiteNoise** - Service de fichiers statiques
* **dj-database-url** - Gestion dynamique des connexions BDD
* **Gunicorn** - Serveur WSGI

---

## ⚙️ Installation et Déploiement Local

Assurez-vous d'avoir Python 3 installé sur votre machine.

### 1. Cloner le dépôt et préparer l'environnement
```bash
git clone https://github.com/votre-nom/gestion_entreprise.git
cd gestion_entreprise
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'environnement (.env)
Créez un fichier `.env` à la racine (au même niveau que `manage.py`) :
```env
DEBUG=True
SECRET_KEY=votre_clef_secrète_très_longue
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Initialiser la Base de Données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Créer un Super - Administrateur
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

Rendez-vous sur [`http://127.0.0.1:8000`](http://127.0.0.1:8000) et connectez-vous avec vos identifiants admin !

---

## ☁️ Modèle de Déploiement

Cette application est packagée pour être déployable sur la plateforme **Railway** très facilement.
1. Le fichier `runtime.txt` précise la version Python.
2. Le fichier `Procfile` commande `gunicorn core.wsgi:application --log-file -`.
3. `dj-database-url` va capter la base PostgreSQL ajoutée dans le projet Railway.

---

## 🚀 Perspectives et Intégrations Futures

1. **API REST Externe :** Développer un module `Django REST Framework` pour permettre à une application mobile (React Native/Flutter) de s'interfacer avec le système.
2. **Machine Learning Avancé :** Remplacer le modèle actuel par **Prophet** ou **ARIMA** pour des prédictions financières long-terme avec prise en compte des saisonsnalités.
3. **WebSockets (Django Channels) :** Push notifications instantanées lors d'une nouvelle vente ou rupture détectée, sans recharger la page.
4. **Gestion RH / Rôles :** Systématiser les droits d'accès avancés de l'entreprise (Admin, Vendeur, Gestionnaire de Stock).

---
*Projet développé dans le cadre de la construction d'une plateforme métier orientée Data & UX.*
