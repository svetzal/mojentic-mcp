\
from unittest.mock import Mock, patch, call, ANY

import pytest

from mojentic_mcp.client import McpClient, McpClientError, McpToolExecutionError, ToolAccessor
from mojentic_mcp.transports import McpTransport, McpTransportError, HttpTransport # Import a concrete one for some tests
from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError, JsonRpcErrorCode


@pytest.fixture
def mock_transport_base(mocker):
    """Creates a base mock McpTransport."""
    transport = Mock(spec=McpTransport)
    transport.initialize = Mock()
    transport.shutdown = Mock()
    # Default send_request to avoid NotImplementError if not overridden by specific test
    transport.send_request = Mock(return_value={"jsonrpc": "2.0", "id": ANY, "result": {}}) 
    return transport

@pytest.fixture
def mock_transport1(mock_transport_base, mocker):
    """Transport 1: provides tool_a, shared_tool."""
    # Result for tools/list
    list_result1 = {
        "tools": [
            {"name": "tool_a", "description": "Tool A from T1", "inputSchema": {"type": "object"}},
            {"name": "shared_tool", "description": "Shared tool from T1", "inputSchema": {"type": "object"}},
        ]
    }
    # Result for tools/call for tool_a
    call_result_tool_a = {"content": [{"type": "text", "text": "tool_a_result_from_t1"}], "isError": False}
    # Result for tools/call for shared_tool
    call_result_shared_tool_t1 = {"content": [{"type": "text", "text": "shared_tool_result_from_t1"}], "isError": False}

    def side_effect_t1(req: JsonRpcRequest):
        if req.method == "tools/list":
            return {"jsonrpc": "2.0", "id": req.id, "result": list_result1}
        if req.method == "tools/call":
            if req.params["name"] == "tool_a":
                return {"jsonrpc": "2.0", "id": req.id, "result": call_result_tool_a}
            if req.params["name"] == "shared_tool":
                return {"jsonrpc": "2.0", "id": req.id, "result": call_result_shared_tool_t1}
        raise McpTransportError(f"Unhandled mock request in transport1: {req.method} {req.params.get('name', '')}")
    
    mock_transport_base.send_request.side_effect = side_effect_t1
    return mock_transport_base


@pytest.fixture
def mock_transport2(mock_transport_base, mocker): # Uses a new instance of mock_transport_base
    # Need a distinct mock object for transport2
    transport2 = Mock(spec=McpTransport)
    transport2.initialize = Mock()
    transport2.shutdown = Mock()

    list_result2 = {
        "tools": [
            {"name": "tool_b", "description": "Tool B from T2", "inputSchema": {"type": "object"}},
            {"name": "shared_tool", "description": "Shared tool from T2 (ignored by client)", "inputSchema": {"type": "object"}},
        ]
    }
    call_result_tool_b = {"content": [{"type": "text", "text": "tool_b_result_from_t2"}], "isError": False}

    def side_effect_t2(req: JsonRpcRequest):
        if req.method == "tools/list":
            return {"jsonrpc": "2.0", "id": req.id, "result": list_result2}
        if req.method == "tools/call":
            if req.params["name"] == "tool_b":
                return {"jsonrpc": "2.0", "id": req.id, "result": call_result_tool_b}
        # This transport should not be called for 'shared_tool' by the client due to first-wins
        raise McpTransportError(f"Unhandled mock request in transport2: {req.method} {req.params.get('name', '')}")

    transport2.send_request.side_effect = side_effect_t2
    return transport2


class DescribeMcpClient:
    def should_be_instantiated_and_discover_tools(self, mock_transport1):
        client = McpClient(transports=[mock_transport1])
        
        mock_transport1.initialize.assert_called_once()
        # tools/list should be called
        mock_transport1.send_request.assert_called_once_with(
            JsonRpcRequest(method="tools/list", params={}, id="mcp_client_tools_list_1")
        )
        assert "tool_a" in client._tool_to_transport_map
        assert "shared_tool" in client._tool_to_transport_map
        assert client._tool_to_transport_map["tool_a"] == mock_transport1

    def should_raise_value_error_if_no_transports_are_provided(self):
        with pytest.raises(ValueError, match="At least one transport must be provided"):
            McpClient(transports=[])

    def should_list_aggregated_tools_respecting_first_wins_for_clashes(self, mock_transport1, mock_transport2):
        client = McpClient(transports=[mock_transport1, mock_transport2])
        
        tools = client.list_tools()
        tool_names = {t["name"] for t in tools}

        assert "tool_a" in tool_names
        assert "tool_b" in tool_names
        assert "shared_tool" in tool_names
        assert len(tools) == 3 # tool_a, tool_b, shared_tool (from T1)

        # Verify 'shared_tool' came from transport1
        shared_tool_desc = next(t for t in tools if t["name"] == "shared_tool")
        assert shared_tool_desc["description"] == "Shared tool from T1"
        assert client._tool_to_transport_map["shared_tool"] == mock_transport1


    def should_get_tool_schema_for_known_tool(self, mock_transport1):
        client = McpClient(transports=[mock_transport1])
        schema_a = client.get_tool_schema("tool_a")
        assert schema_a is not None
        assert schema_a["name"] == "tool_a"
        assert schema_a["description"] == "Tool A from T1"

        assert client.get_tool_schema("nonexistent_tool") is None

    def should_call_tool_on_the_correct_transport(self, mock_transport1, mock_transport2, mocker):
        client = McpClient(transports=[mock_transport1, mock_transport2])

        # Call tool_a (only on transport1)
        result_a = client.call_tool("tool_a", param1="val_a")
        assert result_a["content"][0]["text"] == "tool_a_result_from_t1"
        # Check that mock_transport1.send_request was called for tool_a's "tools/call"
        # The specific call for tool_a
        mock_transport1.send_request.assert_any_call(
            JsonRpcRequest(method="tools/call", params={"name": "tool_a", "arguments": {"param1": "val_a"}}, id=ANY)
        )
        
        # Call tool_b (only on transport2)
        result_b = client.call_tool("tool_b", param2="val_b")
        assert result_b["content"][0]["text"] == "tool_b_result_from_t2"
        mock_transport2.send_request.assert_any_call(
            JsonRpcRequest(method="tools/call", params={"name": "tool_b", "arguments": {"param2": "val_b"}}, id=ANY)
        )

        # Call shared_tool (should go to transport1)
        result_shared = client.call_tool("shared_tool", param_s="val_s")
        assert result_shared["content"][0]["text"] == "shared_tool_result_from_t1"
        mock_transport1.send_request.assert_any_call(
            JsonRpcRequest(method="tools/call", params={"name": "shared_tool", "arguments": {"param_s": "val_s"}}, id=ANY)
        )
        # Ensure transport2 was NOT called for shared_tool's "tools/call"
        # This is harder to assert directly without inspecting all calls to transport2.send_request.
        # The side_effect in mock_transport2 would raise an error if it was called for shared_tool.

    def should_raise_value_error_when_calling_an_unknown_tool(self, mock_transport1):
        client = McpClient(transports=[mock_transport1])
        with pytest.raises(ValueError, match="Tool 'unknown_tool' not found"):
            client.call_tool("unknown_tool", param="value")

    def should_raise_mcp_tool_execution_error_if_tool_result_iserror_true(self, mock_transport1, mocker):
        # Modify mock_transport1 to return isError: True for a specific tool
        erroring_tool_name = "error_maker"
        error_result_payload = {"content": [{"type": "text", "text": "It broke!"}], "isError": True}

        original_side_effect = mock_transport1.send_request.side_effect
        def new_side_effect(req: JsonRpcRequest):
            if req.method == "tools/list": # Augment list response
                list_resp = original_side_effect(JsonRpcRequest(method="tools/list", params={}, id=req.id))
                list_resp["result"]["tools"].append({"name": erroring_tool_name, "description": "Errors", "inputSchema": {}})
                return list_resp
            if req.method == "tools/call" and req.params["name"] == erroring_tool_name:
                return {"jsonrpc": "2.0", "id": req.id, "result": error_result_payload}
            return original_side_effect(req)
        mock_transport1.send_request.side_effect = new_side_effect
        
        client = McpClient(transports=[mock_transport1]) # Re-init to pick up new tool
        
        with pytest.raises(McpToolExecutionError, match="It broke!") as exc_info:
            client.call_tool(erroring_tool_name)
        assert exc_info.value.tool_result_payload == error_result_payload

    def should_shutdown_all_transports_on_client_shutdown(self, mock_transport1, mock_transport2):
        client = McpClient(transports=[mock_transport1, mock_transport2])
        client.shutdown()
        mock_transport1.shutdown.assert_called_once()
        mock_transport2.shutdown.assert_called_once()

    def should_function_as_a_context_manager(self, mock_transport1):
        with McpClient(transports=[mock_transport1]) as client:
            assert client is not None
            mock_transport1.initialize.assert_called_once() # From __init__
        mock_transport1.shutdown.assert_called_once() # From __exit__
        
    def should_handle_transport_errors_gracefully_during_tool_discovery(self, mock_transport1, mocker):
        failing_transport = Mock(spec=McpTransport)
        failing_transport.initialize = Mock()
        failing_transport.send_request.side_effect = McpTransportError("Discovery failed on this one")
        failing_transport.shutdown = Mock()

        # mock_transport1 is the good one
        client = McpClient(transports=[failing_transport, mock_transport1])

        # Check that tools from mock_transport1 are still available
        assert "tool_a" in client._tool_to_transport_map
        assert client.get_tool_schema("tool_a") is not None
        
        # Check that failing_transport was attempted
        failing_transport.initialize.assert_called_once()
        failing_transport.send_request.assert_called_once() # Attempted tools/list
        mock_transport1.initialize.assert_called_once()
        mock_transport1.send_request.assert_called_once() # For its tools/list

        # Ensure client can still call tools from the working transport
        result = client.call_tool("tool_a")
        assert result["content"][0]["text"] == "tool_a_result_from_t1"


class DescribeToolAccessor:
    @pytest.fixture
    def client_for_accessor(self, mock_transport1, mock_transport2):
        # This client will have tool_a, shared_tool (from T1), tool_b (from T2)
        return McpClient(transports=[mock_transport1, mock_transport2])

    def should_allow_calling_discovered_tools_as_methods(self, client_for_accessor):
        # Mock the underlying call_tool to verify it's used correctly
        client_for_accessor.call_tool = Mock(return_value="Dynamic call successful!")

        # Call tool_a
        result_a = client_for_accessor.tools.tool_a(param_x="hello")
        assert result_a == "Dynamic call successful!"
        client_for_accessor.call_tool.assert_called_once_with("tool_a", param_x="hello")
        client_for_accessor.call_tool.reset_mock()

        # Call tool_b
        result_b = client_for_accessor.tools.tool_b(param_y=123)
        assert result_b == "Dynamic call successful!"
        client_for_accessor.call_tool.assert_called_once_with("tool_b", param_y=123)
        client_for_accessor.call_tool.reset_mock()

        # Call shared_tool (should be routed to transport1's version)
        result_shared = client_for_accessor.tools.shared_tool()
        assert result_shared == "Dynamic call successful!"
        client_for_accessor.call_tool.assert_called_once_with("shared_tool")

    def should_raise_attribute_error_for_unknown_tool_name(self, client_for_accessor):
        with pytest.raises(AttributeError, match="'McpClient.tools' has no attribute 'non_existent_tool'"):
            _ = client_for_accessor.tools.non_existent_tool
            
    def should_have_docstring_from_tool_description_on_dynamic_method(self, mock_transport1):
        client = McpClient(transports=[mock_transport1]) # tool_a description is "Tool A from T1"
        
        dynamic_tool_a_method = client.tools.tool_a
        assert dynamic_tool_a_method.__doc__ == "Tool A from T1"

        # Test with a tool that might not have a description in its schema (though unlikely for good tools)
        mock_transport1.send_request.side_effect = lambda req: {
            "jsonrpc": "2.0", "id": req.id, 
            "result": {"tools": [{"name": "no_desc_tool", "inputSchema": {}}]} # No description field
        } if req.method == "tools/list" else None # Simplified for this test
        
        client_no_desc = McpClient(transports=[mock_transport1])
        dynamic_no_desc_method = client_no_desc.tools.no_desc_tool
        assert dynamic_no_desc_method.__doc__ == "Calls the MCP tool 'no_desc_tool'."

