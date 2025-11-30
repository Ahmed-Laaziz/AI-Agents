from fastapi import APIRouter
from api.v1.endpoints import agent_routes

router = APIRouter()

router.include_router(agent_routes.router,prefix="/agent", tags=["Agent"])