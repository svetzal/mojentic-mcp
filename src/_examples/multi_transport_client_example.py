import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the client and transport classes
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import HttpTransport, StdioTransport

def main():
    """
    Example of using the McpClient with multiple transports.
    
    This example demonstrates how to:
    1. Initialize the client with both HTTP and STDIO transports
    2. List all available tools from all transports
    3. Call tools from different transports using a unified interface
    4. Understand the "first-wins" approach for tools with the same name
    
    Note: This example assumes you have both the HTTP server (simple_http.py)
    and a custom tool server (custom_tool_http.py) running on different ports.
    """
    # Create transports for different servers
    
    # HTTP transport for the simple_http.py server (date tools)
    http_transport1 = HttpTransport(url="http://localhost:8000/jsonrpc")
    
    # HTTP transport for the custom_tool_http.py server (user info tool)
    # Assuming it's running on a different port
    http_transport2 = HttpTransport(url="http://localhost:8001/jsonrpc")
    
    # STDIO transport for the simple_stdio.py server (also date tools)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stdio_server_path = os.path.join(script_dir, "simple_stdio.py")
    stdio_transport = StdioTransport(command=[sys.executable, stdio_server_path])
    
    # Initialize the client with multiple transports
    # The order matters for tools with the same name (first-wins)
    with McpClient(transports=[http_transport1, http_transport2, stdio_transport]) as client:
        # List all available tools from all transports
        tools = client.list_tools()
        logger.info(f"Discovered {len(tools)} unique tools from all transports:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # Demonstrate calling tools from different transports
        try:
            # Call date tools (from http_transport1 or stdio_transport, depending on order)
            current_time = client.tools.current_datetime()
            logger.info(f"Current datetime: {current_time}")
            
            resolved_date = client.tools.resolve_date(date_string="next Friday")
            logger.info(f"Resolved date: {resolved_date}")
            
            # Call user info tool (from http_transport2)
            # This assumes custom_tool_http.py is running and has the colour_preferences tool
            user_info = client.tools.colour_preferences()
            logger.info(f"User info: {user_info}")
            
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
        
        # Demonstrate the "first-wins" approach
        # If tools with the same name exist on multiple transports,
        # the client will use the one from the first transport in the list
        logger.info("\nDemonstrating 'first-wins' for tool discovery:")
        for tool_name in ["current_datetime", "resolve_date", "colour_preferences"]:
            schema = client.get_tool_schema(tool_name)
            if schema:
                logger.info(f"Tool '{tool_name}' is available from the first transport that provides it")
                # We could determine which transport it came from by checking the schema details
                # or by examining client._tool_to_transport_map (though that's an internal detail)
            else:
                logger.info(f"Tool '{tool_name}' is not available from any transport")

if __name__ == "__main__":
    main()