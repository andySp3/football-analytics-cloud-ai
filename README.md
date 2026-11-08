# ⚽ Football AI Tactics & Match Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://football-ai-predictor-andy-gffuasgcgke2d4b8.spaincentral-01.azurewebsites.net)
[![Azure](https://img.shields.io/badge/Azure-App%20Service%20%7C%20Blob%20Storage-0078D4?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%203.1%20Flash%20Lite-8E75B2?logo=google&logoColor=white)](https://ai.google.dev/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

Plateforme web interactive d'analyse sportive et tactique automatisée. L'application agrège en temps réel les données de rencontres de football via une API externe, stocke et met en cache les résultats sur un Data Lake **Microsoft Azure Blob Storage**, et produit des analyses tactiques contextualisées à l'aide du modèle **Google Gemini**.

🔗 **Démo en ligne :** [Accéder à l'application déployée sur Azure](https://football-ai-predictor-andy-gffuasgcgke2d4b8.spaincentral-01.azurewebsites.net)[cite: 1, 11]

---

## 🏗️ Architecture du Système

Le projet relie une suite de services cloud et d'APIs dans un pipeline robuste de bout en bout :

```text
[ API-Football ] 
       │ (Flux JSON en temps réel)
       ▼
[ Streamlit Web App ] ──(Vérification cache)──► [ Azure Blob Storage ]
       │                                               │
       │ (Si non archivé)                              │ (Si archivé : lecture directe)
       ▼                                               │
[ Google Gemini 3.1 ]                                  │
       │                                               │
       ▼                                               │
[ Analyse tactique ] ───(Archivage persistant)─────────┘
       │
       ▼
[ Azure App Service ] ◄──(Déploiement continu CI/CD)── [ GitHub Actions ]
```

1. **Ingestion des données :** Récupération automatique des rencontres du jour (scores, compétitions, statuts, logos officiels) via l'API REST API-Football.
2. **Stratégie de Cache Cloud (Azure Blob Storage) :** Avant tout appel IA, l'application vérifie si le rapport du match est déjà présent dans le conteneur cloud (`pl-match-data`). Si oui, il est chargé instantanément sans consommer de requête d'API ni de quota LLM.
3. **Moteur d'Analyse (Google Gemini 3.1 Flash Lite) :** Génération d'une synthèse tactique neutre et structurée (forces en présence, scénario de match, clé de la rencontre) basée sur les faits réels.
4. **Hébergement & Intégration Continue :** Déploiement automatisé sur Azure App Service via GitHub Actions à chaque `git push` sur la branche `main`.

---

## 🛠️ Stack Technique

* **Langage :** Python 3.11+
* **Frontend :** Streamlit
* **Cloud & Stockage :** Microsoft Azure (App Service, Azure Blob Storage SDK)
* **Intelligence Artificielle :** Google GenAI SDK (`gemini-3.1-flash-lite`)
* **Source de Données :** API-Sports (API-Football)
* **DevOps / CI-CD :** GitHub Actions, Git

---

## 🚀 Installation et Lancement Local

### Prérequis
* Python 3.11 ou supérieur installé
* Clés d'API pour API-Football et Google AI Studio
* Chaîne de connexion vers un compte Azure Storage valide
    
### Configuration

1. **Cloner le projet :**
```bash
git clone https://github.com/andySp3/football-analytics-cloud-ai.git
cd football-analytics-cloud-ai
```

2. **Créer et activer un environnement virtuel :**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement :**
Créez un fichier `.env` à la racine du projet avec les variables suivantes :
```env
RAPIDAPI_KEY="votre_cle_api_football"
GEMINI_API_KEY="votre_cle_google_gemini"
AZURE_STORAGE_CONNECTION_STRING="votre_chaine_de_connexion_azure"
```

5. **Démarrer l'application :**
```bash
streamlit run app.py
```
L'application sera accessible sur http://localhost:8501.