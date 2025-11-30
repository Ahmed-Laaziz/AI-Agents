from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

class Settings:
    MONGODB_URI = os.getenv("MONGODB_URI")
    TESTIM_API_KEY = os.getenv("TESTIM_API_KEY")