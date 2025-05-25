"""Tests for the JSON-RPC handler."""

import pytest
from unittest.mock import Mock

from mojentic_mcp.rpc import JsonRpcHandler, JsonRpcRequest, JsonRpcErrorCode
from mojentic.llm.tools.llm_tool import LLMTool


@pytest.fixture
def mock_tool():
    """Create a mock tool for testing."""
    mock_tool = Mock(spec=LLMTool)
    mock_tool.run.return_value = {
        "status": "success",
        "documentation": "# Test Documentation",
        "modules_found": 5
    }
    mock_tool.descriptor = {
        "type": "function",
        "function": {
            "name": "examine",
            "description": "Examine a Python codebase and generate documentation",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to examine"
                    },
                    "format_type": {
                        "type": "string",
                        "description": "Output format (markdown, html, etc.)"
                    }
                },
                "required": ["directory"]
            }
        }
    }

    return mock_tool


class DescribeJsonRpcHandler:
    """Tests for the JsonRpcHandler class."""

    def should_be_instantiated(self, mock_tool):
        """Test that JsonRpcHandler can be instantiated."""
        handler = JsonRpcHandler(tools=[mock_tool])

        assert isinstance(handler, JsonRpcHandler)
        assert handler.should_exit is False
        assert len(handler.methods) > 0
        assert handler.tools == [mock_tool]

    def should_handle_initialize_request(self, mock_tool):
        """Test handling of initialize request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=1,
            method="initialize",
            params={
                "protocolVersion": "2025-03-26",
                "capabilities": {}
            }
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "serverInfo" in response["result"]
        assert "capabilities" in response["result"]
        assert response["result"]["protocolVersion"] == "2025-03-26"

    def should_handle_tools_list_request(self, mock_tool):
        """Test handling of tools/list request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=8,
            method="tools/list",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 8
        assert "result" in response
        assert "tools" in response["result"]
        assert isinstance(response["result"]["tools"], list)
        assert len(response["result"]["tools"]) == 1
        # With only one tool and page size of 10, nextCursor should not be present
        assert "nextCursor" not in response["result"]

        # Verify the examine tool is in the list
        examine_tool = response["result"]["tools"][0]
        assert examine_tool["name"] == "examine"
        assert "description" in examine_tool
        assert "inputSchema" in examine_tool

    def should_handle_tools_list_request_with_pagination(self, mock_tool):
        """Test handling of tools/list request with pagination."""
        # Create multiple mock tools for pagination testing
        mock_tools = []
        for i in range(15):  # Create 15 tools to test pagination (more than page size of 10)
            tool = Mock(spec=LLMTool)
            tool.descriptor = {
                "function": {
                    "name": f"tool_{i}",
                    "description": f"Tool {i} description",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
            mock_tools.append(tool)

        handler = JsonRpcHandler(tools=mock_tools)

        # First page request (no cursor)
        request1 = JsonRpcRequest(
            jsonrpc="2.0",
            id=8,
            method="tools/list",
            params={}
        )

        response1 = handler.handle_request(request1)

        assert response1["jsonrpc"] == "2.0"
        assert response1["id"] == 8
        assert "result" in response1
        assert "tools" in response1["result"]
        assert isinstance(response1["result"]["tools"], list)
        assert len(response1["result"]["tools"]) == 10  # First page should have 10 tools
        assert "nextCursor" in response1["result"]
        assert response1["result"]["nextCursor"] == "10"  # Next cursor should point to index 10

        # Second page request (with cursor)
        request2 = JsonRpcRequest(
            jsonrpc="2.0",
            id=9,
            method="tools/list",
            params={"cursor": "10"}
        )

        response2 = handler.handle_request(request2)

        assert response2["jsonrpc"] == "2.0"
        assert response2["id"] == 9
        assert "result" in response2
        assert "tools" in response2["result"]
        assert isinstance(response2["result"]["tools"], list)
        assert len(response2["result"]["tools"]) == 5  # Second page should have 5 tools
        # No more pages, nextCursor should not be present
        assert "nextCursor" not in response2["result"]

    def should_handle_tools_list_request_with_invalid_cursor(self, mock_tool):
        """Test handling of tools/list request with invalid cursor."""
        handler = JsonRpcHandler(tools=[mock_tool])

        # Request with invalid cursor format
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=10,
            method="tools/list",
            params={"cursor": "invalid"}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 10
        assert "error" in response
        assert response["error"]["code"] == JsonRpcErrorCode.INVALID_PARAMS
        assert "Invalid cursor format" in response["error"]["message"]

    def should_handle_tools_call_examine_request(self, mock_tool):
        """Test handling of tools/call request for the examine tool."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=9,
            method="tools/call",
            params={
                "name": "examine",
                "arguments": {
                    "directory": ".",
                    "format_type": "markdown"
                }
            }
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 9
        assert "result" in response
        assert "content" in response["result"]
        assert isinstance(response["result"]["content"], list)
        assert len(response["result"]["content"]) > 0
        assert "type" in response["result"]["content"][0]
        assert response["result"]["content"][0]["type"] == "text"
        assert "text" in response["result"]["content"][0]
        assert "isError" in response["result"]
        assert response["result"]["isError"] is False

        # Verify that the mock tool's run method was called with the correct arguments
        mock_tool.run.assert_called_once_with(
            directory=".",
            format_type="markdown"
        )


    def should_handle_exit_request(self, mock_tool):
        """Test handling of exit request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=11,
            method="exit",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 11
        assert "result" in response
        assert response["result"] is None
        assert handler.should_exit is True

    def should_handle_unknown_method(self, mock_tool):
        """Test handling of unknown method."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=12,
            method="unknown_method",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 12
        assert "error" in response
        assert response["error"]["code"] == JsonRpcErrorCode.METHOD_NOT_FOUND
        assert "Method not found" in response["error"]["message"]


    def should_handle_tools_call_unknown_tool(self, mock_tool):
        """Test handling of tools/call request for an unknown tool."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=13,
            method="tools/call",
            params={
                "name": "unknown_tool",
                "arguments": {}
            }
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 13
        assert "error" in response
        assert response["error"]["code"] == JsonRpcErrorCode.METHOD_NOT_FOUND
        assert "Tool not found" in response["error"]["message"]

    def should_handle_resources_list_request(self, mock_tool):
        """Test handling of resources/list request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=14,
            method="resources/list",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 14
        assert "result" in response
        assert "resources" in response["result"]
        assert isinstance(response["result"]["resources"], list)
        assert len(response["result"]["resources"]) == 0
        assert "nextCursor" not in response["result"]

    def should_handle_prompts_list_request(self, mock_tool):
        """Test handling of prompts/list request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=15,
            method="prompts/list",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 15
        assert "result" in response
        assert "prompts" in response["result"]
        assert isinstance(response["result"]["prompts"], list)
        assert len(response["result"]["prompts"]) == 0
        assert "nextCursor" not in response["result"]

    def should_handle_ping_request(self, mock_tool):
        """Test handling of ping request."""
        handler = JsonRpcHandler(tools=[mock_tool])
        request = JsonRpcRequest(
            jsonrpc="2.0",
            id=16,
            method="ping",
            params={}
        )

        response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 16
        assert "result" in response
        assert response["result"] == {}
