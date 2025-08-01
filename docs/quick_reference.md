# MCP Tools Quick Reference 🚀

> **Since native MCP integration isn't working, use these commands directly**

## ⚡ Super Quick Commands (q.py)

```bash
python q.py s key value        # Store in memory
python q.py g key              # Get from memory  
python q.py r file.txt         # Read file
python q.py w file.txt content # Write file
python q.py run "git status"   # Run command
python q.py ctx                # Load context
python q.py tools              # Show all tools
```

## 🧠 Memory (Most Important!)

```bash
# Store project context
python q.py s project_status "Working on MCP integration"
python q.py s current_issue "Copilot won't auto-detect tools"
python q.py s solution "Using instructions file approach"

# Retrieve later
python q.py g project_status
python q.py ls  # List all stored keys
```

## 📁 Files (Copy-Paste Ready)

```bash
# Read any file
python -c "from tools.file_tool import FileTool; print(FileTool().read_file('README.md'))"

# Write file
python -c "from tools.file_tool import FileTool; print(FileTool().write_file('test.txt', 'Hello World'))"

# List directory
python -c "from tools.file_tool import FileTool; print(FileTool().list_directory('.'))"
```

## 🐚 Shell Commands

```bash
# Run any command
python -c "from tools.shell_tool import ShellTool; print(ShellTool().run_command('dir'))"

# System info
python -c "from tools.shell_tool import ShellTool; print(ShellTool().get_system_info())"
```

## 🚀 Essential Startup Commands

```bash
# 1. Load workspace context first
python q.py ctx

# 2. Check what's in memory
python q.py ls

# 3. Start session for complex work
python q.py start "Today's development goals"
```

## 💡 Pro Tips

- **Always start with**: `python q.py ctx` to understand current project
- **Store everything important**: Use memory to maintain context between Copilot sessions
- **Use sessions**: For complex multi-step work, start a session and log events
- **Quick file access**: `python q.py r filename` is fastest way to read files

## 🎯 Common Workflows

### New Project Analysis
```bash
python q.py ctx                           # Load context
python q.py s project_analysis "$(python q.py ctx)"  # Store analysis
python q.py start "Analyzing new project"  # Start session
```

### Daily Development
```bash
python q.py g project_status              # Check current status
python q.py start "Today's development"   # Start session
# ... do work ...
python q.py log "Completed feature X"     # Log progress
```

### File Operations
```bash
python q.py dir                           # See what's here
python q.py r important_file.py          # Read key files
python q.py s file_analysis "$(python q.py r config.py)"  # Store for later
```

---
**Keep this reference open** - Copy-paste these commands when Copilot suggests using tools!
