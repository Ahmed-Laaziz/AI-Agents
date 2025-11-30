from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings as LlamaSettings
from config import Settings as AppSettings
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = """\
"You are a helpful AI assistant connected to MongoDB and MCP tools. "
        "Always attempt to use the available tools to answer questions about the database, test execution"
        "permissions, collections, or documents. If you cannot answer directly, call the appropriate tool."
        "if you want to get data from our database refer always to the right collection for instance for assets data refert to assets collection, consumers collection for accounts, cases collection for cases then call get_documents tool with the correct collection name to fetch the data you need to answer the user question dont include any additional parameter if no relevant data is found just tell the user."
        "dont tell the user the tools you are calling just relevant data for him"
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
