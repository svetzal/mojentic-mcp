import json
from typing import Any, Dict, List, Optional

import httpx
import structlog
import sys
import subprocess

logger = structlog.get_logger()


class HttpClientGateway:
    """A thin gateway for HTTP operations using httpx."""
    
    def __init__(self, timeout: float = 30.0):
        """Initialize the HTTP gateway.
        
        Args:
            timeout (float, optional): The timeout for HTTP requests in seconds. Defaults to 30.0.
        """
        self._timeout = timeout
        self._client: Optional[httpx.Client] = None
    
    def initialize(self) -> None:
        """Initialize the HTTP client."""
        self._client = httpx.Client(timeout=self._timeout)
    
    def shutdown(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def post(self, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request with JSON data.
        
        Args:
            url (str): The URL to send the request to.
            json_data (Dict[str, Any]): The JSON data to send.
            
        Returns:
            Dict[str, Any]: The JSON response.
            
        Raises:
            httpx.HTTPStatusError: If the HTTP request returns a 4xx or 5xx status code.
            httpx.RequestError: If the HTTP request fails.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        if not self._client:
            raise RuntimeError("HTTP client not initialized. Call initialize() first.")
        
        response = self._client.post(url, json=json_data)
        response.raise_for_status()
        return response.json()


class StdioGateway:
    """A thin gateway for STDIO operations using subprocess."""
    
    def __init__(self):
        """Initialize the STDIO gateway."""
        self._process: Optional[subprocess.Popen] = None
    
    def start_process(self, command: List[str]) -> int:
        """Start a subprocess with STDIO pipes.
        
        Args:
            command (List[str]): The command to run.
            
        Returns:
            int: The process ID.
            
        Raises:
            FileNotFoundError: If the command is not found.
            subprocess.SubprocessError: If the subprocess fails to start.
        """
        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return self._process.pid
    
    def is_process_running(self) -> bool:
        """Check if the process is running.
        
        Returns:
            bool: True if the process is running, False otherwise.
        """
        if not self._process:
            return False
        return self._process.poll() is None
    
    def write_line(self, line: str) -> None:
        """Write a line to the process's stdin.
        
        Args:
            line (str): The line to write.
            
        Raises:
            BrokenPipeError: If the pipe is broken.
            ValueError: If the process is not running.
        """
        if not self._process or not self._process.stdin or self._process.stdin.closed:
            raise ValueError("Process not running or stdin not available.")
        
        self._process.stdin.write(line + "\n")
        self._process.stdin.flush()
    
    def read_line(self) -> str:
        """Read a line from the process's stdout.
        
        Returns:
            str: The line read.
            
        Raises:
            ValueError: If the process is not running.
        """
        if not self._process or not self._process.stdout or self._process.stdout.closed:
            raise ValueError("Process not running or stdout not available.")
        
        line = self._process.stdout.readline()
        if not line:
            raise EOFError("No more output from process.")
        
        return line.strip()
    
    def terminate_process(self) -> None:
        """Terminate the process."""
        if not self._process:
            return
        
        # Close stdin if it's open
        if self._process.stdin and not self._process.stdin.closed:
            try:
                self._process.stdin.close()
            except Exception:
                pass
        
        # Terminate the process if it's still running
        if self.is_process_running():
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        
        # Close stdout and stderr if they're open
        if self._process.stdout and not self._process.stdout.closed:
            try:
                self._process.stdout.close()
            except Exception:
                pass
        
        if self._process.stderr and not self._process.stderr.closed:
            try:
                self._process.stderr.close()
            except Exception:
                pass
        
        self._process = None
    
    def get_stderr_output(self) -> str:
        """Get any available stderr output.
        
        Returns:
            str: The stderr output.
        """
        if not self._process or not self._process.stderr or self._process.stderr.closed:
            return ""
        
        try:
            return self._process.stderr.read()
        except Exception:
            return ""