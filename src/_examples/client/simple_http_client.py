import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

# Create an HTTP transport pointing to a local MCP server
# You can use either a full URL:
# http_transport = HttpTransport(url="http://localhost:8080/jsonrpc")
# Or host and port (with default path "/jsonrpc"):
http_transport = HttpTransport(host="localhost", port=8080)

logger.info("Connecting to HTTP MCP server on localhost:8080...")
with McpClient(transports=[http_transport]) as client:
    # List all available tools
    tools = client.list_tools()
    logger.info(f"Discovered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', 'No description')}")

    # Call tools using the direct method
    try:
        # Get the current date and time
        result = client.call_tool("get_current_datetime")
        print(f"Current datetime: {result}")

        # Resolve a date string to a specific date
        date_result = client.call_tool("resolve_date", relative_date_found="next Monday")
        print(f"Resolved date for 'next Monday': {date_result}")
    except Exception as e:
        logger.error(f"Error calling tool: {e}")

    # Call tools using the dynamic accessor (more Pythonic)
    try:
        # Get the current date and time
        current_time = client.tools.get_current_datetime()
        print(f"Current datetime (via accessor): {current_time}")

        # Resolve a date string to a specific date
        resolved_date = client.tools.resolve_date(relative_date_found="next Friday")
        print(f"Resolved date for 'next Friday' (via accessor): {resolved_date}")
    except Exception as e:
        logger.error(f"Error using tool accessor: {e}")
