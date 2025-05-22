# Mojentic MCP

Mojentic MCP is a library providing MCP (Machine Conversation Protocol) server and client infrastructure for tools and agentic chat creators. It allows you to easily expose tools to AI assistants that support the MCP protocol.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## What is MCP?

The Machine Conversation Protocol (MCP) is a standardized protocol for communication between AI assistants and external tools or services. It enables AI models to:

- Discover available tools and capabilities
- Call external functions and receive results
- Access resources like files and databases
- Use predefined prompts for specific tasks

Mojentic MCP implements this protocol, making it easy to create servers that expose tools to AI assistants and clients that can interact with MCP servers.

## Key Features

- **HTTP Transport**: Expose the MCP protocol over HTTP using FastAPI
- **STDIO Transport**: Expose the MCP protocol over standard input/output
- **JSON-RPC 2.0 Handler**: Handle standard MCP requests and responses
- **Tool Integration**: Easily expose custom tools to AI assistants
- **MCP Protocol Support**: Implements the core MCP protocol methods

## Installation

```bash
pip install mojentic-mcp
```

## Quick Start

### HTTP Server Example

Create a simple HTTP MCP server with date-related tools:

```python
import logging
import sys

logging.basicConfig(level=logging.INFO)

from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

sys.stderr.write("Starting HTTP MCP server...\n")
sys.stderr.write("Server ready to receive commands\n")
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])
server = HttpMcpServer(rpc_handler)
server.run()
```

### STDIO Server Example

Create a simple STDIO MCP server with date-related tools:

```python
import logging
import sys

logging.basicConfig(level=logging.CRITICAL)

from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

from mojentic_mcp.mcp_stdio import StdioMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")
rpc_handler = JsonRpcHandler(tools=[ResolveDateTool(), CurrentDateTimeTool()])
server = StdioMcpServer(rpc_handler)
server.run()
```

## Next Steps

- Check out the [Tutorials](tutorials/index.md) for step-by-step guides
- Explore the [API Reference](api/index.md) for detailed documentation
- Learn about [Creating Custom Tools](tutorials/custom-tools.md)