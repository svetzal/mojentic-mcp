import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the client and transport classes
from mojentic_mcp.client import McpClient
from mojentic_mcp.transports import StdioTransport

def main():
    """
    Example of using the McpClient with a STDIO transport.
    
    This example starts a subprocess running the simple_stdio.py example
    and demonstrates how to:
    1. Initialize the client with a STDIO transport
    2. List available tools
    3. Call tools using the dynamic accessor
    4. Handle tool errors
    """
    # Get the path to the simple_stdio.py example
    # This assumes the script is run from the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stdio_server_path = os.path.join(script_dir, "simple_stdio.py")
    
    # Create a STDIO transport that runs the simple_stdio.py script as a subprocess
    # The StdioTransport will handle communication with the subprocess
    stdio_transport = StdioTransport(command=[sys.executable, stdio_server_path])
    
    # Initialize the client with the transport
    # The client will automatically discover available tools
    with McpClient(transports=[stdio_transport]) as client:
        # List all available tools
        tools = client.list_tools()
        logger.info(f"Discovered {len(tools)} tools from STDIO server:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # Using the dynamic tool accessor to call tools
        try:
            # Get the current date and time
            current_time = client.tools.current_datetime()
            logger.info(f"Current datetime: {current_time}")
            
            # Resolve a date string to a specific date
            resolved_date = client.tools.resolve_date(date_string="next Tuesday")
            logger.info(f"Resolved date: {resolved_date}")
            
            # Try another date resolution
            resolved_date = client.tools.resolve_date(date_string="2 weeks from now")
            logger.info(f"Date 2 weeks from now: {resolved_date}")
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
        
        # Demonstrate error handling with an invalid date string
        try:
            # This should cause an error in the tool
            invalid_date = client.tools.resolve_date(date_string="not a valid date")
            logger.info(f"Invalid date result: {invalid_date}")
        except Exception as e:
            logger.error(f"Expected error with invalid date: {e}")

if __name__ == "__main__":
    main()