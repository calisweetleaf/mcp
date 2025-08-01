# Codebase Context for Gemini

This document provides a comprehensive overview of the MCP Server (JSON-RPC2) codebase, outlining its structure, key components, development practices, and operational procedures.

## Project Overview

The MCP Server is a Python-based application that provides services via a JSON-RPC2 interface. It appears to be a backend for an AI agent or a similar system, given the tool-based architecture and session management features.

## Directory Structure

The codebase is organized into the following key directories:

-   `c:/Users/treyr/mcp/`: The root directory of the project.
    -   `.git/`: Contains Git repository data.
    -   `.github/`: Houses GitHub-specific files, likely for CI/CD or issue templates.
    -   `.venv/`: The Python virtual environment for the project.
    -   `.vscode/`: Contains VS Code editor-specific settings.
    -   `data/`: Holds application data, including logs, sessions, and cached information.
    -   `docs/`: Contains project documentation.
    -   `scripts/`: Contains various Python scripts for debugging, testing, and setup.
    -   `tests/`: Contains a comprehensive suite of tests for the application.
    -   `tools/`: Contains the core logic for the tools available to the MCP server.

## Key Components

The MCP Server is built primarily with Python. Key components include:

-   **Main Application**: `mcp_server.py` is the main entry point for the server application.
-   **Core Logic**: The `tools/` directory contains the implementation of various tools that provide the server's functionality. These include file operations, code analysis, memory management, and more.
-   **Testing Framework**: The `tests/` directory indicates a strong emphasis on testing. It contains numerous test files, suggesting the use of a framework like `pytest`.
-   **Dependencies**: The `requirements.txt` file lists the Python dependencies for the project.

## Development & Testing

-   **Environment Setup**: The `venv_setup.sh` script is used to set up the Python virtual environment.
-   **Testing**: The project has a `tests/` directory with many test files. Tests can likely be run using `pytest`. Key test scripts include `test_mcp_server.py` and `comprehensive_tool_validation.py`.
-   **Debugging**: `scripts/mcp_debug_tools.py` provides tools for debugging the application.

## How to Run the Server

1.  **Setup Environment**: Run `bash venv_setup.sh` to create the virtual environment and install dependencies from `requirements.txt`.
2.  **Activate Environment**: Activate the virtual environment (e.g., `source .venv/bin/activate`).
3.  **Start Server**: Run `python mcp_server.py` to start the MCP server.

## File Descriptions

### tools/auto_tool_module.py
This tool provides meta-intelligence for the MCP server ecosystem, helping Copilot understand available capabilities and automatically activating relevant context for seamless collaboration continuity.

### tools/enhanced_code_analysis_tool.py
Enhanced Code Analysis & Secure Python Interpreter Tool. Production-ready implementation with complete CFA, DFA, Type Inference, and hardened Python execution.

### tools/memory_interconnect.py
Memory Interconnection Layer - Creates intelligent links between memory systems. This enhancement layer provides: semantic similarity matching between memories, automatic cross-referencing of related content, context-aware memory retrieval, and intelligence amplification through memory synthesis.

### tools/memory_tool.py
Enhanced Memory Tool - Intelligent persistent memory with semantic connections. Integrates with the Memory Interconnection Engine for advanced capabilities.

### tools/project_context_tool.py
Project Context Tool - Enhanced project understanding for GitHub Copilot. Provides intelligent project analysis and context retrieval specifically designed for optimal LLM consumption, following MCP best practices.

### tools/session_manager_tool.py
Enhanced Session Manager Tool - Auto-memory formation and cross-system intelligence. Integrates with enhanced memory system for automatic insight capture.

### tools/shell_tool.py
Shell Tool - Command execution for MCP Server. This tool provides full shell command execution capabilities, allowing Copilot to run any system command, script, or utility. No restrictions - designed for a dedicated coding environment.

### tools/visual_tool.py
Visual Awareness Tool for MCP Server - Fixed Version. Enables true AI-human partnership through screen awareness and visual interaction. All tools are always available with graceful error handling for missing dependencies.

### tools/vscode_terminal_tool.py
VS Code Terminal Integration Tool - Bridge MCP Server with Active Terminal. This tool provides direct integration with VS Code's terminal session, allowing the MCP server to interact with your actual terminal state, history, and current working context.

### mcp_server.py
MCP Server - Model Context Protocol Server Implementation. Complete implementation with 55+ tools for advanced AI-human collaboration.

### docs/copilot_usage_manual.md
GitHub Copilot & MCP Servers in VSCode: The Power User's Comprehensive Manual. This document provides a comprehensive guide on how to set up and use MCP servers with GitHub Copilot in VSCode.

### tools/file_tool.py
File Tool - System-wide file operations for MCP Server. This tool provides full file system access for reading, writing, and managing files anywhere on the system. No restrictions - designed for a dedicated coding environment where full access is desired.