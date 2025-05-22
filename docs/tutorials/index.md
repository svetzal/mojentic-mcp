# Tutorials

Welcome to the Mojentic MCP tutorials! This section provides step-by-step guides to help you get started with the library and explore its features.

## Available Tutorials

- [HTTP Server Tutorial](http-server.md): Learn how to create an MCP server that exposes tools over HTTP
- [STDIO Server Tutorial](stdio-server.md): Learn how to create an MCP server that exposes tools over standard input/output
- [Creating Custom Tools](custom-tools.md): Learn how to create and expose custom tools to AI assistants
- [Client Usage Tutorial](client-usage.md): Learn how to use the McpClient to interact with MCP servers
- [Multi-Transport Client Tutorial](multi-transport.md): Learn how to use a client with multiple transport methods

## Example Workflow

Here's a typical workflow for using Mojentic MCP:

1. Start the HTTP server in one terminal:
   ```bash
   python -m src._examples.simple_http_server.py
   ```

2. Start the custom tool HTTP server in another terminal:
   ```bash
   PORT=8001 python -m src._examples.custom_tool_http.py
   ```

3. Run the client examples in a third terminal:
   ```bash
   python -m src._examples.http_client_example
   python -m src._examples.stdio_client_example
   python -m src._examples.multi_transport_client_example
   ```

## Notes

- The HTTP servers default to port 8000. Use the PORT environment variable to change this.
- The STDIO client example automatically starts the STDIO server as a subprocess.
- The multi-transport example assumes servers are running on ports 8000 and 8001.
- Error handling is demonstrated in all client examples.

## Next Steps

After going through these tutorials, you might want to:

- Check out the [API Reference](../api/index.md) for detailed documentation
- Explore more complex examples in the [src/_examples](https://github.com/svetzal/mojentic-mcp/tree/main/src/_examples) directory
- Contribute to the project on [GitHub](https://github.com/svetzal/mojentic-mcp)