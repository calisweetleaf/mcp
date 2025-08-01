#!/usr/bin/env python3
"""
VS Code MCP Configuration Setup Script

Automatically configures VS Code to use the Personal MCP Server
according to GitHub Copilot MCP integration best practices.
"""

import json
import os
import shutil
import sys
from pathlib import Path


def setup_vscode_mcp():
    """Setup VS Code MCP configuration for GitHub Copilot integration"""
    
    print("🚀 Setting up VS Code MCP Configuration for GitHub Copilot")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent.absolute()
    vscode_dir = project_root / ".vscode"
    mcp_config_file = vscode_dir / "mcp.json"
    
    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(exist_ok=True)
    print(f"📁 Created/verified .vscode directory: {vscode_dir}")
    
    # MCP configuration
    mcp_config = {
        "servers": {
            "PersonalMCP": {
                "description": "Local sovereign MCP server with persistent memory, file operations, shell access, and cognitive session management",
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
                "workingDirectory": "${workspaceFolder}",
                "env": {
                    "PYTHONUNBUFFERED": "1",
                    "MCP_SERVER_LOG_LEVEL": "INFO"
                }
            }
        },
        "inputs": {
            "confirmFullAccess": {
                "type": "confirmDialog", 
                "title": "Full System Access",
                "message": "This MCP server has full file system and shell access. Continue?",
                "default": False
            }
        }
    }
    
    # Write MCP configuration
    with open(mcp_config_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✅ Created MCP configuration: {mcp_config_file}")
    
    # Check if VS Code is installed
    vscode_paths = [
        "code",  # Command line
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",  # macOS
        "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",  # Windows
        "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd"  # Windows x86
    ]
    
    vscode_found = False
    for path in vscode_paths:
        if shutil.which(path) or Path(path).exists():
            vscode_found = True
            print(f"✅ Found VS Code installation: {path}")
            break
    
    if not vscode_found:
        print("⚠️ VS Code not found in common locations")
    
    # Check Python
    try:
        import subprocess
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Python confirmed: {result.stdout.strip()}")
        else:
            print("⚠️ Python version check failed")
    except Exception as e:
        print(f"⚠️ Could not verify Python: {e}")
    
    # Verify MCP server can start
    print("\n🧪 Testing MCP Server...")
    try:
        # Import to verify no syntax errors
        sys.path.insert(0, str(project_root))
        import mcp_server
        print("✅ MCP server imports successfully")
        
        # Check required directories
        data_dir = project_root / "data"
        tools_dir = project_root / "tools"
        
        if not data_dir.exists():
            data_dir.mkdir()
            print(f"📁 Created data directory: {data_dir}")
        
        if not tools_dir.exists():
            print(f"⚠️ Tools directory not found: {tools_dir}")
        else:
            print(f"✅ Tools directory found: {tools_dir}")
            
    except ImportError as e:
        print(f"❌ MCP server import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ MCP server test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 VS Code MCP Setup Complete!")
    print("\nNext Steps:")
    print("1. Open this project in VS Code")
    print("2. Enable GitHub Copilot Agent Mode in VS Code settings")
    print("3. Open Copilot Chat and switch to Agent Mode (@workspace)")
    print("4. Look for 🔧 tools icon to see available MCP tools")
    print("5. Test with: '@workspace What tools do you have available?'")
    print("\nThe MCP server will start automatically when Copilot Agent Mode is activated.")
    
    return True


def verify_copilot_requirements():
    """Verify GitHub Copilot requirements are met"""
    print("\n🔍 Verifying GitHub Copilot Requirements...")
    
    requirements = []
    
    # Check VS Code version (need 1.99+ for Agent Mode)
    try:
        result = subprocess.run(["code", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ VS Code version: {version_line}")
            # Basic version check (would need more sophisticated parsing for exact version)
            requirements.append(True)
        else:
            print("⚠️ Could not determine VS Code version")
            requirements.append(False)
    except:
        print("⚠️ VS Code command line tool not available")
        requirements.append(False)
    
    print("\n📋 Manual Verification Checklist:")
    print("□ GitHub Copilot subscription active")
    print("□ GitHub Copilot extension installed in VS Code") 
    print("□ GitHub Copilot Chat extension installed")
    print("□ Agent Mode enabled in VS Code settings (search: 'chat.agent.enabled')")
    print("□ MCP support enabled (search: 'chat.mcp.enabled')")
    
    return all(requirements)


if __name__ == "__main__":
    success = setup_vscode_mcp()
    if success:
        verify_copilot_requirements()
        sys.exit(0)
    else:
        print("❌ Setup failed")
        sys.exit(1)
