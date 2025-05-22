# STDIO Server API

The Mojentic MCP library provides a STDIO server implementation for exposing MCP functionality over standard input/output (STDIO).

::: mojentic_mcp.mcp_stdio.StdioMcpServer
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.mcp_stdio.start_server
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

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
