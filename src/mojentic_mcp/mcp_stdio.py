"""STDIO-based MCP server implementation for Codebase Examiner."""

import json
import sys
from typing import Dict, Any, Optional

from pydantic import ValidationError

from mojentic_mcp.rpc import JsonRpcHandler, JsonRpcRequest


class StdioMcpServer:
    """An MCP server that communicates over standard input/output using JSON-RPC."""

    def __init__(self, rpc_handler: JsonRpcHandler):
        """Initialize the STDIO MCP server.

        Args:
            rpc_handler (JsonRpcHandler): The JSON-RPC handler to use.
        """
        self.rpc_handler = rpc_handler
        self.should_exit = False

    def _read_request(self) -> Dict[str, Any]:
        """Read a JSON request from standard input.

        Returns:
            Dict[str, Any]: The parsed JSON request
        """
        try:
            line = sys.stdin.readline()
            if not line:
                self.should_exit = True
                return {}

            return json.loads(line)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON request"}

    def _write_response(self, response: Dict[str, Any]) -> None:
        """Write a JSON response to standard output.

        Args:
            response (Dict[str, Any]): The response to write
        """
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def _write_info(self, message: str, status: Optional[str] = "info") -> None:
        """Write an informational message to standard error.

        Args:
            message (str): The message to write
            status (Optional[str]): The status to include in the message
        """
        info = {"status": status, "message": message}
        sys.stderr.write(json.dumps(info) + "\n")
        sys.stderr.flush()

    def _handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a ping request.

        Args:
            request (Dict[str, Any]): The ping request

        Returns:
            Dict[str, Any]: A pong response
        """
        return {
            "status": "success",
            "message": "pong"
        }

    def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single request.

        Args:
            request (Dict[str, Any]): The request to handle

        Returns:
            Dict[str, Any]: The response
        """
        if "error" in request:
            return {"status": "error", "message": request["error"]}

        try:
            # Check if this is a JSON-RPC 2.0 request
            if "jsonrpc" in request and request.get("jsonrpc") == "2.0" and "method" in request:
                # Convert to JsonRpcRequest model
                rpc_request = JsonRpcRequest(**request)
                response = self.rpc_handler.handle_request(rpc_request)
                self.should_exit = self.rpc_handler.should_exit
                return response

            # Handle legacy command-based requests
            command = request.get("command")

            if command == "examine":
                # Convert to JSON-RPC format and use the RPC handler
                jsonrpc_request = JsonRpcRequest(
                    jsonrpc="2.0",
                    id="legacy",
                    method="tools/call",
                    params={
                        "name": "examine",
                        "arguments": request
                    }
                )
                response = self.rpc_handler.handle_request(jsonrpc_request)
                return response.get("result", {"status": "error", "message": "Failed to process examine request"})
            elif command == "ping":
                return self._handle_ping(request)
            elif command == "exit":
                self.should_exit = True
                return {"status": "success", "message": "Server exiting"}
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {command}"
                }
        except ValidationError as e:
            # Invalid Request (validation error)
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": str(e)
                }
            }

    def run(self) -> None:
        """Run the STDIO MCP server loop."""
        # Output an initialization message to stderr
        self._write_info("STDIO MCP server ready", "ready")

        while not self.should_exit:
            try:
                request = self._read_request()
                if self.should_exit:
                    break

                response = self._handle_request(request)
                self._write_response(response)
            except Exception as e:
                self._write_response({
                    "status": "error",
                    "message": f"Server error: {str(e)}"
                })


def start_server(rpc_handler: JsonRpcHandler) -> None:
    """Start the STDIO MCP server.

    Args:
        rpc_handler (JsonRpcHandler): The JSON-RPC handler to use.
    """
    server = StdioMcpServer(rpc_handler)
    server.run()


if __name__ == "__main__":
    # Note: ExaminerTool has been moved or renamed in the mojentic_mcp package
    # from codebase_examiner.core.examiner_tool import ExaminerTool
    # rpc_handler = JsonRpcHandler(tools=[ExaminerTool()])
    rpc_handler = JsonRpcHandler(tools=[])
    start_server(rpc_handler)
