import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from fastmcp import FastMCP
from fastmcp import Context
from config import Settings
import requests
import re
from collections import defaultdict
from tools.db_operations_tools import list_collections_fct, get_documents_fct
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("MongoDB Atlas MCP Server")

# Connect to MongoDB Atlas
client = MongoClient(Settings.MONGODB_URI)
testim_api_key = Settings.TESTIM_API_KEY
TESTIM_API_BASE = "https://api.testim.io"
db = client["Testing_Platform_DB"]

@mcp.tool()
def list_collections() -> list:
    """
    List all collections in the specified database.
    """
    return db.list_collection_names(client=client)

@mcp.tool()
async def get_documents(collection_name: str, limit: Optional[int] = 1, ctx: Context = None) -> list:
    """
    Retrieve documents from a specified collection.
    """
    return await get_documents_fct(collection_name=collection_name, limit=limit, ctx=ctx, client=client)

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=5959, 
        log_level="info"
    )