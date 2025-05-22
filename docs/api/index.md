# API Reference

This section provides detailed documentation for the Mojentic MCP library's API.

## Core Components

The Mojentic MCP library consists of several core components:

### Client

The client components provide a way to interact with MCP servers:

- [McpClient](client.md): The main client class for interacting with MCP servers
- [Transports](transports.md): Classes for communicating with servers using different transport methods

### Server

The server components provide a way to create MCP servers:

- [HttpMcpServer](http-server.md): Server implementation for HTTP transport
- [StdioMcpServer](stdio-server.md): Server implementation for STDIO transport
- [JsonRpcHandler](rpc.md): Handler for JSON-RPC 2.0 requests and responses

### Tools

The tools components provide a way to create custom tools:

- [LLMTool](llm-tool.md): Base class for creating custom tools

## Using the API

The API is designed to be simple and intuitive to use. Here are some common patterns:

### Creating a Server

```python
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with tools
rpc_handler = JsonRpcHandler(tools=[CurrentDateTimeTool()])

# Create an HTTP MCP server with the handler
server = HttpMcpServer(rpc_handler)

# Run the server
server.run()
```

### Using a Client

```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

# Create an HTTP transport
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")

# Initialize the client with the transport
with McpClient(transports=[http_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    
    # Call a tool
    result = client.tools.some_tool(param="value")
```

### Creating a Custom Tool

```python
from mojentic.llm.tools.llm_tool import LLMTool

class MyCustomTool(LLMTool):
    def run(self, param1, param2="default"):
        # Implement your tool's functionality here
        return {"result": f"{param1} - {param2}"}
    
    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "my_custom_tool",
                "description": "Description of what my tool does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of param1"
                        },
                        "param2": {
                            "type": "string",
                            "description": "Description of param2"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
```

## Next Steps

- Check out the [Tutorials](../tutorials/index.md) for step-by-step guides
- Explore the [Examples](https://github.com/svetzal/mojentic-mcp/tree/main/src/_examples) for more usage examples