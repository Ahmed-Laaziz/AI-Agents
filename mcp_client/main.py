from fastapi import FastAPI
from api.v1.routes import router
import uvicorn

app = FastAPI(title="MCP Client API")
app.include_router(router, prefix="/api/v1")