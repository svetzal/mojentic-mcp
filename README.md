# Mojentic-MCP

Mojentic MCP is a library providing MCP (Machine Conversation Protocol) server and client infrastructure for tools and agentic chat creators. It allows you to easily expose tools to AI assistants that support the MCP protocol.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Features

- **HTTP Transport**: Expose the MCP protocol over HTTP using FastAPI
- **STDIO Transport**: Expose the MCP protocol over standard input/output
- **JSON-RPC 2.0 Handler**: Handle standard MCP requests and responses
- **Tool Integration**: Easily expose custom tools to AI assistants
- **MCP Protocol Support**: Implements the core MCP protocol methods. Currently, the primary focus is on the `tools` capabilities (`tools/list`, `tools/call`). Other methods like `resources/list` and `prompts/list` are stubbed to return empty lists for broader MCP compatibility.

## 🔧 Installation

```bash
pip install mojentic-mcp
```

## 🚦 Quick Start

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
# Create an HTTP MCP server with the default path ("/jsonrpc")
server = HttpMcpServer(rpc_handler)
# Or specify a custom path
# server = HttpMcpServer(rpc_handler, path="/custom-path")
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

## 🛠️ Creating Custom Tools

You can create custom tools by extending the `LLMTool` class:

```python
from mojentic.llm.tools.llm_tool import LLMTool
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

class AboutTheUser(LLMTool):
    def run(self):
        return {
            "name": "Stacey",
            "favourite_colour": "purple"
        }

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "colour_preferences",
                "description": "Return the user's favourite colour.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        }

rpc_handler = JsonRpcHandler(tools=[AboutTheUser()])
server = HttpMcpServer(rpc_handler)
server.run()
```

## 📋 Task Management Example

Create a set of related tools that share state:

```python
from mojentic.llm.tools.ephemeral_task_manager import EphemeralTaskList, AppendTaskTool, PrependTaskTool, \
    InsertTaskAfterTool, StartTaskTool, CompleteTaskTool, ListTasksTool, ClearTasksTool

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

task_list = EphemeralTaskList()
rpc_handler = JsonRpcHandler(tools=[
    AppendTaskTool(task_list),
    PrependTaskTool(task_list),
    InsertTaskAfterTool(task_list),
    StartTaskTool(task_list),
    CompleteTaskTool(task_list),
    ListTasksTool(task_list),
    ClearTasksTool(task_list),
])
server = HttpMcpServer(rpc_handler)
server.run()
```

## 📚 MCP Protocol Reference

The library implements the following core JSON-RPC methods as specified by the MCP protocol. While methods for `resources` and `prompts` are present for MCP compatibility (returning empty lists), the current implementation is focused on delivering robust `tools` functionality.

| Method | Description |
|--------|-------------|
| **initialize** | Negotiates protocol version and capabilities |
| **tools/list** | Lists available tools |
| **tools/call** | Calls a tool with arguments |
| **resources/list** | Lists available resources |
| **prompts/list** | Lists available prompts |

## 🔌 Client-Side API

The client-side API allows developers to easily interact with MCP servers. It supports multiple transports (HTTP, STDIO) and provides an idiomatic Python interface for tool discovery and invocation.

### Initialization

```python
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

# Define one or more transports
# You can initialize HttpTransport with a full URL:
http_transport = HttpTransport(url="http://localhost:8080/jsonrpc")
# Or with host, port, and an optional path (defaults to "/jsonrpc"):
http_transport_alt = HttpTransport(host="localhost", port=8080)
# Or with a custom path:
http_transport_custom = HttpTransport(host="localhost", port=8080, path="/custom-path")

stdio_transport = StdioTransport(command="/usr/local/bin/my_mcp_server_command")

# Initialize the client with a list of transports
client = McpClient(transports=[http_transport, stdio_transport])
```

### Tool Invocation

Tools will be accessible as methods on a `tools` attribute of the client object:

```python
# List available tools (aggregated from all transports)
tools_list = client.list_tools()

# Invoke a tool (client determines the correct transport)
resolved_date_result = client.tools.resolve_date(date_string="next Monday")
forecast_result = client.tools.get_weather_forecast(location="New York", days=3)
```

## 📚 Documentation

Visit [the documentation](https://svetzal.github.io/mojentic-mcp/) for comprehensive guides, API reference, and examples.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
