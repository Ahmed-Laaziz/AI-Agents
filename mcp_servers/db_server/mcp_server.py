import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from fastmcp import FastMCP
from fastmcp import Context
from config import Settings
import requests
import re
from collections import defaultdict
from tools.db_operations_tools import list_collections_fct, get_documents_fct
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("MongoDB Atlas MCP Server")

# Connect to MongoDB Atlas
client = MongoClient(Settings.MONGODB_URI)
testim_api_key = Settings.TESTIM_API_KEY
TESTIM_API_BASE = "https://api.testim.io"
db = client["Testing_Platform_DB"]

@mcp.tool()
def list_collections() -> list:
    """
    List all collections in the specified database.
    """
    return db.list_collection_names(client=client)

@mcp.tool()
async def get_documents(collection_name: str, limit: Optional[int] = 1, ctx: Context = None) -> list:
    """
    Retrieve documents from a specified collection.
    """
    return await get_documents_fct(collection_name=collection_name, limit=limit, ctx=ctx, client=client)

@mcp.tool()
def get_first_row_mdl_societe() -> dict:
    """
    Simule la récupération de la première ligne de 'BASE_FRONT.MDL_SOCIETE'
    avec des données non sensibles pour le développement et le test.
    """
    print("⚠️ MOCK ACTIF : Simulation de la récupération Oracle.")
    
    # Données statiques qui imitent le résultat d'une requête Oracle réussie
    mock_data = {
        "SOC_ID": "SOCIETE_TEST_123",  # Crucial pour le chaînage
        "SOC_NOM": "Société Alpha Test",
        "SOC_SIREN": "123456789",
        "SOC_ETAT": "A",
        "SOC_MODIF": "2024-01-15 10:30:00"
    }
    
    # Simuler le cas d'erreur de connexion si besoin (non inclus ici pour un mock de succès)
    # if connection is None:
    #     return {"Erreur": "Connexion Oracle non disponible (MOCK non implémenté pour l'erreur)."}

    # Simuler le cas où aucune ligne n'est trouvée
    # return {"MDL_SOCIETE": "Aucune ligne active avec un nom n'a été trouvée dans la vue."}
    
    return mock_data

@mcp.tool()
def get_company_details_from_parc_admin(soc_id: str) -> dict[str, any]:
    """
    Simule l'appel à l'API externe Parc-Admin pour obtenir les détails de la société.
    Retourne des données statiques (mockées) pour le développement et le test.

    :param soc_id: L'ID de la société (SOC_ID) à utiliser dans l'URL (pour la trace).
    :return: Une réponse JSON (dictionnaire) statique ou une erreur si soc_id est vide.
    """
    print(f"⚠️ MOCK ACTIF : Simulation d'appel API Parc-Admin pour SOC_ID: {soc_id}")
    
    if not soc_id:
        return {"Erreur": "Le SOC_ID est manquant pour l'appel API Parc-Admin (MOCK)."}
    
    # Données statiques qui imitent le JSON retourné par l'API
    mock_api_response = {
        "CompanyId": soc_id,
        "CompanyName": "Alpha Test SARL",
        "Address": "123 Rue de la Simulation, 75000 Paris",
        "ContactEmail": "contact@mock-societe.com",
        "Status": "Active",
        "API_Simulated_Source": "Parc-Admin-Mock-V1.0"
    }

    # Vous pouvez simuler des erreurs API spécifiques si nécessaire pour vos tests:
    # if soc_id == "ERROR_404":
    #     return {"Erreur Appel API": f"HTTP Error 404 sur {url}. Détails: Not Found"}
    
    return mock_api_response

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=5959, 
        log_level="info"
    )