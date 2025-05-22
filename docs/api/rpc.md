# JSON-RPC Handler API

The Mojentic MCP library provides a JSON-RPC 2.0 handler for processing MCP requests and responses.

::: mojentic_mcp.rpc.JsonRpcErrorCode
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.rpc.JsonRpcRequest
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.rpc.JsonRpcError
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: mojentic_mcp.rpc.JsonRpcHandler
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

## JSON-RPC 2.0 Protocol

The JSON-RPC 2.0 protocol is a stateless, light-weight remote procedure call (RPC) protocol. It defines several data structures and the rules around their processing.

### Request Object

A request object has the following members:

- `jsonrpc`: A string specifying the version of the JSON-RPC protocol. Must be exactly "2.0".
- `method`: A string containing the name of the method to be invoked.
- `params`: An object or array that holds the parameter values to be used during the invocation of the method. This member may be omitted.
- `id`: A string or number that identifies this request. If omitted, the request is considered a notification.

Example:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": "request-id"
}
```

### Response Object

A response object has the following members:

- `jsonrpc`: A string specifying the version of the JSON-RPC protocol. Must be exactly "2.0".
- `result`: The result of the method invocation. This member is required on success.
- `error`: An error object if there was an error invoking the method. This member is required on error.
- `id`: The id of the request this response is for. If there was an error in detecting the id in the request, it must be null.

Example (success):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "get_time",
        "description": "Get the current time",
        "inputSchema": {
          "type": "object",
          "properties": {}
        }
      }
    ],
    "nextCursor": null
  },
  "id": "request-id"
}
```

Example (error):
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": "request-id"
}
```

### Error Object

An error object has the following members:

- `code`: A number that indicates the error type that occurred.
- `message`: A string providing a short description of the error.
- `data`: A primitive or structured value that contains additional information about the error. This may be omitted.

## Standard Error Codes

The JSON-RPC 2.0 specification defines several standard error codes:

- `-32700`: Parse error - Invalid JSON was received by the server.
- `-32600`: Invalid Request - The JSON sent is not a valid Request object.
- `-32601`: Method not found - The method does not exist / is not available.
- `-32602`: Invalid params - Invalid method parameter(s).
- `-32603`: Internal error - Internal JSON-RPC error.
- `-32000` to `-32099`: Server error - Reserved for implementation-defined server-errors.

## See Also

- [HTTP Server API](http-server.md): Documentation for the HTTP server implementation.
- [STDIO Server API](stdio-server.md): Documentation for the STDIO server implementation.
- [Transports API](transports.md): Documentation for the transport classes.
