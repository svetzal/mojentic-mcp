import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mojentic_mcp.transports import HttpTransport
from mojentic_mcp.rpc import JsonRpcRequest

def main():
    # Create an HTTP transport pointing to a local MCP server
    http_transport = HttpTransport(host="localhost", port=8080)
    
    logger.info("Connecting to HTTP MCP server on localhost:8080...")
    http_transport.initialize()
    
    try:
        # Create a ping request
        ping_request = JsonRpcRequest(method="ping", params={}, id="ping_test_1")
        
        # Send the request
        logger.info("Sending ping request...")
        response = http_transport.send_request(ping_request)
        
        # Print the response
        logger.info(f"Received response: {response}")
        
        if "result" in response and "status" in response["result"] and response["result"]["status"] == "ok":
            logger.info("Ping successful!")
        else:
            logger.error("Ping failed!")
    finally:
        # Shutdown the transport
        http_transport.shutdown()

if __name__ == "__main__":
    main()