# STDIO Server API

The Mojentic MCP library provides a STDIO server implementation for exposing MCP functionality over standard input/output (STDIO).

## Class: StdioMcpServer

```python
from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

server = StdioMcpServer(rpc_handler=JsonRpcHandler(tools=[...]))
```

`StdioMcpServer` is a class that creates a server for handling MCP requests over STDIO using JSON-RPC.

### Constructor

```python
def __init__(self, rpc_handler: JsonRpcHandler)
```

Creates a new StdioMcpServer instance.

**Parameters:**
- `rpc_handler`: A JsonRpcHandler instance that will handle the JSON-RPC requests.

**Example:**
```python
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with tools
rpc_handler = JsonRpcHandler(tools=[CurrentDateTimeTool()])

# Create a STDIO MCP server
server = StdioMcpServer(rpc_handler)
```

### Methods

#### run

```python
def run(self) -> None
```

Runs the STDIO MCP server loop, reading requests from standard input and writing responses to standard output.

**Example:**
```python
# Run the server
server.run()
```

#### _read_request

```python
def _read_request(self) -> Dict[str, Any]
```

Reads a JSON request from standard input.

**Returns:**
- A dictionary containing the parsed JSON request.

**Note:** This method is typically not called directly but is used internally by the `run` method.

#### _write_response

```python
def _write_response(self, response: Dict[str, Any]) -> None
```

Writes a JSON response to standard output.

**Parameters:**
- `response`: The response to write.

**Note:** This method is typically not called directly but is used internally by the `run` method.

#### _write_info

```python
def _write_info(self, message: str, status: Optional[str] = "info") -> None
```

Writes an informational message to standard error.

**Parameters:**
- `message`: The message to write.
- `status` (optional): The status to include in the message. Default is "info".

**Note:** This method is typically not called directly but is used internally by the `run` method.

#### _handle_request

```python
def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]
```

Handles a single request.

**Parameters:**
- `request`: The request to handle.

**Returns:**
- A dictionary containing the response.

**Note:** This method is typically not called directly but is used internally by the `run` method.

## Function: start_server

```python
from mojentic_mcp.mcp_stdio import start_server
from mojentic_mcp.rpc import JsonRpcHandler

start_server(rpc_handler=JsonRpcHandler(tools=[...]))
```

`start_server` is a convenience function that creates and runs a StdioMcpServer.

**Parameters:**
- `rpc_handler`: The JSON-RPC handler to use.

**Example:**
```python
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic_mcp.mcp_stdio import start_server
from mojentic_mcp.rpc import JsonRpcHandler

# Create a JSON-RPC handler with tools
rpc_handler = JsonRpcHandler(tools=[CurrentDateTimeTool()])

# Start the server
start_server(rpc_handler=rpc_handler)
```

## Communication Protocol

The STDIO server communicates using JSON-RPC 2.0 over standard input/output:

1. The server reads JSON-RPC requests from standard input, one request per line.
2. The server writes JSON-RPC responses to standard output, one response per line.
3. The server writes informational messages to standard error.

### JSON-RPC Request Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "method-name",
  "params": {}
}
```

### JSON-RPC Response Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {}
}
```

### JSON-RPC Error Response Format

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

### Informational Message Format

```json
{
  "status": "info",
  "message": "Informational message"
}
```

## Legacy Command Support

In addition to JSON-RPC 2.0, the STDIO server also supports a legacy command-based protocol:

### Ping Command

```json
{
  "command": "ping"
}
```

Response:
```json
{
  "status": "success",
  "message": "pong"
}
```

### Exit Command

```json
{
  "command": "exit"
}
```

Response:
```json
{
  "status": "success",
  "message": "Server exiting"
}
```

### Examine Command

```json
{
  "command": "examine",
  "query": "query text"
}
```

This command is converted to a JSON-RPC `tools/call` request for the `examine` tool.

## Error Handling

The STDIO server handles various error conditions:

1. **Invalid JSON**: If the request is not valid JSON, an error response is returned.

2. **Invalid Request**: If the request does not conform to the JSON-RPC 2.0 specification, an invalid request error is returned (code -32600).

3. **Unknown Command**: If a legacy command is not recognized, an error response is returned.

4. **Server Error**: If an unexpected error occurs while processing the request, an error response is returned.

## Command Line Usage

The STDIO server can be run directly from the command line:

```bash
python -m mojentic_mcp.mcp_stdio
```

## Best Practices

1. **Use Line-Delimited JSON**: Each request and response should be a single line of JSON.

2. **Handle EOF**: The server will exit when it receives an EOF (end of file) on standard input.

3. **Use Standard Error for Logging**: Write log messages to standard error to avoid interfering with the JSON-RPC communication.

4. **Handle Errors Gracefully**: Ensure that your tools handle errors gracefully to avoid server crashes.

## See Also

- [HTTP Server API](http-server.md): Documentation for the HTTP server implementation.
- [JsonRpcHandler API](rpc.md): Documentation for the JSON-RPC handler used by the server.
- [STDIO Server Tutorial](../tutorials/stdio-server.md): Step-by-step guide to creating a STDIO MCP server.