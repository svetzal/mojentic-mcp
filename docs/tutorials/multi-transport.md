# Multi-Transport Client Tutorial

This tutorial will guide you through using the Mojentic MCP client with multiple transport methods to interact with different MCP servers simultaneously.

## Prerequisites

- Python 3.11 or higher
- Mojentic MCP library installed (`pip install mojentic-mcp`)
- Basic understanding of the [Client Usage Tutorial](client-usage.md)
- Access to multiple MCP servers (either ones you've created or third-party servers)

## Why Use Multiple Transports?

There are several reasons you might want to use multiple transports:

1. **Access to Different Tools**: Different servers might provide different tools that you want to use in your application.
2. **Redundancy**: If one server is unavailable, you can still use tools from other servers.
3. **Specialized Servers**: You might have servers specialized for different tasks (e.g., one for date operations, another for weather forecasts).
4. **Mixed Transport Types**: You might need to communicate with both HTTP and STDIO servers.

## Creating a Multi-Transport Client

Here's how to create a client that communicates with multiple servers using different transport methods:

```python
import logging
import sys
import os
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create HTTP transport for a server with date tools
# You can use either a full URL:
http_transport1 = HttpTransport(url="http://localhost:8000/jsonrpc")
# Or host and port (with default path "/jsonrpc"):
# http_transport1 = HttpTransport(host="localhost", port=8000)

# Create HTTP transport for a server with custom tools
http_transport2 = HttpTransport(url="http://localhost:8001/jsonrpc")
# Or with host and port:
# http_transport2 = HttpTransport(host="localhost", port=8001)

# Create STDIO transport for a server with additional tools
script_dir = os.path.dirname(os.path.abspath(__file__))
stdio_server_path = os.path.join(script_dir, "stdio_server.py")
stdio_transport = StdioTransport(command=[sys.executable, stdio_server_path])

# Initialize the client with multiple transports
with McpClient(transports=[http_transport1, http_transport2, stdio_transport]) as client:
    # The client will automatically discover tools from all transports
    # and provide a unified interface to call them

    # List all available tools from all transports
    tools = client.list_tools()
    logger.info(f"Discovered {len(tools)} unique tools from all transports:")
    for tool in tools:
        logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")
```

## Understanding Tool Discovery

When you initialize a client with multiple transports, it discovers tools from all transports and creates a unified interface. Here's what you need to know:

1. **Unique Tool Names**: The client maintains a list of unique tool names across all transports.

2. **First-Wins Approach**: If multiple transports provide a tool with the same name, the client will use the one from the first transport in the list.

3. **Transport Order Matters**: The order in which you provide transports to the client determines which implementation of a tool will be used when there are duplicates.

## Calling Tools from Different Transports

Once you've initialized the client with multiple transports, you can call tools from any transport using the same unified interface:

```python
# Call a tool from the first HTTP transport
current_time = client.tools.current_datetime()
logger.info(f"Current datetime: {current_time}")

# Call a tool from the second HTTP transport
user_info = client.tools.colour_preferences()
logger.info(f"User info: {user_info}")

# Call a tool from the STDIO transport
# (assuming it provides a unique tool not available from the HTTP transports)
some_result = client.tools.some_unique_tool()
logger.info(f"Result from STDIO tool: {some_result}")
```

## Handling Tool Conflicts

When multiple transports provide tools with the same name, the client uses the "first-wins" approach. Here's how to handle this:

1. **Be Aware of Transport Order**: The order in which you provide transports to the client matters.

2. **Check Tool Availability**: You can check if a specific tool is available using `get_tool_schema`:

```python
schema = client.get_tool_schema("some_tool")
if schema:
    logger.info(f"Tool 'some_tool' is available")
else:
    logger.info(f"Tool 'some_tool' is not available")
```

3. **Specify Transport Explicitly**: If you need to call a specific implementation of a tool, you can specify the transport explicitly:

```python
# Call a tool from a specific transport
result = client.call_tool("some_tool", transport=http_transport2, param="value")
```

## Example: Working with Multiple Servers

Here's a complete example of working with multiple servers:

```python
import logging
import sys
import os
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create transports for different servers
# You can use either a full URL:
http_transport1 = HttpTransport(url="http://localhost:8000/jsonrpc")  # Date tools
# Or host and port:
# http_transport1 = HttpTransport(host="localhost", port=8000)  # Date tools

# Second transport for a different server
http_transport2 = HttpTransport(url="http://localhost:8001/jsonrpc")  # User info tool
# Or with host and port:
# http_transport2 = HttpTransport(host="localhost", port=8001)  # User info tool
script_dir = os.path.dirname(os.path.abspath(__file__))
stdio_server_path = os.path.join(script_dir, "stdio_server.py")
stdio_transport = StdioTransport(command=[sys.executable, stdio_server_path])  # Also date tools

# Initialize the client with multiple transports
with McpClient(transports=[http_transport1, http_transport2, stdio_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    logger.info(f"Discovered {len(tools)} unique tools from all transports:")
    for tool in tools:
        logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")

    try:
        # Call date tools (from http_transport1, since it's first in the list)
        current_time = client.tools.current_datetime()
        logger.info(f"Current datetime: {current_time}")

        resolved_date = client.tools.resolve_date(date_string="next Friday")
        logger.info(f"Resolved date: {resolved_date}")

        # Call user info tool (from http_transport2)
        user_info = client.tools.colour_preferences()
        logger.info(f"User info: {user_info}")

    except Exception as e:
        logger.error(f"Error calling tool: {e}")

    # Demonstrate the "first-wins" approach
    logger.info("\nDemonstrating 'first-wins' for tool discovery:")
    for tool_name in ["current_datetime", "resolve_date", "colour_preferences"]:
        schema = client.get_tool_schema(tool_name)
        if schema:
            logger.info(f"Tool '{tool_name}' is available from the first transport that provides it")
        else:
            logger.info(f"Tool '{tool_name}' is not available from any transport")
```

## Best Practices

1. **Organize Transports Logically**: Group transports by functionality or priority.

2. **Be Mindful of Tool Conflicts**: Be aware of which tools are provided by which transports and how conflicts are resolved.

3. **Handle Errors**: Always handle errors when calling tools, as they might fail for various reasons.

4. **Use Context Managers**: Always use the client with a context manager (`with` statement) to ensure proper cleanup.

5. **Consider Transport Reliability**: Put more reliable transports first in the list to ensure they're used preferentially for duplicate tools.

## Next Steps

- Explore [Creating Custom Tools](custom-tools.md) to expose your own functionality
- Learn how to create an [HTTP MCP Server](http-server.md) or [STDIO MCP Server](stdio-server.md)
- Check out the [API Reference](../api/index.md) for detailed documentation on the client and transport classes
