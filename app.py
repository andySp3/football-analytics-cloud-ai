import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from azure_storage import upload_match_data_to_azure, get_match_data_from_azure
import datetime

# Configuration générale de la page web
st.set_page_config(
    page_title="Football AI Tactics & Match Analytics",
    layout="wide"
)

# Chargement des clés secrètes
load_dotenv()
football_api_key = os.getenv("RAPIDAPI_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialisation du client Gemini
gemini_client = genai.Client(api_key=gemini_api_key)

# Récupération des données depuis l'API Football (uniquement les matchs du jour)
@st.cache_data(ttl=3600)
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": football_api_key}
    date_du_jour = datetime.date.today().strftime("%Y-%m-%d")
    parametres = {"date": date_du_jour}
    
    try:
        response = requests.get(url, headers=headers, params=parametres)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

# Interface utilisateur
st.title("Dashboard Tactique & Analyses de Matchs")

# Affichage de la date du jour
date_affichage = datetime.date.today().strftime("%d/%m/%Y")
st.caption(f"**Matchs du jour ({date_affichage})** | Application connectée en direct à **API-Football**, **Azure Blob Storage** et **Google Gemini**.")

matchs = get_matches()

if not matchs:
    st.warning(f"Aucun match disponible pour la date du jour ({date_affichage}) ou problème de quota d'API.")
else:
    st.info(f"Ce tableau de bord prend en compte uniquement les rencontres programmées ou jouées aujourd'hui ({date_affichage}).")

    # Sélecteur de rencontre
    options_matchs = {
        f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} ({m['league']['name']})": m
        for m in matchs
    }
    
    choix_label = st.selectbox("Sélectionnez une rencontre du jour :", list(options_matchs.keys()))
    match_choisi = options_matchs[choix_label]
    
    # Données extraites
    infos = {
        "fixture_id": match_choisi["fixture"]["id"],
        "date": match_choisi["fixture"]["date"],
        "competition": match_choisi["league"]["name"],
        "pays": match_choisi["league"]["country"],
        "competition_logo": match_choisi["league"].get("logo"),
        "equipe_domicile": match_choisi["teams"]["home"]["name"],
        "logo_domicile": match_choisi["teams"]["home"]["logo"],
        "equipe_exterieur": match_choisi["teams"]["away"]["name"],
        "logo_exterieur": match_choisi["teams"]["away"]["logo"],
        "statut": match_choisi["fixture"]["status"]["long"],
        "buts_domicile": match_choisi["goals"]["home"],
        "buts_exterieur": match_choisi["goals"]["away"]
    }
    
    st.divider()

    # Carte de match style Google
    score_display = (
        f"{infos['buts_domicile']}  -  {infos['buts_exterieur']}"
        if infos["buts_domicile"] is not None
        else "vs"
    )

    with st.container():
        # En-tête : Compétition et Statut
        col_top_left, col_top_right = st.columns([3, 1])
        with col_top_left:
            st.markdown(f"**{infos['competition']}** · {infos['pays']}")
        with col_top_right:
            st.markdown(f"<div style='text-align: right; color: #888;'><b>{infos['statut']}</b></div>", unsafe_allow_html=True)
            
        st.write("")

        # Corps : [Équipe Domicile] [Score] [Équipe Extérieur]
        col_home, col_score, col_away = st.columns([2, 1, 2])
        
        with col_home:
            st.image(infos["logo_domicile"], width=65)
            st.subheader(infos["equipe_domicile"])
            
        with col_score:
            st.markdown(
                f"<h1 style='text-align: center; margin: 0; font-size: 2.8rem;'>{score_display}</h1>",
                unsafe_allow_html=True
            )
            
        with col_away:
            st.image(infos["logo_exterieur"], width=65)
            st.subheader(infos["equipe_exterieur"])
            
    st.divider()
    
    # Logique Azure Blob Storage & Gemini
    nom_blob = f"match_{infos['fixture_id']}.json"
    donnees_azure = get_match_data_from_azure(nom_blob)
    
    # CAS 1 : Présent dans le Cache Cloud Azure
    if donnees_azure and "analyse_ia" in donnees_azure:
        st.info("⚡ Données et analyse chargées instantanément depuis Azure Blob Storage (Cache Cloud actif).")
        st.subheader("Rapport d'analyse tactique (Archivé)")
        st.markdown(donnees_azure["analyse_ia"])
        
    # CAS 2 : Première analyse
    else:
        st.caption("Ce match n'a pas encore été analysé par l'IA.")
        if st.button("Lancer l'analyse tactique IA", type="primary"):
            with st.spinner("Archivage sur Azure Blob Storage et analyse tactique en cours..."):
                prompt = f"""
                Tu es un analyste tactique expert en football.
                Voici les faits officiels d'une rencontre :

                - Compétition : {infos['competition']} ({infos['pays']})
                - Rencontre : {infos['equipe_domicile']} contre {infos['equipe_exterieur']}
                - Statut actuel : {infos['statut']}
                - Score enregistré : {infos['buts_domicile']} - {infos['buts_exterieur']}

                Consignes impératives :
                1. Analyse la physionomie tactique et le scénario du match au vu du score et du statut (ex: match fermé, domination territoriale, efficacité sur transition rapide).
                2. Décris la confrontation des styles de jeu de ces deux clubs (ex: bloc bas, jeu direct, pressing haut) de manière analytique.
                3. Identifie le facteur clé qui fait ou ferait basculer cette rencontre.
                4. RÈGLE STRICTE : Ne cite aucun nom d'entraîneur, de manager ou de composition d'équipe pour garantir la neutralité temporelle de l'analyse. Concentre-toi à 100% sur le jeu et les clubs.
                """
                
                try:
                    reponse_gemini = gemini_client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=prompt
                    )
                    
                    # Stockage de l'analyse avec les métadonnées
                    infos["analyse_ia"] = reponse_gemini.text
                    upload_match_data_to_azure(nom_blob, infos)
                    
                    st.success("Analyse générée et synchronisée sur Azure Blob Storage !")
                    st.subheader("Rapport d'analyse tactique")
                    st.markdown(reponse_gemini.text)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la génération par l'IA : {e}")