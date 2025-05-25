# MCP Compliance TODO List

This document lists the remaining changes needed to make our MCP implementation fully compliant with the specification.

## Completed Items

### 1. `_handle_tools_list` Method
- ✅ Add the `inputSchema` field to each tool in the response (using the "parameters" field from the tool descriptor)
- ✅ Add the `nextCursor` field to the response
- ✅ Implement proper pagination logic for the cursor parameter in `_handle_tools_list`

### 2. `_handle_tools_call` Method
- ✅ Format the response according to the MCP specification
- ✅ Wrap the result in a content array with type information
- ✅ Add the `isError` field to the response
- ✅ Handle errors properly by setting isError to true and providing an error message

### 3. `_handle_ping` Method
- ✅ Implement the ping mechanism for connection health checks
- ✅ Return an empty response as per the ping specification

## Remaining Tasks

### 1. Notifications
- Implement support for the `notifications/tools/list_changed` notification
- Update the `listChanged` field in the initialize method's capabilities response from `false` to `true` when notifications are supported

### 2. Pagination for Other List Methods
- Implement proper pagination logic for the cursor parameter in `_handle_resources_list`
- Implement proper pagination logic for the cursor parameter in `_handle_prompts_list`
- Add the `nextCursor` field to the responses of these methods

### 3. 2025-03-26 Specification Compliance
- Update protocol version in initialize response to "2025-03-26"
- Add support for the "annotations" field in tool definitions
  - Update the tool schema to include optional annotations property
  - Ensure annotations are properly passed through from tool definitions to responses
- Add support for audio content type in tool results
  - Implement handling for audio content with base64-encoded data and mimeType
- Update pagination links in documentation to reference the 2025-03-26 version
- Update resource links in documentation to reference the 2025-03-26 version
- Add appropriate warnings about tool annotations being untrusted unless from trusted servers

## Implementation Priority
1. Update protocol version to 2025-03-26
2. Add support for the "annotations" field in tool definitions
3. Add support for audio content type in tool results
4. Add support for notifications when the tool list changes
5. Implement pagination for resources/list and prompts/list methods
