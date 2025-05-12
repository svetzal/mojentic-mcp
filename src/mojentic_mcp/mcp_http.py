"""HTTP-based MCP server implementation for Codebase Examiner."""

import json

import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError

from mojentic_mcp.rpc import JsonRpcHandler, JsonRpcRequest


class HttpMcpServer:
    """An MCP server that communicates over HTTP using JSON-RPC."""

    def __init__(self, rpc_handler: JsonRpcHandler):
        """Initialize the HTTP MCP server.

        Args:
            rpc_handler (JsonRpcHandler): The JSON-RPC handler to use.
        """
        self.rpc_handler = rpc_handler
        self.app = FastAPI(title="Codebase Examiner MCP", description="MCP server for examining Python codebases")

        # Register the JSON-RPC endpoint
        self.app.post("/jsonrpc")(self.handle_jsonrpc)

    async def handle_jsonrpc(self, request: Request) -> Response:
        """Handle JSON-RPC 2.0 requests.

        Args:
            request (Request): The FastAPI request object

        Returns:
            Response: The JSON-RPC response
        """
        try:
            # Parse the request body
            body = await request.json()

            # Convert to JsonRpcRequest model
            rpc_request = JsonRpcRequest(**body)

            # Handle the JSON-RPC request
            response = self.rpc_handler.handle_request(rpc_request)

            # Return the response
            return Response(
                content=json.dumps(response),
                media_type="application/json"
            )
        except json.JSONDecodeError:
            # Invalid JSON
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            return Response(
                content=json.dumps(error_response),
                media_type="application/json",
                status_code=400
            )
        except ValidationError as e:
            # Invalid Request (validation error)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": str(e)
                }
            }
            return Response(
                content=json.dumps(error_response),
                media_type="application/json",
                status_code=400
            )
        except Exception as e:
            # Server error
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            return Response(
                content=json.dumps(error_response),
                media_type="application/json",
                status_code=500
            )

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the HTTP MCP server.

        Args:
            host (str): The host to bind to
            port (int): The port to listen on
        """
        uvicorn.run(self.app, host=host, port=port)


def start_server(port: int, rpc_handler: JsonRpcHandler):
    """Start the MCP server.

    Args:
        port (int): The port to run the server on
        rpc_handler (JsonRpcHandler): The JSON-RPC handler to use.
    """
    server = HttpMcpServer(rpc_handler)
    server.run(port=port)


if __name__ == "__main__":
    import sys
    # Note: ExaminerTool has been moved or renamed in the mojentic_mcp package
    # from codebase_examiner.core.examiner_tool import ExaminerTool

    if len(sys.argv) < 2:
        print("Usage: python -m mojentic_mcp.mcp_http <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    # rpc_handler = JsonRpcHandler(tools=[ExaminerTool()])
    rpc_handler = JsonRpcHandler(tools=[])
    start_server(port, rpc_handler)
