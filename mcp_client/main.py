from fastapi import FastAPI
from api.v1.routes import router
import uvicorn

app = FastAPI(title="MCP Client API")
app.include_router(router, prefix="/api/v1")

# ⚠️ AJOUT CRITIQUE POUR DÉMARRER LE SERVEUR
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5353, 
        log_level="info",
        reload=False # Mettez à True pour le développement local, False dans Docker
    )