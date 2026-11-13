import os
import json
import requests
from dotenv import load_dotenv
from google import genai
from azure_storage import upload_match_data_to_azure

#Charge les variables d'environnement secrètes
load_dotenv()
football_api_key = os.getenv("RAPIDAPI_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialise le client Gemini
gemini_client = genai.Client(api_key=gemini_api_key)

# Récupére les matchs réels depuis l'API Football
url = "https://v3.football.api-sports.io/fixtures"
headers = {
    "x-apisports-key": football_api_key
}

# Date autorisée par votre forfait gratuit
parametres = {
    "date": "2026-11-05"
}

print("1. Récupération des données depuis l'API Foot...")
reponse = requests.get(url, headers=headers, params=parametres)

if reponse.status_code != 200:
    print(f"Erreur avec l'API Foot (Code {reponse.status_code})")
    exit()

data = reponse.json()
matchs = data.get("response", [])

if not matchs:
    print("Aucun match disponible pour cette date.")
    exit()

# Sélection du premier match retourné par l'API
match_choisi = matchs[0]

infos_match = {
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

nom_fichier_blob = f"match_{infos_match['fixture_id']}.json"
print(f"-> Affiche : {infos_match['equipe_domicile']} vs {infos_match['equipe_exterieur']}")

# Sauvegarder les données brutes sur Azure Blob Storage
print("\n2. Archivage des données sur Microsoft Azure Blob...")
upload_match_data_to_azure(nom_fichier_blob, infos_match)

# Génération de l'analyse avec Gemini
prompt = f"""
Tu es un analyste sportif et tactique expert en football.
Voici les informations réelles d'une rencontre extraites en direct :

- Compétition : {infos_match['competition']} ({infos_match['pays']})
- Affiche : {infos_match['equipe_domicile']} contre {infos_match['equipe_exterieur']}
- Statut du match : {infos_match['statut']}
- Score actuel ou final : {infos_match['buts_domicile']} - {infos_match['buts_exterieur']}

En te basant sur ces données et sur tes connaissances de ces clubs :
1. Présente brièvement les deux équipes (statut et style de jeu habituel).
2. Propose une analyse synthétique de cette affiche (ou un débrief si le match est terminé).
3. Donne un point clé tactique qui a fait ou ferait la différence.
"""

print("\n3. Envoi du contexte à Gemini pour analyse tactique...")
reponse_gemini = gemini_client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)

#Affichage du résultat final
print("\n" + "="*50)
print("RAPPORT COMPLET (DATA LAKE AZURE + IA)")
print("="*50)
print(reponse_gemini.text)