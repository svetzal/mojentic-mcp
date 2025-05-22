# STDIO Server Tutorial

This tutorial will guide you through creating an MCP server that exposes tools over standard input/output (STDIO) using the Mojentic MCP library.

## Prerequisites

- Python 3.11 or higher
- Mojentic MCP library installed (`pip install mojentic-mcp`)
- Basic understanding of Python and STDIO communication

## Creating a Basic STDIO MCP Server

Let's create a simple STDIO MCP server that exposes date-related tools:

```python
import logging
import sys

# Set up logging (CRITICAL level to avoid cluttering STDIO)
logging.basicConfig(level=logging.CRITICAL)

# Import the tool classes
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

# Import the server and handler classes
from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with the tools
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])

# Create a STDIO MCP server with the handler
server = StdioMcpServer(rpc_handler)

# Log that the server is starting (to stderr to avoid interfering with STDIO communication)
sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")

# Run the server
server.run()
```

Save this code to a file (e.g., `stdio_server.py`) and run it with Python:

```bash
python stdio_server.py
```

The server will start and listen for JSON-RPC requests on standard input, responding on standard output.

## Understanding the Code

Let's break down the key components of the STDIO MCP server:

1. **Logging Level**: We set the logging level to CRITICAL to avoid cluttering the standard output, which is used for communication.

2. **Tool Classes**: We import two tool classes from the `mojentic.llm.tools` package:
   - `CurrentDateTimeTool`: Returns the current date and time
   - `ResolveDateTool`: Resolves a date string (e.g., "next Monday") to a specific date

3. **JsonRpcHandler**: This class handles JSON-RPC 2.0 requests and responses. We initialize it with a list of tools that will be exposed to clients.

4. **StdioMcpServer**: This class creates a server that communicates over standard input/output.

5. **Error Messages**: We write error messages to `sys.stderr` to avoid interfering with the JSON-RPC communication on standard input/output.

6. **Running the Server**: The `run()` method starts the server and keeps it running until interrupted.

## Interacting with the Server

STDIO servers are typically used as subprocesses that are started by a client. Here's an example of how to interact with a STDIO MCP server using the Mojentic MCP client:

```python
import os
import sys
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import StdioTransport

# Get the path to the STDIO server script
script_dir = os.path.dirname(os.path.abspath(__file__))
stdio_server_path = os.path.join(script_dir, "stdio_server.py")

# Create a STDIO transport that runs the server script as a subprocess
stdio_transport = StdioTransport(command=[sys.executable, stdio_server_path])

# Initialize the client with the transport
with McpClient(transports=[stdio_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    print(f"Discovered {len(tools)} tools from STDIO server:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
    
    # Call tools using the dynamic accessor
    current_time = client.tools.current_datetime()
    print(f"Current datetime: {current_time}")
    
    resolved_date = client.tools.resolve_date(date_string="next Tuesday")
    print(f"Resolved date: {resolved_date}")
```

## Error Handling

When working with STDIO servers, it's important to handle errors properly. Here's an example of error handling:

```python
try:
    # This should cause an error in the tool
    invalid_date = client.tools.resolve_date(date_string="not a valid date")
    print(f"Invalid date result: {invalid_date}")
except Exception as e:
    print(f"Expected error with invalid date: {e}")
```

## Use Cases for STDIO Servers

STDIO servers are particularly useful in the following scenarios:

1. **Integration with AI Assistants**: Many AI assistants support the MCP protocol over STDIO, allowing them to start your server as a subprocess.

2. **Command-Line Tools**: STDIO servers can be used to create command-line tools that expose functionality to other programs.

3. **Embedded Environments**: In environments where HTTP is not available or not desirable, STDIO provides a simple communication channel.

## Next Steps

- Learn how to create an [HTTP MCP Server](http-server.md)
- Explore [Creating Custom Tools](custom-tools.md) to expose your own functionality
- Check out the [Client Usage Tutorial](client-usage.md) for more details on using the client
- Learn about [Multi-Transport Clients](multi-transport.md) for working with multiple servers