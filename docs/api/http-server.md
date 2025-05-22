# HTTP Server API

The Mojentic MCP library provides an HTTP server implementation for exposing MCP functionality over HTTP using FastAPI.

::: mojentic_mcp.mcp_http.HttpMcpServer
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.mcp_http.start_server
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

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
