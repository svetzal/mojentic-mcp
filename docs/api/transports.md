# Transports API

The Mojentic MCP library provides transport classes for communicating with MCP servers using different protocols. These transport classes implement the `McpTransport` interface.

## Abstract Base Class: McpTransport

```python
from mojentic_mcp.transports import McpTransport
```

`McpTransport` is an abstract base class that defines the interface for all transport classes.

### Methods

#### send_request

```python
@abc.abstractmethod
def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]
```

Sends a JSON-RPC request to the server and returns the response.

**Parameters:**
- `rpc_request`: A JsonRpcRequest object representing the request to send.

**Returns:**
- A dictionary containing the JSON-RPC response.

**Raises:**
- `McpTransportError`: If there's an error sending the request or receiving the response.

#### initialize

```python
def initialize(self) -> None
```

Initializes the transport. This method is called when the transport is first used.

#### shutdown

```python
def shutdown(self) -> None
```

Shuts down the transport and releases any resources. This method is called when the transport is no longer needed.

### Context Manager

The `McpTransport` class can be used as a context manager, which automatically handles initialization and shutdown:

```python
with HttpTransport(url="http://localhost:8000/jsonrpc") as transport:
    # Use the transport here
    response = transport.send_request(rpc_request)
# Transport is automatically shut down when exiting the context
```

## Class: HttpTransport

```python
from mojentic_mcp.transports import HttpTransport
```

`HttpTransport` is an implementation of `McpTransport` that communicates with MCP servers over HTTP.

### Constructor

```python
def __init__(self, url: str = None, host: str = None, port: int = None, path: str = "/jsonrpc", timeout: float = 30.0)
```

Creates a new HttpTransport instance.

**Parameters:**
- `url` (optional): The full URL to the JSON-RPC endpoint. If provided, this takes precedence over host, port, and path.
- `host` (optional): The host to connect to. Required if url is not provided.
- `port` (optional): The port to connect to. Required if url is not provided.
- `path` (optional): The path to the JSON-RPC endpoint. Defaults to "/jsonrpc".
- `timeout` (optional): The timeout for HTTP requests in seconds. Defaults to 30.0.

**Example:**
```python
from mojentic_mcp.transports import HttpTransport

# Create an HTTP transport with a full URL
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")

# Create an HTTP transport with host and port (using default path "/jsonrpc")
http_transport_host_port = HttpTransport(host="localhost", port=8000)

# Create an HTTP transport with host, port, and custom path
http_transport_custom_path = HttpTransport(host="localhost", port=8000, path="/custom-path")

# Create an HTTP transport with a custom timeout
http_transport_with_timeout = HttpTransport(url="http://localhost:8000/jsonrpc", timeout=60.0)
```

### Methods

#### initialize

```python
def initialize(self) -> None
```

Initializes the HTTP transport. This method is called automatically when the transport is first used.

#### shutdown

```python
def shutdown(self) -> None
```

Shuts down the HTTP transport and releases any resources. This method is called automatically when the transport is no longer needed.

#### send_request

```python
def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]
```

Sends a JSON-RPC request to the server over HTTP and returns the response.

**Parameters:**
- `rpc_request`: A JsonRpcRequest object representing the request to send.

**Returns:**
- A dictionary containing the JSON-RPC response.

**Raises:**
- `McpTransportError`: If there's an error sending the request or receiving the response.

**Example:**
```python
from mojentic_mcp.transports import HttpTransport
from mojentic_mcp.rpc import JsonRpcRequest

# Create an HTTP transport (using either a full URL or host/port)
http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")
# Or:
# http_transport = HttpTransport(host="localhost", port=8000)

# Create a JSON-RPC request
rpc_request = JsonRpcRequest(method="tools/list", params={})

# Send the request and get the response
response = http_transport.send_request(rpc_request)
```

## Class: StdioTransport

```python
from mojentic_mcp.transports import StdioTransport
```

`StdioTransport` is an implementation of `McpTransport` that communicates with MCP servers over standard input/output (STDIO).

### Constructor

```python
def __init__(self, command: List[str])
```

Creates a new StdioTransport instance.

**Parameters:**
- `command`: A list of strings representing the command to run the MCP server. The first element is the executable, and the rest are arguments.

**Example:**
```python
import sys
from mojentic_mcp.transports import StdioTransport

# Create a STDIO transport that runs a Python script
stdio_transport = StdioTransport(command=[sys.executable, "stdio_server.py"])

# Create a STDIO transport that runs a compiled executable
stdio_transport = StdioTransport(command=["./mcp_server"])
```

### Methods

#### initialize

```python
def initialize(self) -> None
```

Initializes the STDIO transport by starting the server subprocess. This method is called automatically when the transport is first used.

#### shutdown

```python
def shutdown(self) -> None
```

Shuts down the STDIO transport by terminating the server subprocess and releasing any resources. This method is called automatically when the transport is no longer needed.

#### send_request

```python
def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]
```

Sends a JSON-RPC request to the server over STDIO and returns the response.

**Parameters:**
- `rpc_request`: A JsonRpcRequest object representing the request to send.

**Returns:**
- A dictionary containing the JSON-RPC response.

**Raises:**
- `McpTransportError`: If there's an error sending the request or receiving the response.

**Example:**
```python
import sys
from mojentic_mcp.transports import StdioTransport
from mojentic_mcp.rpc import JsonRpcRequest

# Create a STDIO transport
stdio_transport = StdioTransport(command=[sys.executable, "stdio_server.py"])

# Create a JSON-RPC request
rpc_request = JsonRpcRequest(method="tools/list", params={})

# Send the request and get the response
response = stdio_transport.send_request(rpc_request)
```

## Exception: McpTransportError

```python
from mojentic_mcp.transports import McpTransportError
```

`McpTransportError` is an exception class for transport-related errors.

**Example:**
```python
try:
    response = transport.send_request(rpc_request)
except McpTransportError as e:
    print(f"Transport error: {e}")
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
