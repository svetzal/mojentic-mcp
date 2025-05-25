# Mojentic MCP Examples

This directory contains example code demonstrating how to use the Mojentic MCP library for both server and client implementations. The examples are organized into `server/` and `client/` subdirectories.

## Server Examples

These examples in the `server/` directory demonstrate how to create MCP servers that expose tools to clients:

- **server/simple_http_server.py**: A basic HTTP MCP server with date-related tools
- **server/simple_stdio.py**: A basic STDIO MCP server with date-related tools
- **server/custom_tool_http.py**: An HTTP MCP server with a custom tool
- **server/task_list_tools_http.py**: An HTTP MCP server with task management tools

## Client Examples

These examples in the `client/` directory demonstrate how to use the McpClient to interact with MCP servers:

- **client/simple_http_client.py**: A basic client that connects to an HTTP MCP server
- **client/stdio_client_example.py**: A client that starts and communicates with a STDIO MCP server
- **client/multi_transport_client_example.py**: A client that connects to multiple MCP servers using different transports

## Running the Examples

### Server Examples

Start an HTTP server:
```bash
python -m src._examples.server.simple_http_server
```

Start a custom tool HTTP server on a different port:
```bash
# Set a different port using an environment variable
PORT=8001 python -m src._examples.server.custom_tool_http
```

### Client Examples

Run the HTTP client (requires a running HTTP server):
```bash
python -m src._examples.client.simple_http_client
```

Run the STDIO client (automatically starts the STDIO server as a subprocess):
```bash
python -m src._examples.client.stdio_client_example
```

Run the multi-transport client (requires multiple servers running):
```bash
python -m src._examples.client.multi_transport_client_example
```

## Example Workflow

1. Start the HTTP server in one terminal:
   ```bash
   python -m src._examples.server.simple_http_server
   ```

2. Start the custom tool HTTP server in another terminal:
   ```bash
   PORT=8001 python -m src._examples.server.custom_tool_http
   ```

3. Run the client examples in a third terminal:
   ```bash
   python -m src._examples.client.simple_http_client
   python -m src._examples.client.stdio_client_example
   python -m src._examples.client.multi_transport_client_example
   ```

## Notes

- The HTTP servers default to port 8000. Use the PORT environment variable to change this.
- The STDIO client example automatically starts the STDIO server as a subprocess.
- The multi-transport example assumes servers are running on ports 8000 and 8001.
- Error handling is demonstrated in all client examples.
