# Transports API

The Mojentic MCP library provides transport classes for communicating with MCP servers using different protocols. These transport classes implement the `McpTransport` interface.

::: mojentic_mcp.transports.McpTransport
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.transports.HttpTransport
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.transports.StdioTransport
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.transports.McpTransportError
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

## Usage Examples

### HTTP Transport

```python
from mojentic_mcp.transports import HttpTransport
from mojentic_mcp.rpc import JsonRpcRequest

# Create an HTTP transport with a full URL
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")

# Create an HTTP transport with host and port (using default path "/jsonrpc")
http_transport_host_port = HttpTransport(host="localhost", port=8000)

# Create an HTTP transport with host, port, and custom path
http_transport_custom_path = HttpTransport(host="localhost", port=8000, path="/custom-path")

# Create an HTTP transport with a custom timeout
http_transport_with_timeout = HttpTransport(url="http://localhost:8000/jsonrpc", timeout=60.0)

# Use the transport as a context manager
with HttpTransport(url="http://localhost:8000/jsonrpc") as transport:
    # Create a JSON-RPC request
    rpc_request = JsonRpcRequest(method="tools/list", params={})

    # Send the request and get the response
    response = transport.send_request(rpc_request)
```

### STDIO Transport

```python
import sys
from mojentic_mcp.transports import StdioTransport
from mojentic_mcp.rpc import JsonRpcRequest

# Create a STDIO transport that runs a Python script
stdio_transport = StdioTransport(command=[sys.executable, "stdio_server.py"])

# Create a STDIO transport that runs a compiled executable
stdio_transport_executable = StdioTransport(command=["./mcp_server"])

# Use the transport as a context manager
with StdioTransport(command=[sys.executable, "stdio_server.py"]) as transport:
    # Create a JSON-RPC request
    rpc_request = JsonRpcRequest(method="tools/list", params={})

    # Send the request and get the response
    response = transport.send_request(rpc_request)
```

## Best Practices

1. **Use Context Managers**: Always use transports with a context manager (`with` statement) to ensure proper initialization and cleanup.

2. **Handle Errors**: Always handle `McpTransportError` exceptions when sending requests.

3. **Choose the Right Transport**: Use `HttpTransport` for communicating with HTTP servers and `StdioTransport` for communicating with STDIO servers.

4. **Set Appropriate Timeouts**: For `HttpTransport`, set an appropriate timeout based on the expected response time of the server.

## See Also

- [McpClient API](client.md): Documentation for the client class that uses transports.
- [Client Usage Tutorial](../tutorials/client-usage.md): Step-by-step guide to using the client with different transports.
- [Multi-Transport Client Tutorial](../tutorials/multi-transport.md): Guide to using multiple transports with a single client.
