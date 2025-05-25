import logging
import sys

logging.basicConfig(level=logging.CRITICAL)

from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])
server = StdioMcpServer(rpc_handler)
server.run()