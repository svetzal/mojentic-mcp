# Client Usage Tutorial

This tutorial will guide you through using the Mojentic MCP client to interact with MCP servers.

## Prerequisites

- Python 3.11 or higher
- Mojentic MCP library installed (`pip install mojentic-mcp`)
- Access to an MCP server (either one you've created or a third-party server)

## Basic Client Usage

The Mojentic MCP client provides a simple interface for interacting with MCP servers. Here's a basic example of using the client with an HTTP transport:

```python
import logging
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an HTTP transport pointing to a local MCP server
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")

# Initialize the client with the transport
with McpClient(transports=[http_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    logger.info(f"Discovered {len(tools)} tools:")
    for tool in tools:
        logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")
    
    # Call a tool using the dynamic accessor
    current_time = client.tools.current_datetime()
    logger.info(f"Current datetime: {current_time}")
```

## Understanding the Client

Let's break down the key components of the client:

1. **McpClient**: The main client class that handles communication with MCP servers.

2. **Transports**: Classes that handle the actual communication with servers. Mojentic MCP provides two transport types:
   - `HttpTransport`: For communicating with HTTP MCP servers
   - `StdioTransport`: For communicating with STDIO MCP servers

3. **Tool Discovery**: The client automatically discovers available tools when initialized.

4. **Tool Invocation**: Tools can be called using either the dynamic accessor (`client.tools.<tool_name>()`) or the `call_tool` method.

## Calling Tools

There are two ways to call tools using the client:

### 1. Using the Dynamic Accessor

The dynamic accessor provides a more Pythonic way to call tools:

```python
# Call a tool with no parameters
current_time = client.tools.current_datetime()

# Call a tool with parameters
resolved_date = client.tools.resolve_date(date_string="next Friday")
```

### 2. Using the call_tool Method

The `call_tool` method provides a more explicit way to call tools:

```python
# Call a tool with no parameters
current_time = client.call_tool("current_datetime")

# Call a tool with parameters
resolved_date = client.call_tool("resolve_date", date_string="next Friday")
```

## Error Handling

It's important to handle errors when calling tools. Here's an example of error handling:

```python
try:
    # This might cause an error if the tool doesn't exist or if the parameters are invalid
    result = client.tools.some_tool(param="value")
    logger.info(f"Result: {result}")
except Exception as e:
    logger.error(f"Error calling tool: {e}")
```

## Working with STDIO Servers

When working with STDIO servers, you typically start the server as a subprocess:

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
    # The client will automatically start the server subprocess
    # and communicate with it over STDIO
    
    # List all available tools
    tools = client.list_tools()
    print(f"Discovered {len(tools)} tools from STDIO server:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
    
    # Call tools using the dynamic accessor
    current_time = client.tools.current_datetime()
    print(f"Current datetime: {current_time}")
```

## Getting Tool Schema

You can get the schema for a specific tool using the `get_tool_schema` method:

```python
# Get schema for a specific tool
schema = client.get_tool_schema("current_datetime")
if schema:
    logger.info(f"Tool 'current_datetime' schema: {schema}")
else:
    logger.warning("Tool 'current_datetime' not found")
```

## Advanced Usage: Tool Filtering

If you're working with multiple servers that might have tools with the same name, you can filter tools by transport:

```python
# Get tools from a specific transport
http_tools = client.list_tools(transport=http_transport)
logger.info(f"Discovered {len(http_tools)} tools from HTTP server")

# Call a tool on a specific transport
result = client.call_tool("some_tool", transport=http_transport, param="value")
```

## Best Practices

1. **Use Context Managers**: Always use the client with a context manager (`with` statement) to ensure proper cleanup.

2. **Handle Errors**: Always handle errors when calling tools, as they might fail for various reasons.

3. **Check Tool Availability**: Before calling a tool, check if it's available using `list_tools` or `get_tool_schema`.

4. **Use Logging**: Set up logging to help debug issues with tool calls.

5. **Prefer Dynamic Accessor**: Use the dynamic accessor (`client.tools.<tool_name>()`) for a more Pythonic interface.

## Next Steps

- Learn about [Multi-Transport Clients](multi-transport.md) for working with multiple servers
- Explore [Creating Custom Tools](custom-tools.md) to expose your own functionality
- Check out the [API Reference](../api/index.md) for detailed documentation on the client and transport classes