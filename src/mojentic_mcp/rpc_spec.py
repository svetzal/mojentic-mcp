"""Tests for the JSON-RPC handler."""

import pytest
from unittest.mock import Mock

from mojentic_mcp.rpc import JsonRpcHandler, JsonRpcRequest
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
            "description": "Examine a Python codebase and generate documentation"
        }
    }

    return mock_tool


class DescribeJsonRpcHandler:
    """Tests for the JsonRpcHandler class."""

    def it_should_be_instantiated(self, mock_tool):
        """Test that JsonRpcHandler can be instantiated."""
        handler = JsonRpcHandler(tools=[mock_tool])

        assert isinstance(handler, JsonRpcHandler)
        assert handler.should_exit is False
        assert len(handler.methods) > 0
        assert handler.tools == [mock_tool]

    def it_should_handle_initialize_request(self, mock_tool):
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

    def it_should_handle_tools_list_request(self, mock_tool):
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

        # Verify the examine tool is in the list
        examine_tool = response["result"]["tools"][0]
        assert examine_tool["name"] == "examine"
        assert "description" in examine_tool

    def it_should_handle_tools_call_examine_request(self, mock_tool):
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
        assert "status" in response["result"]
        assert response["result"]["status"] == "success"
        assert "documentation" in response["result"]
        assert "modules_found" in response["result"]

        # Verify that the mock tool's run method was called with the correct arguments
        mock_tool.run.assert_called_once_with(
            directory=".",
            format_type="markdown"
        )


    def it_should_handle_exit_request(self, mock_tool):
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

    def it_should_handle_unknown_method(self, mock_tool):
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
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]


    def it_should_handle_tools_call_unknown_tool(self, mock_tool):
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
        assert response["error"]["code"] == -32601
        assert "Tool not found" in response["error"]["message"]

    def it_should_handle_resources_list_request(self, mock_tool):
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
        assert response["result"]["nextCursor"] is None

    def it_should_handle_prompts_list_request(self, mock_tool):
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
        assert response["result"]["nextCursor"] is None
