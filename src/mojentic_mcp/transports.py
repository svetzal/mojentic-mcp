import abc
import json
import subprocess
import threading
from typing import Any, Dict, List, Optional

import httpx
import structlog

from mojentic_mcp.rpc import JsonRpcRequest, JsonRpcError, JsonRpcErrorCode

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

    def __init__(self, url: str, timeout: float = 30.0):
        self._url = url
        self._timeout = timeout
        self._client: Optional[httpx.Client] = None

    def initialize(self) -> None:
        self._client = httpx.Client(timeout=self._timeout)
        logger.info("HttpTransport initialized", url=self._url)

    def shutdown(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        logger.info("HttpTransport shutdown", url=self._url)

    def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]:
        if not self._client:
            raise McpTransportError("HTTP client not initialized. Call initialize() or use as context manager.")
        
        request_payload = rpc_request.model_dump(exclude_none=True)
        logger.debug("Sending HTTP request", url=self._url, payload=request_payload)
        try:
            response = self._client.post(self._url, json=request_payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            response_json = response.json()
            logger.debug("Received HTTP response", response=response_json)

            if "error" in response_json:
                err = response_json["error"]
                raise JsonRpcError(code=err.get("code"), message=err.get("message"), data=err.get("data"))
            return response_json
        except httpx.HTTPStatusError as e:
            logger.error("HTTP status error", exc_info=True, status_code=e.response.status_code, response_text=e.response.text)
            raise McpTransportError(f"HTTP error: {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error("HTTP request error", exc_info=True)
            raise McpTransportError(f"HTTP request failed: {e}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON response", exc_info=True)
            raise McpTransportError(f"Invalid JSON response from server: {e}") from e


class StdioTransport(McpTransport):
    """MCP Transport using STDIO with a subprocess."""

    def __init__(self, command: List[str]):
        self._command = command
        self._process: Optional[subprocess.Popen] = None
        self._request_id_counter = 1 # Simple counter for stdio requests if not provided
        self._lock = threading.Lock() # To ensure one request/response cycle at a time

    def initialize(self) -> None:
        try:
            self._process = subprocess.Popen(
                self._command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            logger.info("StdioTransport initialized", command=self._command, pid=self._process.pid if self._process else "N/A")
        except FileNotFoundError:
            logger.error("Stdio command not found", command=self._command)
            raise McpTransportError(f"Command not found: {self._command[0]}")
        except Exception as e:
            logger.error("Failed to start Stdio process", command=self._command, exc_info=True)
            raise McpTransportError(f"Failed to start subprocess for command '{self._command[0]}': {e}") from e

    def shutdown(self) -> None:
        if self._process:
            current_pid = self._process.pid
            logger.info("Shutting down StdioTransport", pid=current_pid)
            if self._process.stdin and not self._process.stdin.closed:
                try:
                    exit_request = JsonRpcRequest(jsonrpc="2.0", id=self._request_id_counter, method="exit", params={})
                    self._request_id_counter +=1
                    self._process.stdin.write(json.dumps(exit_request.model_dump(exclude_none=True)) + "\n")
                    self._process.stdin.flush()
                    self._process.stdin.close() # Close stdin to signal no more input
                except Exception:
                    logger.warn("Failed to send exit command or close stdin for stdio process", pid=current_pid, exc_info=True)

            if self._process.poll() is None: # If still running
                self._process.terminate()
                try:
                    self._process.wait(timeout=5) 
                except subprocess.TimeoutExpired:
                    logger.warn("Stdio process did not terminate gracefully, killing.", pid=current_pid)
                    self._process.kill()
            
            if self._process.stderr:
                try:
                    for line in self._process.stderr: # Drain stderr
                        logger.info("StdioTransport stderr on shutdown", pid=current_pid, line=line.strip())
                    self._process.stderr.close()
                except Exception:
                    logger.warn("Error reading stderr on StdioTransport shutdown", pid=current_pid, exc_info=True)
            if self._process.stdout:
                 try:
                    self._process.stdout.close()
                 except Exception:
                    logger.warn("Error closing stdout on StdioTransport shutdown", pid=current_pid, exc_info=True)
            self._process = None
        logger.info("StdioTransport shutdown complete")

    def send_request(self, rpc_request: JsonRpcRequest) -> Dict[str, Any]:
        if not self._process or not self._process.stdin or not self._process.stdout or \
           self._process.stdin.closed or self._process.stdout.closed or self._process.poll() is not None:
            raise McpTransportError("STDIO process not running, pipes unavailable, or process terminated.")

        with self._lock: 
            if rpc_request.id is None: 
                rpc_request.id = self._request_id_counter
                self._request_id_counter += 1

            request_payload_str = json.dumps(rpc_request.model_dump(exclude_none=True))
            logger.debug("Sending STDIO request", payload=request_payload_str, pid=self._process.pid)

            try:
                self._process.stdin.write(request_payload_str + "\n")
                self._process.stdin.flush()

                response_line = self._process.stdout.readline()
                if not response_line:
                    stderr_output = []
                    if self._process.stderr and not self._process.stderr.closed:
                        # Attempt a non-blocking read or use select for robust stderr capture
                        # For PoC, this part is simplified.
                        pass
                    logger.error("No response from STDIO process", pid=self._process.pid, stderr="".join(stderr_output))
                    raise McpTransportError(f"No response from STDIO process (PID: {self._process.pid}) or process terminated.")
                
                logger.debug("Received STDIO response line", line=response_line.strip(), pid=self._process.pid)
                response_json = json.loads(response_line)

                if "error" in response_json:
                    err = response_json["error"]
                    raise JsonRpcError(code=err.get("code"), message=err.get("message"), data=err.get("data"))
                
                if rpc_request.id is not None and response_json.get("id") != rpc_request.id:
                    logger.warn("Received STDIO response with mismatched ID", 
                                expected_id=rpc_request.id, actual_id=response_json.get("id"), pid=self._process.pid)

                return response_json

            except BrokenPipeError:
                logger.error("Broken pipe with STDIO process. Process likely terminated.", pid=self._process.pid if self._process else "N/A", exc_info=True)
                return_code = self._process.poll() if self._process else "N/A"
                stderr_content = ""
                if self._process and self._process.stderr and not self._process.stderr.closed:
                    try:
                        stderr_content = self._process.stderr.read()
                    except Exception:
                        pass # Avoid error during error handling
                raise McpTransportError(f"Broken pipe with STDIO process (PID: {self._process.pid if self._process else 'N/A'}). Return code: {return_code}. Stderr: {stderr_content[:500]}") # Limit stderr length
            except json.JSONDecodeError as e:
                logger.error("Failed to decode JSON response from STDIO", pid=self._process.pid if self._process else "N/A", exc_info=True, response_line=response_line)
                raise McpTransportError(f"Invalid JSON response from STDIO server: {e}") from e
            except Exception as e:
                logger.error("Error during STDIO communication", pid=self._process.pid if self._process else "N/A", exc_info=True)
                raise McpTransportError(f"STDIO communication error: {e}") from e