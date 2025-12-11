from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings as LlamaSettings
from config import Settings as AppSettings
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = """\
"Tu es un agent MCP orchestrateur. 
TU N’AS PAS LE DROIT d’écrire du code, ni d’expliquer comment utiliser les outils.

TU DOIS OBLIGATOIREMENT utiliser les outils disponibles pour répondre.
Pour toute question concernant Oracle, Parc-Admin, Mongo, ou les données métier :
→ Appelle immédiatement le tool approprié.
→ NE FOURNIS AUCUNE DESCRIPTION DU PROCESSUS.
→ NE FOURNIS PAS DE CODE.

Dans le workflow OracleApiWorkflow :
1. Appelle get_first_row_mdl_societe.
2. Extrait SOC_ID.
3. Appelle get_company_details_from_parc_admin avec ce SOC_ID.
4. Retourne UNIQUEMENT la réponse finale (Nom société + Statut).
"""



async def get_agent(all_tools, model_name):
    # Set global LLM
    model = Ollama(
        model=model_name,
        request_timeout=1000,
        base_url=AppSettings.OLLAMA_BASE_URL,
        context_window=1000
    )
    LlamaSettings.model = model
    return FunctionAgent(
        name="Agent",
        description="An agent that can do Anything.",
        tools=all_tools,
        llm=model,
        system_prompt=SYSTEM_PROMPT,
    )

async def handle_user_message(message: str, agent: FunctionAgent, agent_context: Context, verbose=True):
    handler = agent.run(message, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned {event.tool_output}")
    response = await handler
    print("final response:", response)
    return str(response)
