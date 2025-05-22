# HTTP Server API

The Mojentic MCP library provides an HTTP server implementation for exposing MCP functionality over HTTP using FastAPI.

## Class: HttpMcpServer

```python
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

server = HttpMcpServer(rpc_handler=JsonRpcHandler(tools=[...]))
```

`HttpMcpServer` is a class that creates an HTTP server for handling MCP requests over JSON-RPC.

### Constructor

```python
def __init__(self, rpc_handler: JsonRpcHandler, path: str = "/jsonrpc")
```

Creates a new HttpMcpServer instance.

**Parameters:**
- `rpc_handler`: A JsonRpcHandler instance that will handle the JSON-RPC requests.
- `path` (optional): The path to serve the JSON-RPC endpoint on. Defaults to "/jsonrpc".

**Example:**
```python
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with tools
rpc_handler = JsonRpcHandler(tools=[CurrentDateTimeTool()])

# Create an HTTP MCP server with the default path ("/jsonrpc")
server = HttpMcpServer(rpc_handler)

# Or create an HTTP MCP server with a custom path
# server = HttpMcpServer(rpc_handler, path="/custom-path")
```

### Methods

#### run

```python
def run(self, host: str = "0.0.0.0", port: int = 8080)
```

Runs the HTTP MCP server.

**Parameters:**
- `host` (optional): The host to bind to. Default is "0.0.0.0" (all interfaces).
- `port` (optional): The port to listen on. Default is 8080.

**Example:**
```python
# Run the server on the default host and port
server.run()

# Run the server on a specific host and port
server.run(host="127.0.0.1", port=8000)
```

#### handle_jsonrpc

```python
async def handle_jsonrpc(self, request: Request) -> Response
```

Handles JSON-RPC 2.0 requests. This method is registered as the handler for the `/jsonrpc` endpoint.

**Parameters:**
- `request`: The FastAPI request object.

**Returns:**
- A FastAPI Response object containing the JSON-RPC response.

**Note:** This method is typically not called directly but is used internally by FastAPI when a request is received.

## Function: start_server

```python
from mojentic_mcp.mcp_http import start_server
from mojentic_mcp.rpc import JsonRpcHandler

start_server(port=8080, rpc_handler=JsonRpcHandler(tools=[...]), path="/jsonrpc")
```

`start_server` is a convenience function that creates and runs an HttpMcpServer.

**Parameters:**
- `port`: The port to run the server on.
- `rpc_handler`: The JSON-RPC handler to use.
- `path` (optional): The path to serve the JSON-RPC endpoint on. Defaults to "/jsonrpc".

**Example:**
```python
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic_mcp.mcp_http import start_server
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with tools
rpc_handler = JsonRpcHandler(tools=[CurrentDateTimeTool()])

# Start the server with the default path ("/jsonrpc")
start_server(port=8000, rpc_handler=rpc_handler)

# Or start the server with a custom path
# start_server(port=8000, rpc_handler=rpc_handler, path="/custom-path")
```

## JSON-RPC Endpoint

The HTTP server exposes a single JSON-RPC endpoint. By default, this endpoint is at `/jsonrpc`, but it can be customized using the `path` parameter when creating the server. This endpoint accepts POST requests with JSON-RPC 2.0 payloads.

### Request Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "method-name",
  "params": {}
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {}
}
```

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32000,
    "message": "Error message"
  }
}
```

## Error Handling

The HTTP server handles various error conditions:

1. **Invalid JSON**: If the request body is not valid JSON, a parse error is returned (code -32700).

2. **Invalid Request**: If the request does not conform to the JSON-RPC 2.0 specification, an invalid request error is returned (code -32600).

3. **Internal Error**: If an unexpected error occurs while processing the request, an internal error is returned (code -32603).

## Environment Variables

The HTTP server can be configured using environment variables:

- `PORT`: The port to listen on. This overrides the port parameter passed to the `run` method.

**Example:**
```bash
PORT=8001 python -m mojentic_mcp.mcp_http
```

## Command Line Usage

The HTTP server can be run directly from the command line:

```bash
python -m mojentic_mcp.mcp_http <port>
```

**Example:**
```bash
python -m mojentic_mcp.mcp_http 8000
```

## Best Practices

1. **Use a Dedicated Port**: Choose a port that is not used by other services.

2. **Configure Logging**: Set up appropriate logging to monitor server activity.

3. **Secure the Server**: If exposing the server to the internet, consider using HTTPS and authentication.

4. **Handle Errors Gracefully**: Ensure that your tools handle errors gracefully to avoid server crashes.

## See Also

- [STDIO Server API](stdio-server.md): Documentation for the STDIO server implementation.
- [JsonRpcHandler API](rpc.md): Documentation for the JSON-RPC handler used by the server.
- [HTTP Server Tutorial](../tutorials/http-server.md): Step-by-step guide to creating an HTTP MCP server.
