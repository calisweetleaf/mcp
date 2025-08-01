# Personal MCP Server Setup Guide

## 🚀 Quick Start

This guide will get your local MCP server running with VSCode Copilot in minutes.

### Prerequisites

- Python 3.8+ (should be in your PATH as `python`)
- VSCode with GitHub Copilot extensions installed
- VSCode 1.99+ (for Agent Mode support)

### Step 1: Project Structure

Create your project directory with this structure:

```
mcp-server/
├── mcp_server.py              # Main server (from artifacts)
├── .vscode/
│   └── mcp.json              # VSCode configuration (from artifacts)
├── tools/
│   ├── memory_tool.py        # Memory persistence (from artifacts)
│   ├── file_tool.py          # File operations (from artifacts)
│   ├── shell_tool.py         # Shell commands (from artifacts)
│   └── web_tool.py           # Web requests (from artifacts)
├── data/                     # Auto-created for persistent storage
└── tests/
    └── test_mcp_server.py    # Test harness (from artifacts)
```

### Step 2: Test Your Installation

```bash
# Navigate to your project directory
cd mcp-server

# Run the test suite
python tests/test_mcp_server.py
```

You should see output like:
```
🚀 Starting MCP Server Tests
==================================================
🧪 Running Initialization...
   ✅ PASS
🧪 Running Tool Listing...
   ✅ PASS
...
🎉 All tests passed! Your MCP server is ready for VSCode.
```

### Step 3: Configure VSCode

1. **Enable Agent Mode** (if not already enabled):
   - Open VSCode Settings (Ctrl+,)
   - Search for "chat.agent.enabled"
   - Set it to `true`

2. **Enable MCP Support**:
   - Search for "chat.mcp.enabled" 
   - Ensure it's set to `true` (usually default)

3. **Start the MCP Server**:
   - Open your project in VSCode
   - Open `.vscode/mcp.json`
   - You should see a "Start" button at the top - click it
   - Check the Output panel (View → Output) and select "GitHub Copilot" to see logs

### Step 4: Verify Integration

1. **Open Copilot Chat** (Ctrl+Shift+I or click the chat icon)

2. **Switch to Agent Mode**:
   - Look for a dropdown near the chat input
   - Select "Agent" mode

3. **Check Available Tools**:
   - Click the 🔧 (tools) icon in the chat panel
   - You should see "PersonalMCP" server with multiple tools

4. **Test Memory Persistence**:
   ```
   Store "project_status" as "Working on local MCP server implementation"
   ```
   
   Then in a new chat:
   ```
   What's in my memory for "project_status"?
   ```

5. **Test File Operations**:
   ```
   Create a file called test.txt with "Hello from Copilot Agent!"
   ```

6. **Test Shell Access**:
   ```
   Show me my current environment and run "ls -la"
   ```

## 🔧 Advanced Configuration

### Customize Tool Permissions

Edit `mcp_server.py` to modify which tools are exposed or add custom validation.

### Memory Organization

The memory tool supports hierarchical keys:
- `project:myapp:status`
- `learning:python:advanced_concepts`
- `config:vscode:settings`

### Security Notes

⚠️ **This server has full system access by design**:
- Can read/write any file
- Can execute any shell command  
- Can make web requests
- All data stored locally in `data/` folder

This is intentional for a sovereign coding environment, but be aware of the capabilities.

## 🐛 Troubleshooting

### Server Won't Start

1. **Check Python Path**:
   ```bash
   python --version  # Should show Python 3.8+
   which python      # Should show a valid path
   ```

2. **Check File Permissions**:
   ```bash
   ls -la mcp_server.py  # Should be readable
   ```

3. **Check VSCode Output**:
   - View → Output → "GitHub Copilot" 
   - Look for error messages

### Tools Not Appearing

1. **Verify Agent Mode**: Make sure you're in Agent mode, not Ask mode
2. **Restart Server**: In `.vscode/mcp.json`, use the restart button
3. **Check Logs**: Look at `data/mcp_server.log` for errors
4. **Reload VSCode**: Developer: Reload Window (Ctrl+Shift+P)

### Memory Not Persisting

- Check that `data/memory_store.json` is being created
- Verify write permissions in the project directory

### Commands Failing

- The shell tool uses your system's default shell
- Commands run in the project directory by default
- Use full paths for executables if needed

## 💡 Usage Tips

### Memory Best Practices

```
# Store project context
Store "project_context" as "Building a local MCP server for VSCode Copilot. Key files: mcp_server.py (main), tools/ (modules), data/ (persistence)."

# Store code patterns you discover
Store "python_mcp_pattern" as "MCP tools return plain strings, server handles JSON-RPC wrapping"

# Store configuration details
Store "vscode_mcp_config" as "Use stdio transport, python command, PYTHONUNBUFFERED=1"
```

### File Operations

```
# Read configuration files
Read the contents of ~/.bashrc

# Analyze project structure  
List the contents of /home/user/projects recursively

# Edit multiple files
Write a requirements.txt file with the dependencies: requests, flask, pytest
```

### Shell Integration

```
# Development workflow
Run "git status" and show me what files have changed

# System administration
Check disk usage with "df -h" and show me the current processes

# Build and test
Run "python -m pytest tests/" and analyze any failures
```

### Web Research

```
# Documentation lookup
Fetch the Python documentation for urllib.request

# API exploration
Check the status of httpbin.org/json and fetch some sample data

# Research assistance
Search the web for "MCP protocol specification" and summarize the key points
```

## 🎯 Next Steps

Once everything is working:

1. **Customize Tools**: Add your own tools to the `tools/` directory
2. **Expand Memory**: Build rich context about your projects and coding patterns
3. **Create Workflows**: Use Agent Mode for complex, multi-step development tasks
4. **Share Context**: Use memory to maintain context across multiple coding sessions

Your Copilot is now a true co-architect with persistence, full system access, and web research capabilities - all running locally under your control!

## 🔍 Monitoring and Logs

- **Server Logs**: `data/mcp_server.log`
- **VSCode Logs**: Output panel → "GitHub Copilot"
- **Memory Data**: `data/memory_store.json` (human-readable)
- **Web Cache**: `data/web_cache/` (for downloaded resources)

Happy coding with your sovereign AI assistant! 🎉
