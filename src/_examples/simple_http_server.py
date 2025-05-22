import logging
import sys

# Set up logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Import the server and handler classes
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

def main():
    # Create a JSON-RPC handler with the tools we want to expose
    rpc_handler = JsonRpcHandler(tools=[
        CurrentDateTimeTool(),  # Tool to get current date and time
        ResolveDateTool()       # Tool to resolve date strings
    ])

    # Create and run the HTTP server
    # You can use the default path ("/jsonrpc"):
    # server = HttpMcpServer(rpc_handler)
    # Or specify a custom path:
    server = HttpMcpServer(rpc_handler, path="/jsonrpc")  # Default path shown explicitly

    logger.info("Starting HTTP MCP server on port 8080...")
    server.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
