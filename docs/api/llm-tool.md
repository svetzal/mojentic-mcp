# LLMTool API

The `LLMTool` class is the base class for creating custom tools that can be exposed through MCP servers. It provides a standardized interface for defining tool functionality and schema.

## Class: LLMTool

```python
from mojentic.llm.tools.llm_tool import LLMTool

class MyCustomTool(LLMTool):
    # Implementation here
```

`LLMTool` is an abstract base class that should be extended to create custom tools.

### Methods to Implement

#### run

```python
def run(self, **kwargs):
    # Implementation here
```

The `run` method contains the actual functionality of your tool. It should be implemented by subclasses.

**Parameters:**
- `**kwargs`: Parameters passed to the tool, as defined in the descriptor.

**Returns:**
- The result of the tool execution. This should be a value that can be serialized to JSON.

**Example:**
```python
def run(self, name, language="english"):
    greetings = {
        "english": f"Hello, {name}!",
        "spanish": f"¡Hola, {name}!",
        "french": f"Bonjour, {name}!",
        "german": f"Hallo, {name}!"
    }
    return greetings.get(language.lower(), f"Hello, {name}!")
```

#### descriptor

```python
@property
def descriptor(self):
    # Implementation here
```

The `descriptor` property defines the schema of your tool. It should be implemented by subclasses.

**Returns:**
- A dictionary containing the tool schema in the format expected by the MCP protocol.

**Example:**
```python
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
                        "description": "The language for the greeting",
                        "enum": ["english", "spanish", "french", "german"]
                    }
                },
                "required": ["name"]
            }
        }
    }
```

### Descriptor Format

The descriptor should follow this format:

```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Parameter description"
        },
        "param2": {
          "type": "integer",
          "description": "Parameter description",
          "minimum": 1,
          "maximum": 10
        }
      },
      "required": ["param1"]
    }
  }
}
```

- **type**: Should be "function" for MCP tools.
- **function**: Contains the tool definition.
  - **name**: The name of the tool (used by clients to call it).
  - **description**: A human-readable description of what the tool does.
  - **parameters**: A JSON Schema object defining the parameters.
    - **type**: Should be "object" for MCP tools.
    - **properties**: A dictionary of parameter definitions.
      - Each parameter has a name and a schema.
      - Common schema properties: type, description, enum, minimum, maximum.
    - **required**: An array of parameter names that are required.

## Examples

### Basic Tool with No Parameters

```python
class CurrentDateTimeTool(LLMTool):
    def run(self):
        from datetime import datetime
        return datetime.now().isoformat()
    
    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "current_datetime",
                "description": "Get the current date and time.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
```

### Tool with Parameters

```python
class ResolveDateTool(LLMTool):
    def run(self, date_string):
        from dateutil.parser import parse
        try:
            date = parse(date_string)
            return date.isoformat()
        except Exception as e:
            return {"error": f"Failed to parse date: {str(e)}"}
    
    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "resolve_date",
                "description": "Resolve a date string to a specific date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date_string": {
                            "type": "string",
                            "description": "The date string to resolve (e.g., 'next Monday', '2023-01-01')"
                        }
                    },
                    "required": ["date_string"]
                }
            }
        }
```

### Tool with Constructor Parameters

```python
class WeatherForecastTool(LLMTool):
    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__()
    
    def run(self, location, days=1):
        # Implementation here
        pass
    
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
                            "description": "The location to get weather for"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to forecast",
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["location"]
                }
            }
        }
```

## Best Practices

1. **Clear Naming**: Use descriptive names for your tools and parameters.

2. **Comprehensive Descriptions**: Provide clear descriptions for your tools and parameters to help users understand how to use them.

3. **Input Validation**: Validate input parameters in your `run()` method to handle edge cases.

4. **Error Handling**: Use try-except blocks to catch and handle errors gracefully.

5. **Return Serializable Data**: Ensure that your tool returns data that can be serialized to JSON.

6. **Stateless When Possible**: Unless you specifically need shared state, design your tools to be stateless.

7. **Consistent Interface**: If you have multiple related tools, use a consistent interface for similar operations.

## See Also

- [Creating Custom Tools Tutorial](../tutorials/custom-tools.md): Step-by-step guide to creating custom tools.
- [HTTP Server API](http-server.md): Documentation for the HTTP server implementation.
- [STDIO Server API](stdio-server.md): Documentation for the STDIO server implementation.