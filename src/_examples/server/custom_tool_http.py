import logging

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


rpc_handler = JsonRpcHandler(tools=[
    AboutTheUser(),
])

# Create an HTTP MCP server with the default path ("/jsonrpc")
server = HttpMcpServer(rpc_handler)

server.run()
