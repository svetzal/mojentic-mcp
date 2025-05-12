"""Tests for the HTTP-based MCP server."""

from unittest.mock import Mock

from fastapi.testclient import TestClient

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler


class DescribeHttpMcpServer:
    """Tests for the HTTP-based MCP server."""

    def setup_method(self, method):
        """Set up test fixtures."""
        self.mock_rpc_handler = Mock(spec=JsonRpcHandler)
        self.server = HttpMcpServer(self.mock_rpc_handler)
        self.client = TestClient(self.server.app)

    def it_should_handle_jsonrpc_initialize_request(self):
        """Test handling of JSON-RPC initialize request."""
        # Prepare the initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {}
            }
        }

        # Mock the RPC handler response
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "serverInfo": {
                    "name": "Codebase Examiner",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "examineProvider": True
                },
                "protocolVersion": "2025-03-26"
            }
        }
        self.mock_rpc_handler.handle_request.return_value = mock_response

        # Send the request
        response = self.client.post(
            "/jsonrpc",
            json=initialize_request
        )

        # Verify the response
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 1
        assert "result" in response_json
        assert "serverInfo" in response_json["result"]
        assert "capabilities" in response_json["result"]
        assert response_json["result"]["protocolVersion"] == "2025-03-26"

    def it_should_handle_jsonrpc_tools_list_request(self):
        """Test handling of JSON-RPC tools/list request."""
        # Prepare the tools/list request
        tools_list_request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/list",
            "params": {}
        }

        # Mock the RPC handler response
        mock_response = {
            "jsonrpc": "2.0",
            "id": 8,
            "result": {
                "tools": [
                    {
                        "name": "examine",
                        "description": "Examine a Python codebase and generate documentation"
                    }
                ]
            }
        }
        self.mock_rpc_handler.handle_request.return_value = mock_response

        # Send the request
        response = self.client.post(
            "/jsonrpc",
            json=tools_list_request
        )

        # Verify the response
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 8
        assert "result" in response_json
        assert "tools" in response_json["result"]
        assert isinstance(response_json["result"]["tools"], list)
        assert len(response_json["result"]["tools"]) > 0

    def it_should_handle_jsonrpc_tools_call_examine_request(self):
        """Test handling of JSON-RPC tools/call request for the examine tool."""
        # Prepare the tools/call request
        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "examine",
                "arguments": {
                    "directory": ".",
                    "format": "markdown"
                }
            }
        }

        # Mock the RPC handler response
        mock_response = {
            "jsonrpc": "2.0",
            "id": 9,
            "result": {
                "status": "success",
                "documentation": "# Test Documentation",
                "modules_found": 5
            }
        }
        self.mock_rpc_handler.handle_request.return_value = mock_response

        # Send the request
        response = self.client.post(
            "/jsonrpc",
            json=tools_call_request
        )

        # Verify the response
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 9
        assert "result" in response_json
        assert "error" not in response_json
        assert "status" in response_json["result"]
        assert response_json["result"]["status"] == "success"
        assert "documentation" in response_json["result"]
        assert "modules_found" in response_json["result"]


    def it_should_handle_jsonrpc_invalid_json(self):
        """Test handling of invalid JSON in JSON-RPC request."""
        # Send an invalid JSON request
        response = self.client.post(
            "/jsonrpc",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Verify the response
        assert response.status_code == 400
        response_json = response.json()
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] is None
        assert "error" in response_json
        assert response_json["error"]["code"] == -32700
        assert response_json["error"]["message"] == "Parse error"
