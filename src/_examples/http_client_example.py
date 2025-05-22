import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the client and transport classes
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport

def main():
    """
    Example of using the McpClient with an HTTP transport.
    
    This example connects to a local HTTP MCP server (like the one in simple_http.py)
    and demonstrates how to:
    1. Initialize the client with an HTTP transport
    2. List available tools
    3. Get details about a specific tool
    4. Call tools using both direct method and dynamic accessor
    """
    # Create an HTTP transport pointing to a local MCP server
    # Assuming the server from simple_http.py is running on the default port
    http_transport = HttpTransport(url="http://localhost:8000/jsonrpc")
    
    # Initialize the client with the transport
    # The client will automatically discover available tools
    with McpClient(transports=[http_transport]) as client:
        # List all available tools
        tools = client.list_tools()
        logger.info(f"Discovered {len(tools)} tools:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # Get schema for a specific tool (if it exists)
        # The tools available depend on what the server provides
        # In simple_http.py, we expect 'current_datetime' and 'resolve_date'
        current_datetime_schema = client.get_tool_schema("current_datetime")
        if current_datetime_schema:
            logger.info(f"Tool 'current_datetime' schema: {current_datetime_schema}")
        
        # Call a tool directly using call_tool method
        try:
            # Get the current date and time
            result = client.call_tool("current_datetime")
            logger.info(f"Current datetime result: {result}")
            
            # Resolve a date string to a specific date
            # This demonstrates passing arguments to a tool
            date_result = client.call_tool("resolve_date", date_string="next Monday")
            logger.info(f"Resolved date result: {date_result}")
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
        
        # Using the dynamic tool accessor (more Pythonic)
        try:
            # Same calls as above but using the dynamic accessor
            current_time = client.tools.current_datetime()
            logger.info(f"Current datetime (via accessor): {current_time}")
            
            resolved_date = client.tools.resolve_date(date_string="next Friday")
            logger.info(f"Resolved date (via accessor): {resolved_date}")
        except Exception as e:
            logger.error(f"Error using tool accessor: {e}")

if __name__ == "__main__":
    main()