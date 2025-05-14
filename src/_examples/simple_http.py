import logging
import sys

logging.basicConfig(level=logging.INFO)

from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])
server = HttpMcpServer(rpc_handler)
server.run()