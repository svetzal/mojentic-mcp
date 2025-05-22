from typing import Any, Callable, Dict, List, Optional, Tuple, Set
import json

import structlog

from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError # Assuming JsonRpcErrorCode is not directly used by client logic but by errors it catches
from mojentic_mcp.transports import McpTransport, McpTransportError

logger = structlog.get_logger()


class ToolDescriptor(Dict[str, Any]): 
    """Represents the description of a tool as provided by MCP's tools/list."""
    pass


class McpClient:
    """A client for interacting with MCP servers via one or more transports."""

    def __init__(self, transports: List[McpTransport]):
        if not transports:
            raise ValueError("At least one transport must be provided.")
        self._transports = transports
        self._tool_to_transport_map: Dict[str, McpTransport] = {}
        self._tool_schemas: Dict[str, ToolDescriptor] = {} 
        
        self.tools: ToolAccessor = ToolAccessor(self)

        self._initialize_transports_and_discover_tools()

    def _initialize_transports_and_discover_tools(self) -> None:
        """Initializes all transports and discovers tools from them."""
        all_discovered_tools_with_transport: List[Tuple[ToolDescriptor, McpTransport]] = []
        # Use a consistent ID for tools/list requests from the client for simplicity
        tools_list_request_id = "mcp_client_tools_list_1"


        for transport_idx, transport in enumerate(self._transports):
            transport_name = f"{type(transport).__name__}_{transport_idx}"
            try:
                transport.initialize() 
                
                # MCP Initialize call (optional for client, but good for server to know client caps)
                # For PoC, we'll keep it simple. A full client might send its own capabilities.
                # init_params = {"protocolVersion": "2025-03-26", "capabilities": {"clientInfo": {"name": "MojenticMcpClient"}}}
                # init_request = JsonRpcRequest(method="initialize", params=init_params, id=f"mcp_client_init_{transport_idx}")
                # init_response = transport.send_request(init_request)
                # logger.debug("MCP Initialize response from transport", transport_name=transport_name, response=init_response)


                list_request = JsonRpcRequest(method="tools/list", params={}, id=tools_list_request_id)
                response = transport.send_request(list_request)
                
                if "result" in response and isinstance(response["result"], dict) and "tools" in response["result"]:
                    tools_on_this_transport = response["result"]["tools"]
                    if isinstance(tools_on_this_transport, list):
                        logger.info(f"Discovered {len(tools_on_this_transport)} tools on transport", transport_name=transport_name)
                        for tool_desc in tools_on_this_transport:
                            if isinstance(tool_desc, dict) and "name" in tool_desc:
                                all_discovered_tools_with_transport.append((tool_desc, transport))
                            else:
                                logger.warn("Invalid tool descriptor format from transport", transport_name=transport_name, tool_desc=tool_desc)
                    else:
                        logger.warn("tools/list response 'tools' field is not a list", transport_name=transport_name, response_result=response["result"])
                else:
                    logger.warn("tools/list response did not contain a valid result with tools", transport_name=transport_name, response=response)
            except (McpTransportError, JsonRpcError) as e:
                logger.error("Failed to list tools from transport during initialization", transport_name=transport_name, exc_info=True)
            except Exception as e: # Catch any other unexpected error during init of a transport
                logger.error("Unexpected error initializing transport or listing tools", transport_name=transport_name, exc_info=True)

        unique_tool_names: Set[str] = set()
        for tool_desc, transport in all_discovered_tools_with_transport:
            tool_name = tool_desc.get("name")
            if tool_name and isinstance(tool_name, str) and tool_name not in unique_tool_names:
                unique_tool_names.add(tool_name)
                self._tool_to_transport_map[tool_name] = transport
                self._tool_schemas[tool_name] = tool_desc 
                logger.debug(f"Registered tool '{tool_name}' from transport {type(transport).__name__}")
        
        logger.info(f"Total unique tools discovered and registered: {len(self._tool_to_transport_map)}")

    def list_tools(self) -> List[ToolDescriptor]:
        """Lists all unique tools available from the configured transports.

        Returns:
            A list of tool descriptors (schemas).
        """
        return list(self._tool_schemas.values())

    def get_tool_schema(self, tool_name: str) -> Optional[ToolDescriptor]:
        """Gets the schema for a specific tool based on the 'first-wins' discovery.

        Args:
            tool_name: The name of the tool.

        Returns:
            The tool descriptor (schema) if found, else None.
        """
        return self._tool_schemas.get(tool_name)

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Calls a tool on the appropriate MCP server.

        Args:
            tool_name: The name of the tool to call.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The 'result' part of the JSON-RPC response from the tool execution.
            Typically this is a dict like `{"content": [...], "isError": ...}`.

        Raises:
            ValueError: If the tool is not found.
            McpClientError: For client-specific errors or if the tool execution itself reports an error.
            McpTransportError: If a transport layer error occurs.
            JsonRpcError: If the server returns a JSON-RPC protocol error.
        """
        if tool_name not in self._tool_to_transport_map:
            logger.error("Tool not found for call", tool_name=tool_name, available_tools=list(self._tool_to_transport_map.keys()))
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self._tool_to_transport_map.keys())}")

        transport = self._tool_to_transport_map[tool_name]
        
        call_params = {"name": tool_name, "arguments": kwargs}
        # Using a simple request ID strategy for client calls
        request_id = f"mcp_client_call_{tool_name}_{sum(ord(c) for c in json.dumps(kwargs, sort_keys=True)) if kwargs else 'noargs'}"
        
        rpc_request = JsonRpcRequest(method="tools/call", params=call_params, id=request_id)
        
        logger.info("Calling tool", tool_name=tool_name, transport=type(transport).__name__, params_length=len(kwargs))
        try:
            response = transport.send_request(rpc_request)
            
            if "result" in response and isinstance(response["result"], dict):
                tool_result_payload = response["result"]
                
                if tool_result_payload.get("isError"):
                    error_content = tool_result_payload.get("content", [])
                    error_message = f"Tool '{tool_name}' execution reported an error on the server."
                    if error_content and isinstance(error_content, list) and error_content[0].get("text"):
                        error_message = error_content[0]["text"]
                    logger.error("Tool call resulted in a server-side execution error", tool_name=tool_name, server_response_result=tool_result_payload)
                    raise McpToolExecutionError(error_message, tool_result_payload)

                logger.info("Tool call successful", tool_name=tool_name, result_keys=list(tool_result_payload.keys()))
                return tool_result_payload 
            
            # If 'error' is in response, transport should have raised JsonRpcError
            # This handles cases where response is malformed (e.g. no 'result' and no 'error')
            logger.error("Tool call response missing 'result' and no 'error' field was processed by transport", 
                         tool_name=tool_name, response=response)
            raise McpClientError(f"Invalid response from server for tool '{tool_name}': Malformed response.")

        except (McpTransportError, JsonRpcError) as e: # Re-raise known transport/RPC errors
            logger.error(f"Error calling tool '{tool_name}' (transport/RPC)", exc_info=True)
            raise
        except McpToolExecutionError: # Re-raise our custom tool error
            raise
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error calling tool '{tool_name}'", exc_info=True)
            raise McpClientError(f"Unexpected error calling tool '{tool_name}': {e}") from e

    def shutdown(self) -> None:
        """Shuts down all managed transports."""
        logger.info("Shutting down McpClient and its transports.")
        for transport_idx, transport in enumerate(self._transports):
            transport_name = f"{type(transport).__name__}_{transport_idx}"
            try:
                transport.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down transport {transport_name}", exc_info=True)
    
    def __enter__(self):
        # Initialization including transport init and tool discovery happens in __init__
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


class ToolAccessor:
    """Provides dynamic attribute access for calling tools via an McpClient."""
    def __init__(self, client: McpClient):
        # Use a "private" name to avoid potential clashes with actual tool names.
        self._mcp_client_instance = client

    def __getattr__(self, name: str) -> Callable[..., Any]:
        # Check if the tool 'name' is known to the client.
        # Accessing _tool_to_transport_map directly for efficiency, assuming it's stable after client init.
        if name in self._mcp_client_instance._tool_to_transport_map:
            def tool_caller(**kwargs: Any) -> Any:
                return self._mcp_client_instance.call_tool(name, **kwargs)
            
            # Enhance the callable with docstring and schema if available
            tool_schema = self._mcp_client_instance.get_tool_schema(name)
            if tool_schema:
                tool_caller.__doc__ = tool_schema.get("description", f"Calls the MCP tool '{name}'.")
                # You could attach the schema directly: setattr(tool_caller, 'schema', tool_schema)
            else:
                tool_caller.__doc__ = f"Calls the MCP tool '{name}'."
            return tool_caller
        
        raise AttributeError(f"'{type(self._mcp_client_instance).__name__}.tools' has no attribute '{name}'. "
                             f"Available tools: {list(self._mcp_client_instance._tool_to_transport_map.keys())}")


class McpClientError(Exception):
    """Base exception for McpClient related errors."""
    pass

class McpToolExecutionError(McpClientError):
    """Exception raised when a tool call results in an error reported by the tool itself (isError: true)."""
    def __init__(self, message: str, tool_result_payload: Dict[str, Any]):
        super().__init__(message)
        self.tool_result_payload = tool_result_payload