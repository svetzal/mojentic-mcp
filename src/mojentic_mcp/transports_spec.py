\
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock, ANY

import httpx
import pytest

from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError
from mojentic_mcp.transports import HttpTransport, StdioTransport, McpTransportError


class DescribeHttpTransport:
    def it_should_be_instantiated(self):
        transport = HttpTransport(url="http://test.com")
        assert isinstance(transport, HttpTransport)
        assert transport._url == "http://test.com"

    def it_should_send_request_successfully_and_return_json_result(self, mocker):
        mock_httpx_client_instance = MagicMock(spec=httpx.Client)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        expected_result = {"jsonrpc": "2.0", "id": 1, "result": "success"}
        mock_response.json.return_value = expected_result
        
        mock_httpx_client_instance.post.return_value = mock_response
        mocker.patch("httpx.Client", return_value=mock_httpx_client_instance)

        transport = HttpTransport(url="http://test.com")
        with transport: # Initializes client
            request = JsonRpcRequest(jsonrpc="2.0", id=1, method="test_method", params={"data": "value"})
            response = transport.send_request(request)

        assert response == expected_result
        mock_httpx_client_instance.post.assert_called_once_with(
            "http://test.com",
            json={"jsonrpc": "2.0", "id": 1, "method": "test_method", "params": {"data": "value"}}
        )
        mock_response.raise_for_status.assert_called_once()

    def it_should_raise_mcp_transport_error_on_http_status_error(self, mocker):
        mock_httpx_client_instance = MagicMock(spec=httpx.Client)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        # Configure raise_for_status to actually raise the error
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=Mock(spec=httpx.Request), response=mock_response
        )
        mock_httpx_client_instance.post.return_value = mock_response
        mocker.patch("httpx.Client", return_value=mock_httpx_client_instance)
        
        transport = HttpTransport(url="http://test.com")
        with transport:
            request = JsonRpcRequest(id=1, method="test")
            with pytest.raises(McpTransportError, match="HTTP error: 500 - Internal Server Error"):
                transport.send_request(request)

    def it_should_raise_mcp_transport_error_on_httpx_request_error(self, mocker):
        mock_httpx_client_instance = MagicMock(spec=httpx.Client)
        mock_httpx_client_instance.post.side_effect = httpx.RequestError("Connection refused", request=Mock(spec=httpx.Request))
        mocker.patch("httpx.Client", return_value=mock_httpx_client_instance)

        transport = HttpTransport(url="http://test.com")
        with transport:
            request = JsonRpcRequest(id=1, method="test")
            with pytest.raises(McpTransportError, match="HTTP request failed: Connection refused"):
                transport.send_request(request)
    
    def it_should_raise_json_rpc_error_if_server_response_contains_error_field(self, mocker):
        mock_httpx_client_instance = MagicMock(spec=httpx.Client)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200 # HTTP success, but RPC error
        error_payload = {"code": -32600, "message": "Invalid Request", "data": "details"}
        mock_response.json.return_value = {"jsonrpc": "2.0", "id": 1, "error": error_payload}
        mock_httpx_client_instance.post.return_value = mock_response
        mocker.patch("httpx.Client", return_value=mock_httpx_client_instance)

        transport = HttpTransport(url="http://test.com")
        with transport:
            request = JsonRpcRequest(id=1, method="test")
            with pytest.raises(JsonRpcError) as exc_info:
                transport.send_request(request)
            assert exc_info.value.code == -32600
            assert exc_info.value.message == "Invalid Request"
            assert exc_info.value.data == "details"

    def it_should_raise_mcp_transport_error_if_send_request_called_before_initialization(self):
        transport = HttpTransport(url="http://test.com") # Not using 'with' or calling initialize()
        request = JsonRpcRequest(id=1, method="test")
        with pytest.raises(McpTransportError, match="HTTP client not initialized"):
            transport.send_request(request)

    def it_should_close_client_on_shutdown(self, mocker):
        mock_httpx_client_instance = MagicMock(spec=httpx.Client)
        mocker.patch("httpx.Client", return_value=mock_httpx_client_instance)

        transport = HttpTransport(url="http://test.com")
        transport.initialize() # Manually initialize
        assert transport._client is not None
        transport.shutdown()
        mock_httpx_client_instance.close.assert_called_once()
        assert transport._client is None


class DescribeStdioTransport:
    @pytest.fixture
    def mock_popen_instance(self, mocker):
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.pid = 12345
        mock_proc.stdin = MagicMock()
        mock_proc.stdout = MagicMock()
        mock_proc.stderr = MagicMock()
        mock_proc.poll.return_value = None # Simulate running process
        return mock_proc

    @pytest.fixture
    def mock_popen_class(self, mocker, mock_popen_instance):
        return mocker.patch("subprocess.Popen", return_value=mock_popen_instance)

    def it_should_be_instantiated(self):
        transport = StdioTransport(command=["my_server_cmd", "--arg"])
        assert isinstance(transport, StdioTransport)
        assert transport._command == ["my_server_cmd", "--arg"]

    def it_should_initialize_and_shutdown_subprocess_correctly(self, mock_popen_class, mock_popen_instance):
        transport = StdioTransport(command=["my_server"])
        
        with transport: # Uses __enter__ and __exit__
            mock_popen_class.assert_called_once_with(
                ["my_server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            assert transport._process == mock_popen_instance

        # Shutdown sequence
        mock_popen_instance.stdin.write.assert_any_call(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "exit", "params": {}}) + \'\'\'\\n\'\'\')
        mock_popen_instance.stdin.flush.assert_called()
        mock_popen_instance.stdin.close.assert_called_once()
        mock_popen_instance.terminate.assert_called_once()
        mock_popen_instance.wait.assert_called_once_with(timeout=5)
        # mock_popen_instance.stderr.close.assert_called_once() # Assuming stderr is drained and closed
        # mock_popen_instance.stdout.close.assert_called_once()


    def it_should_send_request_and_receive_response_via_stdio(self, mock_popen_class, mock_popen_instance):
        expected_response_json = {"jsonrpc": "2.0", "id": 1, "result": "stdio_success"}
        mock_popen_instance.stdout.readline.return_value = json.dumps(expected_response_json) + \'\'\'\\n\'\'\'
        
        transport = StdioTransport(command=["my_server"])
        with transport:
            request = JsonRpcRequest(id=1, method="test_stdio", params={"key": "val"})
            response = transport.send_request(request)

        assert response == expected_response_json
        expected_payload_str = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "test_stdio", "params": {"key": "val"}})
        # Check that the write call contains the expected payload string
        # This is a bit fragile if other writes happen to stdin, but for this test it's okay.
        written_data = "".join(c[0][0] for c in mock_popen_instance.stdin.write.call_args_list if json.dumps({"jsonrpc": "2.0", "id": 1, "method": "test_stdio"}) in c[0][0])
        assert expected_payload_str in written_data

        mock_popen_instance.stdin.flush.assert_called()

    def it_should_raise_mcp_transport_error_if_stdio_command_not_found(self, mocker):
        mocker.patch("subprocess.Popen", side_effect=FileNotFoundError("Command 'nonexistent' not found"))
        transport = StdioTransport(command=["nonexistent"])
        with pytest.raises(McpTransportError, match="Command not found: nonexistent"):
            transport.initialize() # or with transport:
            
    def it_should_raise_mcp_transport_error_on_broken_pipe_during_send(self, mock_popen_class, mock_popen_instance):
        mock_popen_instance.stdin.write.side_effect = BrokenPipeError
        mock_popen_instance.poll.return_value = 1 # Process terminated
        mock_popen_instance.stderr.read.return_value = "Process crashed"


        transport = StdioTransport(command=["my_server"])
        with transport:
            request = JsonRpcRequest(id=1, method="test")
            with pytest.raises(McpTransportError, match="Broken pipe with STDIO process .* Return code: 1. Stderr: Process crashed"):
                transport.send_request(request)

    def it_should_raise_json_rpc_error_if_stdio_server_returns_rpc_error(self, mock_popen_class, mock_popen_instance):
        error_payload = {"code": -32601, "message": "Method Not Found via STDIO"}
        mock_popen_instance.stdout.readline.return_value = json.dumps({"jsonrpc": "2.0", "id": 1, "error": error_payload}) + \'\'\'\\n\'\'\'

        transport = StdioTransport(command=["my_server"])
        with transport:
            request = JsonRpcRequest(id=1, method="unknown")
            with pytest.raises(JsonRpcError) as exc_info:
                transport.send_request(request)
            assert exc_info.value.code == -32601
            assert exc_info.value.message == "Method Not Found via STDIO"
            
    def it_should_assign_and_use_request_id_if_not_provided(self, mock_popen_class, mock_popen_instance):
        # Server echos back the ID it receives
        mock_popen_instance.stdout.readline.side_effect = lambda: json.dumps({"jsonrpc": "2.0", "id": transport._request_id_counter -1, "result": "success_auto_id"}) + \'\'\'\\n\'\'\'
        
        transport = StdioTransport(command=["my_server"])
        with transport:
            # First request, no ID
            request1 = JsonRpcRequest(method="test1")
            response1 = transport.send_request(request1)
            assert response1["id"] == 1 # StdioTransport assigns 1
            
            # Check that the written payload contained id:1
            written_payload1_str = mock_popen_instance.stdin.write.call_args_list[-2][0][0] # Second to last due to exit
            assert \'\'\'"id": 1\'\'\' in written_payload1_str
            assert \'\'\'"method": "test1"\'\'\' in written_payload1_str


            # Second request, no ID
            request2 = JsonRpcRequest(method="test2")
            response2 = transport.send_request(request2)
            assert response2["id"] == 2 # StdioTransport assigns 2
            
            written_payload2_str = mock_popen_instance.stdin.write.call_args_list[-1][0][0] # Last call before exit
            assert \'\'\'"id": 2\'\'\' in written_payload2_str
            assert \'\'\'"method": "test2"\'\'\' in written_payload2_str

    def it_should_raise_error_if_process_not_running_on_send(self, mock_popen_class, mock_popen_instance):
        transport = StdioTransport(command=["test"])
        # transport.initialize() # Process starts here
        # Simulate process terminating unexpectedly *after* initialize but *before* send
        mock_popen_instance.poll.return_value = 1 # Process terminated
        
        # Need to initialize to set up self._process
        transport._process = mock_popen_instance # Manually set it up for this test case after it's "terminated"

        request = JsonRpcRequest(id=1, method="test")
        with pytest.raises(McpTransportError, match="STDIO process not running, pipes unavailable, or process terminated."):
            transport.send_request(request)
