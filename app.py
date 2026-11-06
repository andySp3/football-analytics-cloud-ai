import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from azure_storage import upload_match_data_to_azure, get_match_data_from_azure

# Configuration générale de la page web
st.set_page_config(
    page_title="Premier League Predictor",
    page_icon="⚽",
    layout="wide"
)

# 1. Chargement des clés secrètes
load_dotenv()
football_api_key = os.getenv("RAPIDAPI_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialisation du client Gemini
gemini_client = genai.Client(api_key=gemini_api_key)

# -------------------------------------------------------------
# Fonction de récupération des matchs depuis l'API Football
# -------------------------------------------------------------
@st.cache_data(ttl=3600)  # Met en cache les données pendant 1 heure pour économiser les quotas
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": football_api_key}
    parametres = {"date": "2026-11-05"}
    
    try:
        response = requests.get(url, headers=headers, params=parametres)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

# -------------------------------------------------------------
# Interface utilisateur
# -------------------------------------------------------------
st.title("⚽ Dashboard Tactique & Analyses de Matchs")
st.markdown("Application connectée en direct à **API-Football**, **Azure Blob Storage** et **Google Gemini**.")

matchs = get_matches()

if not matchs:
    st.warning("Aucun match disponible pour cette date ou problème de quota d'API.")
else:
    # Création du dictionnaire pour le sélecteur : "Équipe Dom vs Équipe Ext" -> données du match
    options_matchs = {
        f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} ({m['league']['name']})": m
        for m in matchs
    }
    
    choix_label = st.selectbox("Sélectionnez une rencontre :", list(options_matchs.keys()))
    match_choisi = options_matchs[choix_label]
    
    # Extraction des informations du match sélectionné
    infos = {
        "fixture_id": match_choisi["fixture"]["id"],
        "date": match_choisi["fixture"]["date"],
        "competition": match_choisi["league"]["name"],
        "pays": match_choisi["league"]["country"],
        "equipe_domicile": match_choisi["teams"]["home"]["name"],
        "equipe_exterieur": match_choisi["teams"]["away"]["name"],
        "statut": match_choisi["fixture"]["status"]["long"],
        "buts_domicile": match_choisi["goals"]["home"],
        "buts_exterieur": match_choisi["goals"]["away"]
    }
    
    st.divider()
    
    # Affichage des informations clés sous forme de colonnes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Compétition", value=infos["competition"])
    with col2:
        score_text = f"{infos['buts_domicile']} - {infos['buts_exterieur']}" if infos['buts_domicile'] is not None else "À venir"
        st.metric(label="Score", value=score_text)
    with col3:
        st.metric(label="Statut du match", value=infos["statut"])
        
    st.divider()
    
    nom_blob = f"match_{infos['fixture_id']}.json"

    # Vérification dans Azure Blob Storage
    donnees_azure = get_match_data_from_azure(nom_blob)
    
    # CAS 1 : Le match ET l'analyse existent déjà sur Azure
    if donnees_azure and "analyse_ia" in donnees_azure:
        st.info("⚡ Données et analyse chargées instantanément depuis Azure Blob Storage (Cache Cloud actif).")
        st.subheader("Rapport d'analyse tactique (Archivé)")
        st.markdown(donnees_azure["analyse_ia"])
        
    # CAS 2 : Première analyse à générer
    else:
        st.caption("Ce match n'a pas encore été analysé par l'IA.")
        if st.button("Lancer l'analyse tactique IA", type="primary"):
            with st.spinner("Appel à Google Gemini et archivage sur Azure..."):
                prompt = f"""
                Tu es un analyste sportif et tactique expert en football.
                Voici les informations d'une rencontre :

                - Compétition : {infos['competition']} ({infos['pays']})
                - Rencontre : {infos['equipe_domicile']} contre {infos['equipe_exterieur']}
                - Statut : {infos['statut']}
                - Score : {infos['buts_domicile']} - {infos['buts_exterieur']}

                En te basant sur ces données et ton expertise :
                1. Présente brièvement les deux équipes et leur dynamique générale.
                2. Propose une analyse synthétique de cette affiche (ou un débriefing si terminée).
                3. Identifie le facteur tactique déterminant de la rencontre.
                """
                
                try:
                    reponse_gemini = gemini_client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=prompt
                    )
                    
                    # On stocke l'analyse IA directement avec les données du match
                    infos["analyse_ia"] = reponse_gemini.text
                    
                    # Sauvegarde finale du bundle complet dans Azure
                    upload_match_data_to_azure(nom_blob, infos)
                    
                    st.success("Analyse générée et synchronisée sur Azure Blob Storage !")
                    st.subheader("Rapport d'analyse tactique")
                    st.markdown(reponse_gemini.text)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la génération par l'IA : {e}")