from typing import Any
from llama_index.core.workflow import Workflow, step, Context, StartEvent, Event, StopEvent
from llama_index.tools.mcp import McpToolSpec
from core.client_factory import get_db_client
from core.offline_agent import get_agent, handle_user_message
import json
import re

# ---- Events ----

class ToolsLoaded(Event):
    pass


class CompanyBaseLoaded(Event):
    pass


class CompanyDetailsLoaded(Event):
    pass


# ---- Workflow ----

class CompanyLookupWorkflow(Workflow):

    def __init__(self):
        super().__init__(timeout=120)

    # ---------------------------------------------------
    @step()
    async def load_tools(self, ctx: Context, ev: StartEvent) -> ToolsLoaded:
        """Load all MCP tools from your server."""
        ctx.model_name = getattr(ev, "model_name", None)

        client = get_db_client()
        spec = McpToolSpec(client=client)
        ctx.tools = await spec.to_tool_list_async()

        return ToolsLoaded()

    # ---------------------------------------------------
    @step()
    async def call_mdl_societe(self, ctx: Context, ev: ToolsLoaded) -> CompanyBaseLoaded:
        get_first_row = next(t for t in ctx.tools if t.metadata.name == "get_first_row_mdl_societe")
        tool_output = await get_first_row.acall()

        content_str = tool_output.content
        print("Raw Tool Output String:", repr(content_str))

        # Regex to extract SOC_ID
        match = re.search(r'"SOC_ID"\s*:\s*"([^"]+)"', content_str)
        if not match:
            raise ValueError("SOC_ID not found in tool output")
        
        soc_id = match.group(1)
        ctx.soc_id = soc_id
        print("Extracted SOC_ID:", soc_id)

        return CompanyBaseLoaded()
    # ---------------------------------------------------
    @step()
    async def call_parc_admin(self, ctx: Context, ev: CompanyBaseLoaded) -> CompanyDetailsLoaded:
        """Step 2 & 3: Call get_company_details_from_parc_admin(SOC_ID)."""

        get_company_details = next(t for t in ctx.tools if t.metadata.name == "get_company_details_from_parc_admin")

        ctx.company_details = await get_company_details.acall(soc_id=ctx.soc_id)

        return CompanyDetailsLoaded()

    # ---------------------------------------------------
    @step()
    async def agent_summary(self, ctx: Context, ev: CompanyDetailsLoaded) -> StopEvent:
        """Step 4: Ask LLM to write a human summary."""

        agent = await get_agent(ctx.tools, ctx.model_name)
        agent_ctx = Context(agent)

        prompt = (
            "You are an expert assistant with access to company information.\n\n"
            "Your task is to present the company information in a clear and human-friendly way.\n"
            "Do NOT mention JSON, tools, or technical structure.\n"
            "Speak naturally, as if you looked into our system yourself.\n\n"
            "Here is the information you found:\n"
            f"- Parc Admin Details: {ctx.company_details}\n\n"
            "Now summarize this company: name, status, address, and any other meaningful insights."
        )

        ctx.agent_output = await handle_user_message(prompt, agent, agent_ctx)

        return StopEvent({
            "soc_id": ctx.soc_id,
            "company_details": ctx.company_details,
            "summary": ctx.agent_output,
        })
