import json
from unittest.mock import Mock, patch, MagicMock, ANY

import pytest

from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError
from mojentic_mcp.transports import HttpTransport, StdioTransport, McpTransportError
from mojentic_mcp.gateways import HttpClientGateway, StdioGateway


class DescribeHttpTransport:
    """Tests for the HttpTransport class."""

    @pytest.fixture
    def mock_http_gateway(self, mocker):
        mock_gateway = Mock(spec=HttpClientGateway)
        mock_gateway.post.return_value = {"jsonrpc": "2.0", "id": 1, "result": "success"}
        return mock_gateway

    def should_be_instantiatable_with_url_and_timeout(self):
        transport = HttpTransport(url="http://example.com/mcp", timeout=60.0)

        assert isinstance(transport, HttpTransport)
        assert transport._url == "http://example.com/mcp"
        assert transport._timeout == 60.0
        assert isinstance(transport._http_gateway, HttpClientGateway)

    def should_be_instantiatable_with_host_port_and_path(self):
        transport = HttpTransport(host="example.com", port=8080, path="/custom", timeout=60.0)

        assert isinstance(transport, HttpTransport)
        assert transport._url == "http://example.com:8080/custom"
        assert transport._timeout == 60.0
        assert isinstance(transport._http_gateway, HttpClientGateway)

    def should_be_instantiatable_with_host_and_port_using_default_path(self):
        transport = HttpTransport(host="example.com", port=8080)

        assert isinstance(transport, HttpTransport)
        assert transport._url == "http://example.com:8080/jsonrpc"
        assert transport._timeout == 30.0
        assert isinstance(transport._http_gateway, HttpClientGateway)

    def should_raise_error_if_neither_url_nor_host_port_provided(self):
        with pytest.raises(ValueError, match="Either url or both host and port must be provided"):
            HttpTransport()

    def should_initialize_and_shutdown_http_gateway(self, mock_http_gateway):
        transport = HttpTransport(url="http://example.com/mcp", http_gateway=mock_http_gateway)

        transport.initialize()
        mock_http_gateway.initialize.assert_called_once()

        transport.shutdown()
        mock_http_gateway.shutdown.assert_called_once()

    def should_work_as_context_manager(self, mock_http_gateway):
        with HttpTransport(url="http://example.com/mcp", http_gateway=mock_http_gateway) as transport:
            mock_http_gateway.initialize.assert_called_once()

        mock_http_gateway.shutdown.assert_called_once()

    def should_send_request_and_receive_response(self, mock_http_gateway):
        expected_response = {"jsonrpc": "2.0", "id": 1, "result": "success"}
        mock_http_gateway.post.return_value = expected_response

        transport = HttpTransport(url="http://example.com/mcp", http_gateway=mock_http_gateway)
        transport.initialize()

        request = JsonRpcRequest(id=1, method="test", params={"key": "value"})
        response = transport.send_request(request)

        assert response == expected_response
        mock_http_gateway.post.assert_called_once_with(
            "http://example.com/mcp", 
            {"jsonrpc": "2.0", "id": 1, "method": "test", "params": {"key": "value"}}
        )

    def should_raise_mcp_transport_error_if_client_not_initialized(self, mocker):
        mock_gateway = Mock(spec=HttpClientGateway)
        mock_gateway.post.side_effect = RuntimeError("HTTP client not initialized. Call initialize() first.")

        transport = HttpTransport(url="http://example.com/mcp", http_gateway=mock_gateway)
        request = JsonRpcRequest(id=1, method="test")

        with pytest.raises(McpTransportError, match="HTTP client not initialized"):
            transport.send_request(request)

    def should_raise_json_rpc_error_if_server_returns_rpc_error(self, mock_http_gateway):
        error_response = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}}
        mock_http_gateway.post.return_value = error_response

        transport = HttpTransport(url="http://example.com/mcp", http_gateway=mock_http_gateway)
        transport.initialize()

        request = JsonRpcRequest(id=1, method="unknown")
        with pytest.raises(McpTransportError) as exc_info:
            transport.send_request(request)

        # Check that the error message contains the expected parts
        error_msg = str(exc_info.value)
        assert "Method not found" in error_msg

    def should_raise_mcp_transport_error_on_http_error(self, mock_http_gateway):
        # Configure the mock to raise an exception when post is called
        mock_http_gateway.post.side_effect = Exception("HTTP error: 404 - Not Found")

        transport = HttpTransport(url="http://example.com/mcp", http_gateway=mock_http_gateway)
        transport.initialize()

        request = JsonRpcRequest(id=1, method="test")
        with pytest.raises(McpTransportError, match="HTTP request failed: HTTP error: 404 - Not Found"):
            transport.send_request(request)


class DescribeStdioTransport:
    """Tests for the StdioTransport class."""

    @pytest.fixture
    def mock_stdio_gateway(self, mocker):
        mock_gateway = Mock(spec=StdioGateway)
        mock_gateway.start_process.return_value = 12345  # PID
        mock_gateway.is_process_running.return_value = True
        mock_gateway.read_line.return_value = json.dumps({"jsonrpc": "2.0", "id": 1, "result": "stdio_success"})
        return mock_gateway

    def should_be_instantiated(self):
        transport = StdioTransport(command=["my_server_cmd", "--arg"])
        assert isinstance(transport, StdioTransport)
        assert transport._command == ["my_server_cmd", "--arg"]
        assert isinstance(transport._stdio_gateway, StdioGateway)
        assert transport._pid is None

    def should_initialize_and_shutdown_subprocess_correctly(self, mock_stdio_gateway):
        transport = StdioTransport(command=["my_server"], stdio_gateway=mock_stdio_gateway)

        with transport: # Uses __enter__ and __exit__
            mock_stdio_gateway.start_process.assert_called_once_with(["my_server"])
            assert transport._pid == 12345

        # Shutdown sequence
        mock_stdio_gateway.is_process_running.assert_called()
        mock_stdio_gateway.write_line.assert_called_with(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "exit", "params": {}}))
        mock_stdio_gateway.terminate_process.assert_called_once()
        assert transport._pid is None


    def should_send_request_and_receive_response_via_stdio(self, mock_stdio_gateway):
        expected_response_json = {"jsonrpc": "2.0", "id": 1, "result": "stdio_success"}
        mock_stdio_gateway.read_line.return_value = json.dumps(expected_response_json)

        transport = StdioTransport(command=["my_server"], stdio_gateway=mock_stdio_gateway)
        with transport:
            # Reset the mock to clear any previous calls
            mock_stdio_gateway.write_line.reset_mock()

            request = JsonRpcRequest(id=1, method="test_stdio", params={"key": "val"})
            response = transport.send_request(request)

            assert response == expected_response_json

            # Check that the write_line method was called with the expected payload
            expected_payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "test_stdio", "params": {"key": "val"}})
            mock_stdio_gateway.write_line.assert_called_with(expected_payload)

    def should_raise_mcp_transport_error_if_stdio_command_not_found(self, mocker):
        mock_gateway = Mock(spec=StdioGateway)
        mock_gateway.start_process.side_effect = FileNotFoundError("Command 'nonexistent' not found")

        transport = StdioTransport(command=["nonexistent"], stdio_gateway=mock_gateway)
        with pytest.raises(McpTransportError, match="Command not found: nonexistent"):
            transport.initialize() # or with transport:

    def should_raise_mcp_transport_error_on_broken_pipe_during_send(self, mock_stdio_gateway):
        # Configure the mock to raise BrokenPipeError when write_line is called
        mock_stdio_gateway.write_line.side_effect = BrokenPipeError("Broken pipe")
        mock_stdio_gateway.get_stderr_output.return_value = "Some error output"

        transport = StdioTransport(command=["my_server"], stdio_gateway=mock_stdio_gateway)
        with transport:
            request = JsonRpcRequest(id=1, method="test")
            with pytest.raises(McpTransportError) as exc_info:
                transport.send_request(request)

            # Check that the error message contains the expected parts
            error_msg = str(exc_info.value)
            assert "Broken pipe with STDIO process" in error_msg
            assert "Some error output" in error_msg

    def should_raise_json_rpc_error_if_stdio_server_returns_rpc_error(self, mock_stdio_gateway):
        error_payload = {"code": -32601, "message": "Method Not Found via STDIO"}

        # Configure the mock to return an error response
        mock_stdio_gateway.read_line.return_value = json.dumps({"jsonrpc": "2.0", "id": 1, "error": error_payload})

        transport = StdioTransport(command=["my_server"], stdio_gateway=mock_stdio_gateway)
        with transport:
            request = JsonRpcRequest(id=1, method="unknown")

            # The implementation wraps JsonRpcError in McpTransportError
            with pytest.raises(McpTransportError) as exc_info:
                transport.send_request(request)

            # Check that the error message contains the expected parts
            error_msg = str(exc_info.value)
            assert "Method Not Found via STDIO" in error_msg

    def should_assign_and_use_request_id_if_not_provided(self, mock_stdio_gateway):
        # Configure the mock to return different responses for different calls
        responses = [
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": "success_auto_id"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "result": "success_auto_id"})
        ]
        mock_stdio_gateway.read_line.side_effect = responses

        transport = StdioTransport(command=["my_server"], stdio_gateway=mock_stdio_gateway)
        with transport:
            # Reset the mock to clear any previous calls
            mock_stdio_gateway.write_line.reset_mock()

            # First request, no ID
            request1 = JsonRpcRequest(method="test1")
            response1 = transport.send_request(request1)
            assert response1["id"] == 1 # StdioTransport assigns 1

            # Check that the write_line method was called with the expected payload
            mock_stdio_gateway.write_line.assert_called_with(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "test1"}))

            # Reset the mock again
            mock_stdio_gateway.write_line.reset_mock()

            # Second request, no ID
            request2 = JsonRpcRequest(method="test2")
            response2 = transport.send_request(request2)
            assert response2["id"] == 2 # StdioTransport assigns 2

            # Check that the write_line method was called with the expected payload
            mock_stdio_gateway.write_line.assert_called_with(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "test2"}))

    def should_raise_error_if_process_not_running_on_send(self, mock_stdio_gateway):
        # Configure the mock to report that the process is not running
        mock_stdio_gateway.is_process_running.return_value = False

        transport = StdioTransport(command=["test"], stdio_gateway=mock_stdio_gateway)
        transport._pid = 12345  # Simulate that initialize was called

        request = JsonRpcRequest(id=1, method="test")
        with pytest.raises(McpTransportError, match="STDIO process not running or process terminated."):
            transport.send_request(request)
