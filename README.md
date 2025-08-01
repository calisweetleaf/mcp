# Personal MCP Server for VSCode Copilot (Local, Sovereign, Minimal)

## Overview

This is a fully-featured, fully local MCP server template for use with VSCode Copilot's agent mode. Provides persistent memory, file and shell access, and is designed for security and simplicity. No cloud dependencies, no data exfiltration.

## Quick Start

### Automated Setup (Recommended)

```powershell
# Complete setup - autostart + global VSCode configuration
.\setup_complete.ps1 -Complete
```

### Manual Setup

1. Install Python 3.8+
2. Set up autostart: `.\start_mcp_server.ps1 -Install`
3. Start server: `.\start_mcp_server.ps1 -Start`
4. Configure VSCode: `.\setup_vscode_mcp.ps1 -Install`
5. Restart VSCode

### Features

- **Cognitive Session Management**: Episodic, semantic, and procedural memory
- **Persistent Memory**: Cross-session context retention
- **File Operations**: Read, write, search files system-wide
- **Shell Access**: Execute commands and scripts
- **Web Capabilities**: Fetch URLs, search, download content
- **Auto-restart**: Survives system reboots
- **Global VSCode Integration**: Available in all workspaces

## Structure

- `mcp_server.py` — main dispatcher/server.
- `tools/` — separate tool files.
- `data/` — persistent storage.
- `tests/` — minimal endpoint tests.

## Security

- Only local access, all endpoints auditable.
- Expose only trusted tools.
- No external APIs or telemetry.
