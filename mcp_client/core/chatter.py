from llama_index.tools.mcp import McpToolSpec
from core.client_factory import get_db_client
from core.offline_agent import get_agent
from llama_index.core.workflow import Context

# ----- LOAD ALL MCP TOOLS -----

async def load_all_mcp_tools():
    clients = [
        get_db_client(),
        # add more MCP clients...
    ]

    all_tools = []

    for client in clients:
        #await client.open()              # IMPORTANT
        spec = McpToolSpec(client=client)
        tools = await spec.to_tool_list_async()
        all_tools.extend(tools)

    return all_tools


# ----- BUILD AN OFFLINE AGENT + EXECUTE PROMPT -----

async def run_offline_agent(prompt: str, model_name: str):
    tools = await load_all_mcp_tools()

    agent = await get_agent(tools, model_name)
    agent_context = Context(agent)

    from core.offline_agent import handle_user_message
    response = await handle_user_message(prompt, agent, agent_context)

    return response