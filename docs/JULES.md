# JULES - MCP Codebase Context

This document provides essential context for JULES to effectively work on the `mcp` codebase.

## Project Overview: The MCP Server

The `mcp` codebase implements the Model Context Protocol (MCP) server, a comprehensive platform for advanced AI-human collaboration. Its core functionalities include:
- Persistent memory across sessions
- Extensive file operations
- Secure shell and system tools
- Web tools for content fetching and search
- Advanced session management with cognitive tracking
- Visual automation and screen interaction
- Enhanced code analysis (CFA, DFA, type inference)
- Secure Python execution with sandboxing
- Real-time tool registration and management

The main server logic resides in `mcp_server.py`. For a detailed understanding of the MCP server's setup, architecture, and how `mcp_server.py` functions, refer to the `copilot_usage_manual.md` in the `docs` directory. This document is a core reference for the project.

## Current Tasks and Development Focus

Refer to the `TODO.md` file for the current list of tasks and development priorities. This file is actively maintained and should be consulted for what needs to be done.

### Current TODO.md Content:
```
2025-07-31 20:42:57.860 [info] Discovered 73 tools
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_store does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_retrieve does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_list does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_search does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_consolidate does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_categories does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_analyze_entry does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.861 [warning] Tool bb7_memory_intelligent_search does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_memory_get_insights does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_memory_concept_network does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_memory_extract_concepts does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_search_files does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_run_command does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_run_script does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_fetch_url does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_download_file does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_search_web does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_cross_session_analysis does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.862 [warning] Tool bb7_session_recommendations does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_learned_patterns does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_session_intelligence does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_auto_memory_stats does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_screen_capture does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_screen_monitor does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_visual_diff does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_window_manager does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_active_window does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_keyboard_input does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_mouse_control does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.863 [warning] Tool bb7_clipboard_manage does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_status does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_run_command does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_history does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_environment does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_cd does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_terminal_which does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_analyze_project_structure does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.864 [warning] Tool bb7_get_recent_changes does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_workspace_context_loader does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_show_available_capabilities does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_auto_session_resume does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_intelligent_tool_guide does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_analyze_code_complete does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_python_execute_secure does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_security_audit does not have a description. Tools must be accurately described to be called
2025-07-31 20:42:57.865 [warning] Tool bb7_get_execution_audit does not have a description. Tools must be accurately described to be called
```

## Specific Tasks for `tools/` and `mcp_server.py`

### `tools/` Directory
The `tools/` directory contains individual tool modules that are dynamically loaded by the `mcp_server.py`. Each file in this directory should represent a fully functional tool.
**Task:** Ensure each tool in the `tools/` subfolder is fully functional and has accurate descriptions for all its functions. The `TODO.md` indicates that many tools are missing descriptions, which is a critical area for improvement.

### `mcp_server.py`
This is the core of the MCP server. It handles tool registration, execution, and overall server management.
**Task:** Review `mcp_server.py` to ensure robust error handling, efficient tool management, and adherence to the MCP standard. Pay particular attention to the `register_tools` and `call_tool` methods, and the `tool_registry` structure. The `TODO.md` also highlights warnings about missing tool descriptions, which directly relates to the `tool_registry` in `mcp_server.py`.

## Testing
The `tests/` directory contains various test scripts. JULES should use these tests to quickly verify changes and ensure the codebase remains stable and functional.
**Task:** Utilize the tests in the `tests/` subfolder to ensure each file in the `tools/` subfolder is fully functional and that the `mcp_server.py` operates as expected.

## Key Documentation
-   `docs/copilot_usage_manual.md`: This is a core document for understanding the MCP server, its setup, and the internal workings of `mcp_server.py`. JULES should reference this document for in-depth information.
-   `TODO.md`: As mentioned above, this file outlines the current development tasks.

## General Guidelines for JULES
-   **Adhere to existing conventions:** When making changes, follow the existing coding style, structure, and patterns found in the `mcp` codebase.
-   **Prioritize functionality and robustness:** All implemented code should be production-ready, fully functional, and robust, avoiding simulated logic or hardcoded values.
-   **Self-verification:** Use the provided tests to verify your changes.
-   **Update `TODO.md`:** Always update `TODO.md` with new or completed tasks.
