from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env.docker")

class Settings:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
    MCP_BASE_URL = os.getenv("MCP_BASE_URL")
    MONGO_DB_BASE_URL = os.getenv("MONGO_DB_BASE_URL")