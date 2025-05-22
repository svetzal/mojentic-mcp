# McpClient API

The `McpClient` class is the main client interface for interacting with MCP servers. It provides methods for discovering and calling tools exposed by MCP servers.

## Class: McpClient

```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

client = McpClient(transports=[HttpTransport(url="http://localhost:8000/jsonrpc")])
```

### Constructor

```python
def __init__(self, transports: List[McpTransport])
```

Creates a new McpClient instance.

**Parameters:**
- `transports`: A list of transport objects that implement the `McpTransport` interface. These transports are used to communicate with MCP servers.

**Example:**
```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

# Create transports
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")
stdio_transport = StdioTransport(command=["python", "stdio_server.py"])

# Create client with multiple transports
client = McpClient(transports=[http_transport, stdio_transport])
```

### Methods

#### list_tools

```python
def list_tools(self, transport: Optional[McpTransport] = None) -> List[Dict[str, Any]]
```

Lists all available tools from all transports or from a specific transport.

**Parameters:**
- `transport` (optional): A specific transport to list tools from. If not provided, tools from all transports are listed.

**Returns:**
- A list of tool descriptors, each containing information about a tool.

**Example:**
```python
# List all tools from all transports
tools = client.list_tools()
for tool in tools:
    print(f"Tool: {tool['name']} - {tool.get('description', 'No description')}")

# List tools from a specific transport
http_tools = client.list_tools(transport=http_transport)
```

#### get_tool_schema

```python
def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]
```

Gets the schema for a specific tool.

**Parameters:**
- `tool_name`: The name of the tool to get the schema for.

**Returns:**
- The tool schema if found, or None if the tool is not available.

**Example:**
```python
schema = client.get_tool_schema("current_datetime")
if schema:
    print(f"Tool schema: {schema}")
else:
    print("Tool not found")
```

#### call_tool

```python
def call_tool(self, tool_name: str, transport: Optional[McpTransport] = None, **kwargs: Any) -> Any
```

Calls a tool with the specified parameters.

**Parameters:**
- `tool_name`: The name of the tool to call.
- `transport` (optional): A specific transport to use for the call. If not provided, the first transport that provides the tool is used.
- `**kwargs`: Parameters to pass to the tool.

**Returns:**
- The result of the tool call.

**Raises:**
- `McpClientError`: If there's an error with the client.
- `McpToolExecutionError`: If there's an error executing the tool.

**Example:**
```python
try:
    # Call a tool with no parameters
    current_time = client.call_tool("current_datetime")
    print(f"Current time: {current_time}")
    
    # Call a tool with parameters
    resolved_date = client.call_tool("resolve_date", date_string="next Friday")
    print(f"Resolved date: {resolved_date}")
    
    # Call a tool on a specific transport
    result = client.call_tool("some_tool", transport=http_transport, param="value")
except McpClientError as e:
    print(f"Client error: {e}")
except McpToolExecutionError as e:
    print(f"Tool execution error: {e}")
```

#### shutdown

```python
def shutdown(self)
```

Shuts down the client and all its transports.

**Example:**
```python
# Shutdown the client when done
client.shutdown()
```

### Context Manager

The `McpClient` class can be used as a context manager, which automatically handles shutdown:

```python
with McpClient(transports=[http_transport]) as client:
    # Use the client here
    tools = client.list_tools()
    result = client.call_tool("some_tool", param="value")
# Client is automatically shut down when exiting the context
```

## Dynamic Tool Access

The `McpClient` provides a dynamic accessor for tools via the `tools` attribute:

```python
# Using the dynamic accessor
current_time = client.tools.current_datetime()
resolved_date = client.tools.resolve_date(date_string="next Friday")
```

This is equivalent to using the `call_tool` method but provides a more Pythonic interface.

## Exception Classes

### McpClientError

Base exception class for client errors.

```python
class McpClientError(Exception)
```

### McpToolExecutionError

Exception raised when there's an error executing a tool.

```python
class McpToolExecutionError(McpClientError)
```

**Attributes:**
- `message`: The error message.
- `tool_result_payload`: The payload returned by the tool that caused the error.

## Best Practices

1. **Use Context Managers**: Always use the client with a context manager (`with` statement) to ensure proper cleanup.

2. **Handle Errors**: Always handle errors when calling tools, as they might fail for various reasons.

3. **Check Tool Availability**: Before calling a tool, check if it's available using `list_tools` or `get_tool_schema`.

4. **Prefer Dynamic Accessor**: Use the dynamic accessor (`client.tools.<tool_name>()`) for a more Pythonic interface.

## See Also

- [Transports API](transports.md): Documentation for the transport classes used by the client.
- [Client Usage Tutorial](../tutorials/client-usage.md): Step-by-step guide to using the client.
- [Multi-Transport Client Tutorial](../tutorials/multi-transport.md): Guide to using the client with multiple transports.