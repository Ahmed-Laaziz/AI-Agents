import os
import json
import oracledb
from dotenv import load_dotenv
from pymongo import MongoClient
from fastmcp import FastMCP, Context
from config import Settings
import requests
import re
from collections import defaultdict
from tools.db_operations_tools import list_collections_fct, get_documents_fct
from typing import Optional
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Hybrid Database MCP Server")
EXTERNAL_API_BASE_URL = "http://localhost:8080/parc-admin/v1.3/companies"

# --- Connexion MongoDB ---
client = MongoClient(Settings.MONGODB_URI)
testim_api_key = Settings.TESTIM_API_KEY
TESTIM_API_BASE = "https://api.testim.io"
db = client["Testing_Platform_DB"]

# --- Connexion Oracle ---
connection = None # Initialiser à None

# ⚠️ Forcer l'initialisation du Mode Thick pour utiliser le client natif et éviter DPY-3015
try:
    # Le chemin est trouvé via LD_LIBRARY_PATH du Dockerfile
    oracledb.init_oracle_client() 
    print("✅ Mode Thick Oracle initialisé.")
except Exception as e:
    print(f"⚠️ Avertissement: Échec d'initialisation du mode Thick. Erreur: {e}")

try:
    dsn_tns = oracledb.makedsn("xxx.XXX.XXX", 1522, "xxxxxx")
    connection = oracledb.connect(user="mdl_xxxx", password="xxxxxxxxxxxxx", dsn=dsn_tns)
    print("✅ Connexion Oracle établie.")
except oracledb.DatabaseError as e:
    # Le script continue, mais l'outil Oracle sera non fonctionnel.
    print(f"❌ Erreur de connexion Oracle: Le serveur va démarrer, mais les outils Oracle ne fonctionneront pas. Message: {e.message}")
    
# --- Outils MCP ---

@mcp.tool()
def list_collections_oracle() -> list:
    """
    List all views in the specified Oracle database schema ('BASE_FRONT').
    """
    if connection is None:
        return ["Erreur: Connexion Oracle non disponible au démarrage du serveur."]

    # Gestion du curseur et des données (Votre logique est correcte)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT view_name FROM ALL_VIEWS WHERE owner = 'BASE_FRONT' ORDER BY view_name")
        results = cursor.fetchall()
        
        return [row[0] for row in results]
        
    except Exception as e:
        print(f"Erreur d'exécution de la requête Oracle: {e}")
        return [f"Erreur SQL Oracle: {e}"]
        
    finally:
        # Assurer que le curseur est toujours fermé
        cursor.close()

@mcp.tool()
async def get_documents(collection_name: str, limit: Optional[int] = 1, ctx: Context = None) -> list:
    """
    Retrieve documents from a specified MongoDB collection. (This tool targets MongoDB).
    """
    return await get_documents_fct(collection_name=collection_name, limit=limit, ctx=ctx, client=client)

@mcp.tool()
def get_first_row_mdl_societe() -> dict:
    """
    Retrieves the first row of data from the 'MDL_SOCIETE' view in the Oracle schema 'BASE_FRONT'.
    Returns the result as a dictionary with column names as keys.
    """
    if connection is None:
        return {"Erreur": "Connexion Oracle non disponible."}

    # ⚠️ REQUÊTE MODIFIÉE : Ajout de ORDER BY et WHERE pour obtenir une ligne valide
    sql_query = """
    SELECT *
    FROM BASE_FRONT.MDL_SOCIETE
    WHERE SOC_ETAT = 'A' -- S'assurer que la société est Active
    AND SOC_NOM IS NOT NULL -- S'assurer que le nom est présent
    ORDER BY SOC_MODIF DESC -- Trier par la plus récente modification (pour une ligne valide)
    FETCH FIRST 1 ROW ONLY -- Utiliser la syntaxe moderne au lieu de ROWNUM
    """

    try:
        # ... (le reste du code de connexion et de récupération des résultats) ...
        cursor = connection.cursor()
        cursor.execute(sql_query)
        
        columns = [col[0] for col in cursor.description]
        result = cursor.fetchone()
        
        if result:
            return dict(zip(columns, result))
        else:
            return {"MDL_SOCIETE": "Aucune ligne active avec un nom n'a été trouvée dans la vue."}
            
    except Exception as e:
        print(f"Erreur d'exécution de la requête sur MDL_SOCIETE: {e}")
        return {"Erreur SQL Oracle": str(e)}
        
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
@mcp.tool()
def get_company_details_from_parc_admin(soc_id: str) -> dict[str, Any]:
    """
    Appelle l'API externe Parc-Admin pour obtenir les détails de la société 
    en utilisant le SOC_ID (qui sert de CompanyId). Cet outil est conçu pour être
    chaîné après la récupération du SOC_ID via l'outil Oracle.

    :param soc_id: L'ID de la société (SOC_ID) à utiliser dans l'URL.
    :return: La réponse JSON de l'API externe ou un dictionnaire d'erreur.
    """
    if not soc_id:
        return {"Erreur": "Le SOC_ID est manquant pour l'appel API Parc-Admin."}
    
    # Construction de l'URL finale: http://.../companies/{soc_id}
    url = f"{EXTERNAL_API_BASE_URL}/{soc_id}"
    
    # Définition des headers requis par l'API externe
    headers = {
        "accept": "*/*",
        "WS-ConsoAuthent": "basic" # ⚠️ Assurez-vous que cette valeur est correcte et suffisante
    }

    try:
        # Exécution de la requête GET
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 

        # Retourne la réponse JSON de l'API externe
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        # Erreur côté serveur ou client HTTP (4xx ou 5xx)
        return {"Erreur Appel API": f"HTTP Error {http_err.response.status_code} sur {url}. Détails: {http_err.response.text}"}
    except requests.exceptions.RequestException as req_err:
        # Erreur de connexion (Timeout, DNS, etc.)
        return {"Erreur Connexion API": f"Impossible d'atteindre l'API {url}. Vérifiez le réseau/DNS : {req_err}"}
if __name__ == "__main__":
    print("🚀 Tentative de lancement du serveur FastMCP. Tous les outils ont été définis.")
    #print("voila la list : --->"+str(get_company_details_from_parc_admin('2324793')))
    mcp.run(
     transport="sse",
     host="0.0.0.0",
     port=5959, 
     log_level="info"
    )