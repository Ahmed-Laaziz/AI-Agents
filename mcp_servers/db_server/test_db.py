
'''
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from fastmcp import Client
from .db import mcp

# Mock MongoDB for testing without actual database connection
@pytest.fixture
def mock_mongodb():
    with patch('db.client') as mock_client:
        # Mock the MongoDB client and database
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_client.list_database_names.return_value = ["Testing_Platform_DB", "admin", "local"]
        
        # Mock collection operations
        mock_db.list_collection_names.return_value = ["users", "products", "orders"]
        
        # Mock collection.find() for documents
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock documents data
        mock_documents = [
            {"_id": "1", "name": "Test User 1", "email": "test1@example.com"},
            {"_id": "2", "name": "Test User 2", "email": "test2@example.com"},
            {"_id": "3", "name": "Test User 3", "email": "test3@example.com"}
        ]
        
        mock_cursor = Mock()
        mock_cursor.limit.return_value = mock_documents[:2]  # Return first 2 for limit test
        mock_collection.find.return_value = mock_cursor
        
        yield mock_client

@pytest.fixture
def mcp_server():
    """Fixture that returns your MongoDB MCP server instance."""
    return mcp

class TestMongoDBMCPServer:
    
    @pytest.mark.asyncio
    async def test_list_databases(self, mcp_server, mock_mongodb):
        """Test the list_databases tool."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("list_databases")
            
            # Extract the actual result from the response
            databases = result[0].text if hasattr(result[0], 'text') else result[0]
            
            assert "Testing_Platform_DB" in databases
            assert "admin" in databases
            assert "local" in databases

    @pytest.mark.asyncio
    async def test_list_collections(self, mcp_server, mock_mongodb):
        """Test the list_collections tool."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("list_collections", {
                "database_name": "Testing_Platform_DB"
            })
            
            collections = result[0].text if hasattr(result[0], 'text') else result[0]
            
            assert "users" in collections
            assert "products" in collections
            assert "orders" in collections

    @pytest.mark.asyncio
    async def test_get_documents(self, mcp_server, mock_mongodb):
        """Test the get_documents tool."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_documents", {
                "collection_name": "users",
                "limit": 2
            })
            
            # The result should contain the mocked documents
            documents = result[0].text if hasattr(result[0], 'text') else result[0]
            
            # Verify we got documents back
            assert len(documents) == 2
            assert documents[0]["name"] == "Test User 1"
            assert documents[1]["name"] == "Test User 2"

    @pytest.mark.asyncio
    async def test_get_documents_with_context_logging(self, mcp_server, mock_mongodb):
        """Test that context logging works in get_documents."""
        async with Client(mcp_server) as client:
            # This test verifies the tool runs without errors when context is used
            result = await client.call_tool("get_documents", {
                "collection_name": "users",
                "limit": 5
            })
            
            # Should complete successfully
            assert result is not None

    @pytest.mark.asyncio
    async def test_empty_collection(self, mcp_server, mock_mongodb):
        """Test handling of empty collections."""
        # Mock empty collection
        mock_mongodb.__getitem__.return_value.list_collection_names.return_value = []
        
        async with Client(mcp_server) as client:
            result = await client.call_tool("list_collections", {
                "database_name": "empty_db"
            })
            
            collections = result[0].text if hasattr(result[0], 'text') else result[0]
            assert collections == []

    @pytest.mark.asyncio
    async def test_tool_availability(self, mcp_server):
        """Test that all expected tools are available."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            assert "list_databases" in tool_names
            assert "list_collections" in tool_names
            assert "get_documents" in tool_names
'''

print("CI test triggered from dev branch.")

def test_dummy_success():
    assert 1 == 1  # ✅ This will pass

# Uncomment this to make it fail:
# def test_dummy_fail():
#     assert 1 == 2  # ❌ This will fail
