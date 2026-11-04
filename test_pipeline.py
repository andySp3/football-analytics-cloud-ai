import os
from dotenv import load_dotenv
from google import genai

# Chargement des variables du fichier .env
load_dotenv()

# Initialisation du client Gemini
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Données simulées d'un match de Premier League
match_data = {
    "fixture": "Arsenal vs Chelsea",
    "competition": "Premier League",
    "arsenal": {
        "forme_5_derniers": "V-V-N-V-D",
        "moyenne_xg_marques": 2.1,
        "moyenne_xg_concedes": 0.8,
        "absents_majeurs": ["Bukayo Saka (incertain)"]
    },
    "chelsea": {
        "forme_5_derniers": "V-D-V-N-V",
        "moyenne_xg_marques": 1.7,
        "moyenne_xg_concedes": 1.4,
        "absents_majeurs": ["Reece James (blessé)"]
    },
    "historique_face_a_face": "Arsenal 3 victoires, Chelsea 1 victoire, 1 nul",
    "meteo": "Pluie légère, 9°C, pelouse glissante"
}

prompt = f"""
Tu es un analyste tactique expert de Premier League.
Analyse ces données pour le match {match_data['fixture']} :
{match_data}

Fournis une analyse synthétique en 3 points :
1. Dynamique récente des deux clubs.
2. Scénario tactique attendu.
3. Estimation sur les buts et xG.
"""

print("Envoi des données à Gemini...")
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)

print("\n--- RAPPORT D'ANALYSE ---")
print(response.text)