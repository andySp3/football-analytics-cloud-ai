import os
import requests
from dotenv import load_dotenv
from google import genai

# 1. Charger les clés secrètes du fichier .env
load_dotenv()
football_api_key = os.getenv("RAPIDAPI_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialiser le client Gemini
gemini_client = genai.Client(api_key=gemini_api_key)

# -------------------------------------------------------------
# ÉTAPE A : Récupérer un vrai match depuis l'API Football
# -------------------------------------------------------------
url = "https://v3.football.api-sports.io/fixtures"
headers = {
    "x-apisports-key": football_api_key
}

# Date autorisée par votre forfait gratuit (fenêtre glissante)
parametres = {
    "date": "2026-11-05"
}

print("1. Interrogation de l'API Foot...")
reponse = requests.get(url, headers=headers, params=parametres)

if reponse.status_code != 200:
    print(f"Erreur avec l'API Foot (Code {reponse.status_code})")
    exit()

data = reponse.json()
matchs = data.get("response", [])

if not matchs:
    print("Aucun match disponible pour cette date.")
    exit()

# On sélectionne le premier match de la liste
match_choisi = matchs[0]

# On extrait les données propres de ce match
infos_match = {
    "competition": match_choisi["league"]["name"],
    "pays": match_choisi["league"]["country"],
    "equipe_domicile": match_choisi["teams"]["home"]["name"],
    "equipe_exterieur": match_choisi["teams"]["away"]["name"],
    "statut": match_choisi["fixture"]["status"]["long"],
    "buts_domicile": match_choisi["goals"]["home"],
    "buts_exterieur": match_choisi["goals"]["away"]
}

print(f"-> Match sélectionné : {infos_match['equipe_domicile']} vs {infos_match['equipe_exterieur']}")

# -------------------------------------------------------------
# ÉTAPE B : Injecter ces données réelles dans Gemini
# -------------------------------------------------------------
prompt = f"""
Tu es un analyste sportif et tactique expert en football.
Voici les informations réelles d'une rencontre extraites en direct via une API :

- Compétition : {infos_match['competition']} ({infos_match['pays']})
- Affiche : {infos_match['equipe_domicile']} contre {infos_match['equipe_exterieur']}
- Statut du match : {infos_match['statut']}
- Score actuel ou final : {infos_match['buts_domicile']} - {infos_match['buts_exterieur']}

En te basant sur ces données et sur tes connaissances de ces clubs :
1. Présente brièvement les deux équipes (leur statut et style de jeu habituel).
2. Propose une analyse synthétique de cette affiche (ou un débrief si le match est terminé).
3. Donne un point clé tactique qui a fait ou ferait la différence.
"""

print("2. Envoi des données réelles à Gemini...")
reponse_gemini = gemini_client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)

# -------------------------------------------------------------
# ÉTAPE C : Affichage du résultat final
# -------------------------------------------------------------
print("\n" + "="*40)
print("RAPPORT D'ANALYSE GÉNÉRÉ PAR L'IA")
print("="*40)
print(reponse_gemini.text)