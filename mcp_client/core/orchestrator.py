from typing import Any
from llama_index.core.workflow import Workflow, step, Context, StartEvent, Event, StopEvent
from llama_index.tools.mcp import McpToolSpec
from core.client_factory import get_db_client
from core.offline_agent import get_agent, handle_user_message
import os

class ToolsLoaded(Event):
    pass

class DataFetched(Event):
    pass

class HybridWorkflow(Workflow):

    def __init__(self):
        # increase timeout (default = 10s → too short)
        super().__init__(timeout=120)

    @step()
    async def load_tools(self, ctx: Context, ev: StartEvent) -> ToolsLoaded:
        ctx.model_name = getattr(ev, "model_name", None)

        client = get_db_client()
        spec = McpToolSpec(client=client)
        ctx.tools = await spec.to_tool_list_async()
        return ToolsLoaded()

    @step()
    async def fetch_mandatory_data(self, ctx: Context, ev: ToolsLoaded) -> DataFetched:
        list_collections = next(t for t in ctx.tools if t.metadata.name == "list_collections")
        get_documents = next(t for t in ctx.tools if t.metadata.name == "get_documents")

        ctx.collections = await list_collections.acall()
        ctx.assets = await get_documents.acall(collection_name="assets", limit=100)
        return DataFetched()

    @step()
    async def agent_reasoning(self, ctx: Context, ev: DataFetched) -> StopEvent:
        agent = await get_agent(ctx.tools, ctx.model_name)
        agent_ctx = Context(agent)

        prompt = (
            f"You are an expert Test Data Consultant. Your job is to give clear, "
            f"human-like summaries to stakeholders.\n"
            f"\n"
            f"STYLE GUIDELINES:\n"
            f"1. DO NOT mention 'JSON', 'provided data', 'analyzing the file', or technical structures.\n"
            f"2. Speak naturally, as if you just looked into the system yourself.\n"
            f"3. Start directly with the insights. Example: 'Currently, we have 50 assets available...'\n"
            f"\n"
            f"CONTEXT DATA:\n"
            f"{ctx.assets}\n"
            f"\n"
            f"TASK:\n"
            f"Based on the context above, analyze the assets and provide statistics."
        )
        ctx.agent_output = await handle_user_message(prompt, agent, agent_ctx)

        return StopEvent({
            "collections": ctx.collections,
            "assets": ctx.assets,
            "agent_output": ctx.agent_output,
        })
