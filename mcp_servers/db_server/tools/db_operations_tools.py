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

def list_collections_fct(client: MongoClient) -> list:
    """
    List all collections in the specified database.
    """
    db = client["Testing_Platform_DB"]
    return db.list_collection_names()

async def get_documents_fct(collection_name: str, limit: int, client: MongoClient, ctx: Context = None) -> list:
    """
    Retrieve documents from a specified collection.
    """
    db = client["Testing_Platform_DB"]
    if ctx:
        await ctx.info(f"Fetching {limit} documents from collection: {collection_name}, and database : {db}")
    collection = db[collection_name]
    documents = list(collection.find().limit(limit))
    if ctx:
        await ctx.debug(f"Retrieved documents : {documents}")
    return [doc for doc in documents]
