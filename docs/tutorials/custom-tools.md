# Creating Custom Tools

This tutorial will guide you through creating custom tools for your MCP server using the Mojentic MCP library.

## Prerequisites

- Python 3.11 or higher
- Mojentic MCP library installed (`pip install mojentic-mcp`)
- Basic understanding of Python classes and inheritance

## Basic Custom Tool

Let's create a simple custom tool that returns information about a user:

```python
from mojentic.llm.tools.llm_tool import LLMTool
from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

class AboutTheUser(LLMTool):
    def run(self):
        return {
            "name": "Stacey",
            "favourite_colour": "purple"
        }

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "colour_preferences",
                "description": "Return the user's favourite colour.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        }

# Create a JSON-RPC handler with the custom tool
rpc_handler = JsonRpcHandler(tools=[AboutTheUser()])

# Create an HTTP MCP server with the handler
server = HttpMcpServer(rpc_handler)

# Run the server
server.run()
```

Save this code to a file (e.g., `custom_tool_server.py`) and run it with Python:

```bash
python custom_tool_server.py
```

## Understanding Custom Tools

Let's break down the key components of a custom tool:

1. **Extending LLMTool**: All custom tools should extend the `LLMTool` class from `mojentic.llm.tools.llm_tool`.

2. **Implementing run()**: The `run()` method contains the actual functionality of your tool. It should return a value that can be serialized to JSON.

3. **Implementing descriptor**: The `descriptor` property defines the schema of your tool, including:
   - `name`: The name of the tool (used by clients to call it)
   - `description`: A human-readable description of what the tool does
   - `parameters`: The JSON schema for the tool's parameters

## Tool with Parameters

Let's create a more complex tool that accepts parameters:

```python
class GreetUser(LLMTool):
    def run(self, name, language="english"):
        greetings = {
            "english": f"Hello, {name}!",
            "spanish": f"¡Hola, {name}!",
            "french": f"Bonjour, {name}!",
            "german": f"Hallo, {name}!"
        }
        return greetings.get(language.lower(), f"Hello, {name}!")

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "greet_user",
                "description": "Generate a greeting for the user in the specified language.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the user to greet"
                        },
                        "language": {
                            "type": "string",
                            "description": "The language for the greeting (english, spanish, french, german)",
                            "enum": ["english", "spanish", "french", "german"]
                        }
                    },
                    "required": ["name"]
                }
            }
        }
```

In this example:
- The `run()` method accepts parameters that match the schema defined in the descriptor
- The `parameters` object defines the expected input parameters
- The `required` array specifies which parameters are required

## Tools with Shared State

You can create multiple tools that share state by passing a shared object to each tool's constructor:

```python
from mojentic.llm.tools.ephemeral_task_manager import EphemeralTaskList, AppendTaskTool, PrependTaskTool, \
    InsertTaskAfterTool, StartTaskTool, CompleteTaskTool, ListTasksTool, ClearTasksTool

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

# Create a shared task list
task_list = EphemeralTaskList()

# Create a JSON-RPC handler with multiple tools that share the task list
rpc_handler = JsonRpcHandler(tools=[
    AppendTaskTool(task_list),
    PrependTaskTool(task_list),
    InsertTaskAfterTool(task_list),
    StartTaskTool(task_list),
    CompleteTaskTool(task_list),
    ListTasksTool(task_list),
    ClearTasksTool(task_list),
])

# Create an HTTP MCP server with the handler
server = HttpMcpServer(rpc_handler)

# Run the server
server.run()
```

In this example:
- The `EphemeralTaskList` class provides a shared state for all the tools
- Each tool is initialized with the same `task_list` instance
- The tools can read from and write to the shared state

## Best Practices for Custom Tools

1. **Clear Naming**: Use descriptive names for your tools and parameters.

2. **Comprehensive Descriptions**: Provide clear descriptions for your tools and parameters to help users understand how to use them.

3. **Input Validation**: Validate input parameters in your `run()` method to handle edge cases.

4. **Error Handling**: Use try-except blocks to catch and handle errors gracefully.

5. **Return Serializable Data**: Ensure that your tool returns data that can be serialized to JSON.

6. **Stateless When Possible**: Unless you specifically need shared state, design your tools to be stateless.

7. **Consistent Interface**: If you have multiple related tools, use a consistent interface for similar operations.

## Example: Weather Forecast Tool

Here's a more complete example of a custom tool that fetches weather forecasts:

```python
import requests
from mojentic.llm.tools.llm_tool import LLMTool

class WeatherForecastTool(LLMTool):
    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__()
    
    def run(self, location, days=1):
        try:
            # This is a placeholder - you would use a real weather API
            response = requests.get(
                f"https://api.weatherapi.com/v1/forecast.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "days": days
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and return the forecast data
            forecast = []
            for day in data["forecast"]["forecastday"]:
                forecast.append({
                    "date": day["date"],
                    "max_temp_c": day["day"]["maxtemp_c"],
                    "min_temp_c": day["day"]["mintemp_c"],
                    "condition": day["day"]["condition"]["text"]
                })
            
            return forecast
        
        except requests.RequestException as e:
            return {"error": f"Failed to fetch weather data: {str(e)}"}
    
    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for (city name, postal code, etc.)"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to forecast (1-10)",
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["location"]
                }
            }
        }
```

## Next Steps

- Learn how to create an [HTTP MCP Server](http-server.md) or [STDIO MCP Server](stdio-server.md) to expose your custom tools
- Check out the [Client Usage Tutorial](client-usage.md) to learn how to interact with your tools
- Explore the [API Reference](../api/index.md) for detailed documentation on the LLMTool class and other components