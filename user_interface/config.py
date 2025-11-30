from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env.docker")

class Settings:
    MCP_CLIENT_BASE_URL = os.getenv("MCP_CLIENT_BASE_URL")