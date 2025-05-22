# HTTP Server Tutorial

This tutorial will guide you through creating an MCP server that exposes tools over HTTP using the Mojentic MCP library.

## Prerequisites

- Python 3.11 or higher
- Mojentic MCP library installed (`pip install mojentic-mcp`)
- Basic understanding of Python and HTTP

## Creating a Basic HTTP MCP Server

Let's create a simple HTTP MCP server that exposes date-related tools:

```python
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import the tool classes
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

# Import the server and handler classes
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with the tools
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])

# Create an HTTP MCP server with the handler
server = HttpMcpServer(rpc_handler)

# Log that the server is starting
sys.stderr.write("Starting HTTP MCP server...\n")
sys.stderr.write("Server ready to receive commands\n")

# Run the server
server.run()
```

Save this code to a file (e.g., `http_server.py`) and run it with Python:

```bash
python http_server.py
```

The server will start and listen for HTTP requests on port 8000 by default.

## Understanding the Code

Let's break down the key components of the HTTP MCP server:

1. **Tool Classes**: We import two tool classes from the `mojentic.llm.tools` package:
   - `CurrentDateTimeTool`: Returns the current date and time
   - `ResolveDateTool`: Resolves a date string (e.g., "next Monday") to a specific date

2. **JsonRpcHandler**: This class handles JSON-RPC 2.0 requests and responses. We initialize it with a list of tools that will be exposed to clients.

3. **HttpMcpServer**: This class creates an HTTP server that exposes the MCP protocol. It uses FastAPI under the hood.

4. **Running the Server**: The `run()` method starts the server and keeps it running until interrupted.

## Customizing the Server

### Changing the Port

By default, the HTTP server runs on port 8000. You can change this by setting the `PORT` environment variable:

```bash
PORT=8001 python http_server.py
```

### Adding More Tools

You can add more tools to the server by including them in the list passed to the `JsonRpcHandler`:

```python
from mojentic.llm.tools.some_other_tool import SomeOtherTool

rpc_handler = JsonRpcHandler(tools=[
    ResolveDateTool(), 
    CurrentDateTimeTool(),
    SomeOtherTool()
])
```

## Interacting with the Server

Once the server is running, clients can interact with it using the MCP protocol. Here's a simple example using the Mojentic MCP client:

```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

# Create an HTTP transport pointing to the server
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")

# Initialize the client with the transport
with McpClient(transports=[http_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    print(f"Discovered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
    
    # Call a tool
    current_time = client.tools.current_datetime()
    print(f"Current datetime: {current_time}")
    
    resolved_date = client.tools.resolve_date(date_string="next Friday")
    print(f"Resolved date: {resolved_date}")
```

For more details on using the client, see the [Client Usage Tutorial](client-usage.md).

## Next Steps

- Learn how to create a [STDIO MCP Server](stdio-server.md)
- Explore [Creating Custom Tools](custom-tools.md) to expose your own functionality
- Check out the [API Reference](../api/index.md) for detailed documentation