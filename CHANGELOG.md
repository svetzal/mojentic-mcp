# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2024-05-25

### Changed
- Split dependencies so users can install only what they need:
  - Base package has minimal dependencies
  - `[client]` installs httpx for client functionality
  - `[server]` installs fastapi and uvicorn for server functionality
  - `[dev]` continues to provide development dependencies

## [0.7.0] - 2023-11-27

### Added
- Improved tools/list method with inputSchema field and pagination support
- Enhanced tools/call method with proper content array formatting and error handling
- Implemented ping mechanism for connection health checks

## [0.6.0] - 2023-11-20

### Added
- Comprehensive documentation with tutorials and API reference
- Custom styling for documentation site
- Improved navigation structure in documentation

## [0.5.0] - 2023-11-15

### Added
- HTTP transport to expose the MCP protocol over HTTP
- STDIO transport to expose the MCP protocol over STDIO
- JSON-RPC 2.0 handler to handle standard MCP requests and responses
- Support for core MCP protocol methods:
  - initialize
  - tools/list
  - tools/call
  - resources/list
  - prompts/list
- Integration with mojentic LLM tools
- Example implementations:
  - Simple HTTP server
  - Simple STDIO server
  - Custom tool creation
  - Task management tools

### Changed
- Initial public release

## [0.1.0] - 2023-10-01

### Added
- Initial project structure
- Basic JSON-RPC handler implementation
