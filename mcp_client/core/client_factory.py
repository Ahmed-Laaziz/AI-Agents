from fastmcp import Client
from llama_index.tools.mcp import BasicMCPClient
from config import Settings

def get_db_client():
    return BasicMCPClient(Settings.MONGO_DB_BASE_URL)
