# McpClient API

The `McpClient` class is the main client interface for interacting with MCP servers. It provides methods for discovering and calling tools exposed by MCP servers.

## Usage Examples

```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

# Create transports
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")
stdio_transport = StdioTransport(command=["python", "stdio_server.py"])

# Create client with multiple transports
with McpClient(transports=[http_transport, stdio_transport]) as client:
    # List all tools from all transports
    tools = client.list_tools()
    for tool in tools:
        print(f"Tool: {tool['name']} - {tool.get('description', 'No description')}")
    
    # Call a tool with parameters
    result = client.call_tool("some_tool", param="value")
    
    # Using the dynamic accessor
    current_time = client.tools.current_datetime()
    resolved_date = client.tools.resolve_date(date_string="next Friday")
```

## API Reference

::: mojentic_mcp.client.McpClient
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.client.ToolAccessor
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

## Exception Classes

::: mojentic_mcp.client.McpClientError
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.client.McpToolExecutionError
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

## Best Practices

1. **Use Context Managers**: Always use the client with a context manager (`with` statement) to ensure proper cleanup.

2. **Handle Errors**: Always handle errors when calling tools, as they might fail for various reasons.

3. **Check Tool Availability**: Before calling a tool, check if it's available using `list_tools` or `get_tool_schema`.

4. **Prefer Dynamic Accessor**: Use the dynamic accessor (`client.tools.<tool_name>()`) for a more Pythonic interface.

## See Also

- [Transports API](transports.md): Documentation for the transport classes used by the client.
- [Client Usage Tutorial](../tutorials/client-usage.md): Step-by-step guide to using the client.
- [Multi-Transport Client Tutorial](../tutorials/multi-transport.md): Guide to using the client with multiple transports.