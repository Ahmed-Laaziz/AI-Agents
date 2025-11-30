from fastmcp import Client
from llama_index.tools.mcp import BasicMCPClient
from config import Settings

def get_db_client():
    return BasicMCPClient(Settings.MONGO_DB_BASE_URL)

def get_jira_client():
    return BasicMCPClient(Settings.MCP_BASE_URL)

def get_assistant_client():
    return Client(Settings.ASSISTANT_BASE_URL)