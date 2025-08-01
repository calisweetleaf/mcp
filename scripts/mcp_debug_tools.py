#!/usr/bin/env python3
"""
MCP Connection Debugging Tools

Diagnose why GitHub Copilot isn't discovering MCP server tools.
Based on the GitHub Copilot MCP integration requirements.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
import logging
from typing import Optional


def test_mcp_server_direct():
    """Test MCP server by sending JSON-RPC requests directly"""
    print("🧪 Testing MCP Server Direct Communication")
    print("=" * 50)
    
    process: Optional[subprocess.Popen] = None
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Check if pipes are available
        if process.stdin is None or process.stdout is None:
            print("❌ Failed to create pipes for subprocess communication")
            return False
        
        # Test initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "debug-client", "version": "1.0.0"}
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        else:
            print("❌ No initialize response received")
            return False
        
        # Test tools/list request
        tools_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Sending tools/list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response_line = process.stdout.readline()
        if tools_response_line:
            tools_response = json.loads(tools_response_line.strip())
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools available")
            
            # Show first few tools
            for i, tool in enumerate(tools[:5]):
                print(f"   {i+1}. {tool.get('name', 'unnamed')} - {tool.get('description', 'no description')[:50]}...")
            
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
                
        else:
            print("❌ No tools/list response received")
            return False
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        
        print("✅ MCP Server communication test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ MCP Server test FAILED: {e}")
        if process:
            try:
                process.terminate()
            except:
                pass
        return False


def check_vscode_mcp_config():
    """Check VS Code MCP configuration"""
    print("\n🔍 Checking VS Code MCP Configuration")
    print("=" * 50)
    
    vscode_dir = Path(".vscode")
    mcp_json = vscode_dir / "mcp.json"
    
    if not vscode_dir.exists():
        print("❌ .vscode directory not found")
        return False
        
    if not mcp_json.exists():
        print("❌ .vscode/mcp.json file not found")
        print("💡 This is REQUIRED for Copilot to discover your MCP server")
        return False
    
    try:
        with open(mcp_json, 'r') as f:
            config = json.load(f)
            
        print("✅ .vscode/mcp.json found")
        
        servers = config.get('servers', {})
        if not servers:
            print("❌ No servers defined in mcp.json")
            return False
            
        print(f"✅ Found {len(servers)} server(s) configured:")
        
        for server_name, server_config in servers.items():
            print(f"   • {server_name}")
            print(f"     Command: {server_config.get('command', 'not specified')}")
            print(f"     Args: {server_config.get('args', [])}")
            print(f"     Transport: {server_config.get('transport', 'not specified')}")
            
            # Check if the command exists
            command = server_config.get('command')
            if command:
                try:
                    subprocess.run([command, '--version'], capture_output=True, timeout=5)
                    print(f"     ✅ Command '{command}' is accessible")
                except:
                    print(f"     ⚠️ Command '{command}' may not be accessible")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in mcp.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading mcp.json: {e}")
        return False


def check_copilot_requirements():
    """Check GitHub Copilot requirements"""
    print("\n🤖 Checking GitHub Copilot Requirements")
    print("=" * 50)
    
    requirements_met = []
    
    # Check VS Code
    try:
        result = subprocess.run(['code', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ VS Code found: {version}")
            requirements_met.append(True)
        else:
            print("❌ VS Code command not found")
            requirements_met.append(False)
    except:
        print("❌ VS Code not accessible via command line")
        requirements_met.append(False)
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print(f"✅ Python: {python_version}")
        requirements_met.append(True)
    except:
        print("❌ Python version check failed")
        requirements_met.append(False)
    
    print("\n📋 Manual Checks Required:")
    print("   □ GitHub Copilot subscription active")
    print("   □ GitHub Copilot extension installed in VS Code")
    print("   □ GitHub Copilot Chat extension installed") 
    print("   □ Agent Mode enabled: Settings → 'chat.agent.enabled' = true")
    print("   □ MCP enabled: Settings → 'chat.mcp.enabled' = true")
    
    return all(requirements_met)


def generate_minimal_test_server():
    """Generate a minimal test MCP server for debugging"""
    print("\n🔧 Generating Minimal Test Server")
    print("=" * 50)
    
    minimal_server = '''#!/usr/bin/env python3
"""
Minimal MCP Server for Testing Copilot Connection
"""

import json
import sys

def handle_request(request):
    method = request.get("method")
    request_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "MinimalTestServer", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A simple test tool to verify MCP connection",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "Test message"
                                }
                            },
                            "required": ["message"]
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name")
        if tool_name == "test_tool":
            args = request.get("params", {}).get("arguments", {})
            message = args.get("message", "Hello from test tool!")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Test tool received: {message}"}]
                }
            }
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -1, "message": f"Unknown method: {method}"}
    }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -1, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
'''
    
    test_server_path = Path("test_mcp_server.py")
    with open(test_server_path, 'w') as f:
        f.write(minimal_server)
    
    print(f"✅ Created minimal test server: {test_server_path}")
    
    # Create corresponding mcp.json
    test_mcp_config = {
        "servers": {
            "TestMCP": {
                "description": "Minimal test MCP server",
                "command": "python",
                "args": ["test_mcp_server.py"],
                "transport": "stdio",
                "workingDirectory": "${workspaceFolder}"
            }
        }
    }
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    test_mcp_json = vscode_dir / "test_mcp.json"
    with open(test_mcp_json, 'w') as f:
        json.dump(test_mcp_config, f, indent=2)
    
    print(f"✅ Created test config: {test_mcp_json}")
    print("\n💡 To test:")
    print("1. Rename test_mcp.json to mcp.json")
    print("2. Restart VS Code")
    print("3. Open Copilot Chat in Agent Mode")
    print("4. Look for TestMCP server with 1 tool")


def comprehensive_diagnosis():
    """Run comprehensive MCP connection diagnosis"""
    print("🩺 COMPREHENSIVE MCP CONNECTION DIAGNOSIS")
    print("=" * 60)
    print(f"Timestamp: {time.ctime()}")
    print()
    
    # Test 1: MCP Server Direct
    server_works = test_mcp_server_direct()
    
    # Test 2: VS Code Config
    config_works = check_vscode_mcp_config()
    
    # Test 3: Copilot Requirements
    copilot_ready = check_copilot_requirements()
    
    # Test 4: Generate minimal test
    generate_minimal_test_server()
    
    # Summary
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 30)
    print(f"MCP Server Communication: {'✅ PASS' if server_works else '❌ FAIL'}")
    print(f"VS Code Configuration: {'✅ PASS' if config_works else '❌ FAIL'}")
    print(f"Copilot Requirements: {'✅ PASS' if copilot_ready else '❌ PARTIAL'}")
    
    if not server_works:
        print("\n🚨 CRITICAL: MCP server is not working properly")
        print("   • Check for Python errors in mcp_server.py")
        print("   • Verify all imports are available")
        print("   • Test with: python mcp_server.py")
    
    if not config_works:
        print("\n🚨 CRITICAL: VS Code MCP configuration missing/invalid")
        print("   • Create .vscode/mcp.json file")
        print("   • Verify JSON syntax is correct")
        print("   • Check file paths and commands")
    
    if server_works and config_works:
        print("\n✅ MCP server appears to be configured correctly!")
        print("   • Try restarting VS Code completely")
        print("   • Ensure Copilot Agent Mode is enabled")
        print("   • Check VS Code Output panel for MCP logs")
        print("   • Look for 🔧 tools icon in Copilot Chat")


if __name__ == "__main__":
    comprehensive_diagnosis()
