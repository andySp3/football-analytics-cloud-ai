import os
import requests
from dotenv import load_dotenv

# 1. Charger la clé secrète du fichier .env
load_dotenv()
api_key = os.getenv("RAPIDAPI_KEY")

url = "https://v3.football.api-sports.io/fixtures"

headers = {
    "x-apisports-key": api_key
}

# 2. On interroge la date du jour autorisée par le plan gratuit
parametres = {
    "date": "2026-11-05"  # Date autorisée par votre forfait
}

print("Appel de l'API Football (date autorisée : 2026-11-05)...")

reponse = requests.get(url, headers=headers, params=parametres)

if reponse.status_code == 200:
    data = reponse.json()
    matchs = data.get("response", [])
    
    if not matchs:
        print("Aucun match trouvé pour cette date.")
        print("Réponse brute :", data)
    else:
        print(f"\n--- {len(matchs)} MATCH(S) TROUVÉ(S) AUJOURD'HUI ---")
        # On affiche les 10 premières rencontres de la journée
        for match in matchs[:10]:
            competition = match["league"]["name"]
            pays = match["league"]["country"]
            equipe_dom = match["teams"]["home"]["name"]
            equipe_ext = match["teams"]["away"]["name"]
            statut = match["fixture"]["status"]["long"]
            print(f"[{pays} - {competition}] ⚽ {equipe_dom} vs {equipe_ext} ({statut})")
else:
    print(f"Erreur de connexion : Code {reponse.status_code}")
    print(reponse.text)