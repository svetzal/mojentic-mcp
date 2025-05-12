"""Common RPC infrastructure for Mojentic MCP.

This module provides a common JSONRPC infrastructure that can be used by different
transport mechanisms (HTTP, STDIO, etc.) to handle RPC requests.
"""

from importlib.metadata import version
from typing import Dict, Any, Optional, List

from mojentic.llm.tools.llm_tool import LLMTool
from pydantic import BaseModel, Field




class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request model."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Optional[Any] = Field(None, description="Request ID")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")


class JsonRpcError(Exception):
    """Exception raised for JSON-RPC errors."""

    def __init__(self, code: int, message: str, data: Any = None):
        """Initialize a JSON-RPC error.

        Args:
            code (int): The error code
            message (str): The error message
            data (Any, optional): Additional error data. Defaults to None.
        """
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class JsonRpcHandler:
    """Base class for handling JSON-RPC 2.0 requests."""

    def __init__(self, tools: List[LLMTool]):
        """Initialize the JSON-RPC handler.

        Args:
            tools (List[LLMTool]): List of tools to serve.
        """
        self.should_exit = False

        # Initialize tools
        self.tools: List[LLMTool] = tools

        self.methods = {
            "initialize": self._handle_initialize,
            "exit": self._handle_exit,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "prompts/list": self._handle_prompts_list,
        }

    def handle_request(self, request: JsonRpcRequest) -> Dict[str, Any]:
        """Handle a JSON-RPC 2.0 request.

        Args:
            request (JsonRpcRequest): The JSON-RPC request

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        method = request.method
        request_id = request.id
        params = request.params or {}

        # Check if the method exists
        if method not in self.methods:
            return self._create_error_response(
                request_id,
                -32601,
                f"Method not found: {method}"
            )

        # Call the method handler
        try:
            result = self.methods[method](params)
            return self._create_result_response(request_id, result)
        except JsonRpcError as e:
            return self._create_error_response(
                request_id,
                e.code,
                e.message,
                e.data
            )
        except Exception as e:
            return self._create_error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )

    def _create_result_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 result response.

        Args:
            request_id (Any): The request ID
            result (Any): The result

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def _create_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 error response.

        Args:
            request_id (Any): The request ID
            code (int): The error code
            message (str): The error message
            data (Any, optional): Additional error data. Defaults to None.

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the initialize method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        protocol_version = params.get("protocolVersion")
        capabilities = params.get("capabilities", {})

        return {
            "serverInfo": {
                "name": "Mojentic MCP",
                "version": version("mojentic-mcp")
            },
            "capabilities": {
                "examineProvider": True
            },
            "protocolVersion": protocol_version
        }


    def _handle_exit(self, params: Dict[str, Any]) -> None:
        """Handle the exit method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            None: No result
        """
        self.should_exit = True
        return None

    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the tools/list method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        tools_list = []
        for tool in self.tools:
            descriptor = tool.descriptor
            tools_list.append({
                "name": descriptor["function"]["name"],
                "description": descriptor["function"]["description"]
            })

        return {
            "tools": tools_list
        }

    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the tools/call method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})

        # Find the tool with the given name
        tool = next((t for t in self.tools if t.descriptor["function"]["name"] == tool_name), None)

        if tool is None:
            raise JsonRpcError(-32601, f"Tool not found: {tool_name}")

        return tool.run(**tool_arguments)

    def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the resources/list method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result with empty resources list
        """
        return {
            "resources": [],
            "nextCursor": None
        }

    def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the prompts/list method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result with empty prompts list
        """
        return {
            "prompts": [],
            "nextCursor": None
        }
