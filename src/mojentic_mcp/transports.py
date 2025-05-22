import abc
import json
import threading
from typing import Any, Dict, List, Optional

import structlog

from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError, JsonRpcErrorCode
from mojentic_mcp.gateways import HttpClientGateway, StdioGateway

logger = structlog.get_logger()


class McpTransport(abc.ABC):
    """Abstract base class for MCP transports."""

    @abc.abstractmethod
    def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]:
        """Sends a JSON-RPC request and returns the response.

        Args:
            rpc_request: The JSON-RPC request object.

        Returns:
            The JSON-RPC response as a dictionary.

        Raises:
            McpTransportError: If a transport-level error occurs.
            JsonRpcError: If the server returns a JSON-RPC error.
        """
        pass

    def initialize(self) -> None:
        """Initializes the transport (e.g., connect, start subprocess)."""
        pass

    def shutdown(self) -> None:
        """Shuts down the transport (e.g., disconnect, stop subprocess)."""
        pass

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


class McpTransportError(Exception):
    """Base exception for transport-related errors."""
    pass


class HttpTransport(McpTransport):
    """MCP Transport using HTTP."""

    def __init__(self, url: str = None, host: str = None, port: int = None, path: str = "/jsonrpc", timeout: float = 30.0, http_gateway: Optional[HttpClientGateway] = None):
        """Initialize the HTTP transport.

        Args:
            url (str, optional): The full URL to the JSON-RPC endpoint. If provided, this takes precedence over host, port, and path.
            host (str, optional): The host to connect to. Required if url is not provided.
            port (int, optional): The port to connect to. Required if url is not provided.
            path (str, optional): The path to the JSON-RPC endpoint. Defaults to "/jsonrpc".
            timeout (float, optional): The timeout for HTTP requests in seconds. Defaults to 30.0.
            http_gateway (HttpGateway, optional): The HTTP gateway to use. If not provided, a new one will be created.

        Raises:
            ValueError: If neither url nor both host and port are provided.
        """
        if url:
            self._url = url
        elif host and port:
            self._url = f"http://{host}:{port}{path}"
        else:
            raise ValueError("Either url or both host and port must be provided")

        self._timeout = timeout
        self._http_gateway = http_gateway or HttpClientGateway(timeout=timeout)

    def initialize(self) -> None:
        self._http_gateway.initialize()
        logger.info("HttpTransport initialized", url=self._url)

    def shutdown(self) -> None:
        self._http_gateway.shutdown()
        logger.info("HttpTransport shutdown", url=self._url)

    def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]:
        request_payload = rpc_request.model_dump(exclude_none=True)
        logger.debug("Sending HTTP request", url=self._url, payload=request_payload)
        try:
            response_json = self._http_gateway.post(self._url, request_payload)
            logger.debug("Received HTTP response", response=response_json)

            if "error" in response_json:
                err = response_json["error"]
                raise JsonRpcError(code=err.get("code"), message=err.get("message"), data=err.get("data"))
            return response_json
        except RuntimeError as e:
            logger.error("HTTP gateway error", exc_info=True)
            raise McpTransportError(f"HTTP client not initialized: {e}") from e
        except Exception as e:
            logger.error("HTTP request error", exc_info=True)
            raise McpTransportError(f"HTTP request failed: {e}") from e


class StdioTransport(McpTransport):
    """MCP Transport using STDIO with a subprocess."""

    def __init__(self, command: List[str], stdio_gateway: Optional[StdioGateway] = None):
        """Initialize the STDIO transport.

        Args:
            command (List[str]): The command to run.
            stdio_gateway (StdioGateway, optional): The STDIO gateway to use. If not provided, a new one will be created.
        """
        self._command = command
        self._stdio_gateway = stdio_gateway or StdioGateway()
        self._request_id_counter = 1  # Simple counter for stdio requests if not provided
        self._lock = threading.Lock()  # To ensure one request/response cycle at a time
        self._pid = None

    def initialize(self) -> None:
        try:
            self._pid = self._stdio_gateway.start_process(self._command)
            logger.info("StdioTransport initialized", command=self._command, pid=self._pid)
        except FileNotFoundError:
            logger.error("Stdio command not found", command=self._command)
            raise McpTransportError(f"Command not found: {self._command[0]}")
        except Exception as e:
            logger.error("Failed to start Stdio process", command=self._command, exc_info=True)
            raise McpTransportError(f"Failed to start subprocess for command '{self._command[0]}': {e}") from e

    def shutdown(self) -> None:
        if self._pid:
            logger.info("Shutting down StdioTransport", pid=self._pid)
            try:
                # Send exit request before terminating
                if self._stdio_gateway.is_process_running():
                    try:
                        exit_request = JsonRpcRequest(jsonrpc="2.0", id=self._request_id_counter, method="exit", params={})
                        self._request_id_counter += 1
                        self._stdio_gateway.write_line(json.dumps(exit_request.model_dump(exclude_none=True)))
                    except Exception:
                        logger.warn("Failed to send exit command for stdio process", pid=self._pid, exc_info=True)

                # Terminate the process
                self._stdio_gateway.terminate_process()
            except Exception as e:
                logger.warn("Error during StdioTransport shutdown", pid=self._pid, exc_info=True)

            self._pid = None
        logger.info("StdioTransport shutdown complete")

    def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]:
        if not self._pid or not self._stdio_gateway.is_process_running():
            raise McpTransportError("STDIO process not running or process terminated.")

        with self._lock:
            if rpc_request.id is None:
                rpc_request.id = self._request_id_counter
                self._request_id_counter += 1

            request_payload_str = json.dumps(rpc_request.model_dump(exclude_none=True))
            logger.debug("Sending STDIO request", payload=request_payload_str, pid=self._pid)

            try:
                self._stdio_gateway.write_line(request_payload_str)

                try:
                    response_line = self._stdio_gateway.read_line()
                except EOFError:
                    stderr_output = self._stdio_gateway.get_stderr_output()
                    logger.error("No response from STDIO process", pid=self._pid, stderr=stderr_output)
                    raise McpTransportError(f"No response from STDIO process (PID: {self._pid}) or process terminated.")

                logger.debug("Received STDIO response line", line=response_line, pid=self._pid)
                response_json = json.loads(response_line)

                if "error" in response_json:
                    err = response_json["error"]
                    raise JsonRpcError(code=err.get("code"), message=err.get("message"), data=err.get("data"))

                if rpc_request.id is not None and response_json.get("id") != rpc_request.id:
                    logger.warn("Received STDIO response with mismatched ID",
                                expected_id=rpc_request.id, actual_id=response_json.get("id"), pid=self._pid)

                return response_json

            except ValueError as e:
                logger.error("STDIO process error", pid=self._pid, exc_info=True)
                raise McpTransportError(f"STDIO process error: {e}") from e
            except BrokenPipeError:
                logger.error("Broken pipe with STDIO process. Process likely terminated.", pid=self._pid, exc_info=True)
                stderr_content = self._stdio_gateway.get_stderr_output()
                raise McpTransportError(f"Broken pipe with STDIO process (PID: {self._pid}). Stderr: {stderr_content[:500]}") # Limit stderr length
            except json.JSONDecodeError as e:
                logger.error("Failed to decode JSON response from STDIO", pid=self._pid, exc_info=True, response_line=response_line)
                raise McpTransportError(f"Invalid JSON response from STDIO server: {e}") from e
            except Exception as e:
                logger.error("Error during STDIO communication", pid=self._pid, exc_info=True)
                raise McpTransportError(f"STDIO communication error: {e}") from e
