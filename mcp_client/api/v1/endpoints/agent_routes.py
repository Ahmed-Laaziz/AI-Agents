from fastapi import APIRouter
from models.schemas import PromptRequest
from core.orchestrator import run_offline_agent, load_all_mcp_tools
from core.utils import serialize_tool

router = APIRouter()


@router.post("/offline_agent")
async def ask_offline_agent(payload: PromptRequest):
    response = await run_offline_agent(
        prompt=payload.prompt,
        model_name=payload.model
    )
    return {"response": response}


@router.get("/get_tools")
async def list_tools():
    tools = await load_all_mcp_tools()
    return [serialize_tool(t) for t in tools]
