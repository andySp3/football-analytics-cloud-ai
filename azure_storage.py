import os
import json
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# 1. Charger la chaîne de connexion secrète depuis .env
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# 2. Nom du conteneur créé sur le portail Azure
CONTAINER_NAME = "pl-match-data"

def upload_match_data_to_azure(filename, data_dict):
    """Téléverse un dictionnaire Python sous forme de fichier JSON sur Azure Blob Storage."""
    try:
        # Initialiser la connexion au service Azure
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Récupérer l'accès au conteneur et définir le nom du blob (fichier distant)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        
        # Convertir les données en texte JSON formaté
        json_data = json.dumps(data_dict, ensure_ascii=False, indent=4)
        
        print(f"Téléversement de {filename} vers Azure Blob Storage...")
        # overwrite=True remplace le fichier s'il existe déjà
        blob_client.upload_blob(json_data, overwrite=True)
        print("-> Succès : Fichier archivé dans le Cloud !")
        
    except Exception as e:
        print(f"Erreur lors du transfert : {e}")

def get_match_data_from_azure(filename):
    """Vérifie si le fichier existe sur Azure. Si oui, le télécharge et renvoie le dictionnaire."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        
        # Vérifier si le blob existe sur le serveur Azure
        if blob_client.exists():
            stream = blob_client.download_blob()
            data_dict = json.loads(stream.readall().decode("utf-8"))
            return data_dict
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture sur Azure : {e}")
        return None

if __name__ == "__main__":
    # Test avec un petit objet factice pour valider la passerelle
    donnees_test = {
        "projet": "Premier League Predictor",
        "statut": "Connexion Azure Blob opérationnelle",
        "date_test": "2026-11-06"
    }
    upload_match_data_to_azure("test_connexion.json", donnees_test)