import logging
import sys

from mojentic.llm.tools.llm_tool import LLMTool

from mojentic_mcp.mcp_http import HttpMcpServer

logging.basicConfig(level=logging.INFO)

from mojentic_mcp.rpc import JsonRpcHandler


class AboutTheUser(LLMTool):
    def run(self):
        return {
            "name": "Stacey",
            "favourite_colour": "purple"
        }

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "colour_preferences",
                "description": "Return the user's favourite colour.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        }


sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")
rpc_handler = JsonRpcHandler(tools=[
    AboutTheUser(),
])
server = HttpMcpServer(rpc_handler)
server.run()
