from typing import Any
from llama_index.core.workflow import Workflow, step, Context, StartEvent, Event, StopEvent
from llama_index.tools.mcp import McpToolSpec
from core.client_factory import get_db_client
from core.offline_agent import get_agent, handle_user_message
import os

# --- Événements Spécifiques au Flux de Travail ---

class ToolsLoaded(Event):
    """Indique que les outils du serveur MCP ont été découverts."""
    pass

class CompanyIDFetched(Event):
    """Indique que le SOC_ID a été récupéré d'Oracle."""
    pass

# --- Le Flux de Travail ---

class OracleApiWorkflow(Workflow):
    """
    Workflow pour chaîner la récupération du SOC_ID depuis Oracle
    et l'appel d'une API externe Parc-Admin.
    """

    def __init__(self):
        # Augmenter le timeout pour laisser le temps au LLM et aux API de répondre
        super().__init__(timeout=300)

    @step()
    async def load_tools(self, ctx: Context, ev: StartEvent) -> ToolsLoaded:
        """Découvre tous les outils exposés par le serveur MCP (Oracle/API)."""
        
        # Récupère le nom du modèle LLM depuis l'événement de démarrage
        ctx.model_name = getattr(ev, "model_name", "mistral") 

        client = get_db_client()
        spec = McpToolSpec(client=client)
        # Liste tous les outils disponibles (y compris les deux nouveaux)
        ctx.tools = await spec.to_tool_list_async()
        
        return ToolsLoaded()

    @step()
    async def execute_tool_chain(self, ctx: Context, ev: ToolsLoaded) -> StopEvent:
        """
        Exécute la chaîne d'outils Oracle -> LLM -> API Externe.
        L'Agent LLM est responsable de déterminer l'ordre.
        """
        
        # 1. Instanciation de l'Agent LLM
        agent = await get_agent(ctx.tools, ctx.model_name)
        agent_ctx = Context(agent)

        # 2. Définition du Prompt de Chaînage
        # Le prompt guide l'agent à utiliser les deux outils dans l'ordre.
        prompt = """
Exécution forcée du workflow :

1. Appelle get_first_row_mdl_societe.
2. Récupère SOC_ID.
3. Appelle get_company_details_from_parc_admin(SOC_ID).
4. Retourne uniquement : 
   - Le nom de la société
   - Le statut
Aucune explication. Aucun code. Seulement la réponse finale.
"""


        # 3. Exécution de l'Agent (qui gère la séquence des outils)
        ctx.final_response = await handle_user_message(prompt, agent, agent_ctx)

        # 4. Terminaison du Workflow avec la réponse de l'agent
        return StopEvent({
            "status": "Chaîne d'outils terminée avec succès.",
            "final_answer": ctx.final_response,
        })