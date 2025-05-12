import json
from io import StringIO
from unittest.mock import patch, Mock

from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler


class DescribeStdioMcpServer:
    """Tests for the StdioMcpServer class."""

    def setup_method(self, method):
        """Set up test fixtures."""
        self.mock_rpc_handler = Mock(spec=JsonRpcHandler)
        self.mock_rpc_handler.should_exit = False
        self.server = StdioMcpServer(self.mock_rpc_handler)
        self.mock_stdout = StringIO()
        self.mock_stdin = StringIO()

    def it_should_handle_initialize_request(self):
        """Test handling of initialize request with protocol version 2025-03-26."""
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

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(initialize_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 1
        assert "result" in response_json
        assert "serverInfo" in response_json["result"]
        assert "capabilities" in response_json["result"]
        assert response_json["result"]["protocolVersion"] == "2025-03-26"
        assert response_json["result"]["serverInfo"]["version"] == "0.1.0"

    def it_should_handle_tools_list_request(self):
        """Test handling of tools/list request."""
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

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(tools_list_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 8
        assert "result" in response_json
        assert "tools" in response_json["result"]
        assert isinstance(response_json["result"]["tools"], list)
        assert len(response_json["result"]["tools"]) > 0

        # Verify the examine tool is in the list
        examine_tool = next((tool for tool in response_json["result"]["tools"] if tool["name"] == "examine"), None)
        assert examine_tool is not None
        assert "description" in examine_tool

    def it_should_handle_tools_call_examine_request(self):
        """Test handling of tools/call request for the examine tool."""
        # Prepare the tools/call request
        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "examine",
                "arguments": {}
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

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(tools_call_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        assert response_json["jsonrpc"] == "2.0"
        assert response_json["id"] == 9
        assert "result" in response_json
        assert "error" not in response_json

        # Verify the result contains expected fields from examine response
        assert "status" in response_json["result"]
        assert response_json["result"]["status"] == "success"
        assert "documentation" in response_json["result"]
        assert "modules_found" in response_json["result"]

    def it_should_handle_legacy_examine_request(self):
        """Test handling of legacy examine request."""
        # Prepare the legacy examine request
        legacy_request = {
            "command": "examine",
            "directory": ".",
            "format": "markdown"
        }

        # Mock the RPC handler response
        mock_result = {
            "status": "success",
            "documentation": "# Test Documentation",
            "modules_found": 5
        }
        mock_response = {
            "jsonrpc": "2.0",
            "id": "legacy",
            "result": mock_result
        }
        self.mock_rpc_handler.handle_request.return_value = mock_response

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(legacy_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        assert response_json["status"] == "success"
        assert response_json["documentation"] == "# Test Documentation"
        assert response_json["modules_found"] == 5
