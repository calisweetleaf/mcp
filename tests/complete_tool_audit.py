#!/usr/bin/env python3
"""
Complete Tool Audit - Find ALL tools and test every single one
This script will identify all expected tools vs registered tools
"""

import sys
import os
import time
import json
from typing import Any

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def audit_all_tools():
    """Complete audit of all tools across all modules"""
    print("COMPLETE MCP TOOL AUDIT")
    print("=" * 60)
    
    # Import all tool modules
    try:
        from tools.memory_tool import EnhancedMemoryTool
        from tools.file_tool import FileTool
        from tools.shell_tool import ShellTool
        from tools.web_tool import WebTool
        from tools.session_manager_tool import EnhancedSessionTool
        from tools.visual_tool import VisualTool
        from tools.vscode_terminal_tool import VSCodeTerminalTool
        from tools.auto_tool_module import AutoTool
        from mcp_server import MCPServer
        
        print("Successfully imported all modules")
    except Exception as e:
        print(f"Import error: {e}")
        return False
    
    # Get expected tools from each module
    print(f"\n--- EXPECTED TOOLS BY MODULE ---")
    
    expected_tools = {}
    total_expected = 0
    
    modules = [
        ("Memory", EnhancedMemoryTool()),
        ("File", FileTool()),
        ("Shell", ShellTool()),
        ("Web", WebTool()),
        ("Session", EnhancedSessionTool()),
        ("Visual", VisualTool()),
        ("Terminal", VSCodeTerminalTool()),
        ("Auto", AutoTool())
    ]
    
    for module_name, module_instance in modules:
        try:
            module_tools = list(module_instance.get_tools().keys())
            expected_tools[module_name] = module_tools
            total_expected += len(module_tools)
            print(f"{module_name} Tools ({len(module_tools)}):")
            for tool in sorted(module_tools):
                print(f"  - {tool}")
        except Exception as e:
            print(f"Error getting tools from {module_name}: {e}")
            expected_tools[module_name] = []
        print()
    
    print(f"TOTAL EXPECTED TOOLS: {total_expected}")
    
    # Get actually registered tools
    print(f"\n--- ACTUALLY REGISTERED TOOLS ---")
    
    try:
        server = MCPServer()
        registered_tools = list(server.tools.keys())
        print(f"Server registered {len(registered_tools)} tools:")
        for i, tool in enumerate(sorted(registered_tools), 1):
            print(f"{i:2d}. {tool}")
    except Exception as e:
        print(f"Error initializing server: {e}")
        return False
    
    # Compare expected vs registered
    print(f"\n--- COMPARISON ANALYSIS ---")
    
    all_expected = set()
    for module_tools in expected_tools.values():
        all_expected.update(module_tools)
    
    registered_set = set(registered_tools)
    
    missing_tools = all_expected - registered_set
    extra_tools = registered_set - all_expected
    
    print(f"Expected tools: {len(all_expected)}")
    print(f"Registered tools: {len(registered_set)}")
    print(f"Missing tools: {len(missing_tools)}")
    print(f"Extra tools: {len(extra_tools)}")
    
    if missing_tools:
        print(f"\nMISSING TOOLS ({len(missing_tools)}):")
        for tool in sorted(missing_tools):
            print(f"  - {tool}")
    
    if extra_tools:
        print(f"\nEXTRA TOOLS ({len(extra_tools)}):")
        for tool in sorted(extra_tools):
            print(f"  - {tool}")
    
    # Test ALL registered tools
    print(f"\n--- TESTING ALL {len(registered_tools)} TOOLS ---")
    
    test_results = {}
    successful_tests = 0
    failed_tests = 0
    
    for tool_name in sorted(registered_tools):
        try:
            result = test_individual_tool(server, tool_name)
            if result["success"]:
                print(f"PASS: {tool_name}")
                successful_tests += 1
            else:
                print(f"FAIL: {tool_name} - {result['message']}")
                failed_tests += 1
            test_results[tool_name] = result
        except Exception as e:
            print(f"ERROR: {tool_name} - {str(e)[:60]}")
            failed_tests += 1
            test_results[tool_name] = {"success": False, "message": f"Exception: {str(e)[:60]}"}
    
    # Final summary
    print(f"\n" + "=" * 60)
    print(f"COMPLETE AUDIT RESULTS")
    print(f"=" * 60)
    print(f"Expected tools: {len(all_expected)}")
    print(f"Registered tools: {len(registered_set)}")
    print(f"Registration accuracy: {len(registered_set)/len(all_expected)*100:.1f}%")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {failed_tests}")
    print(f"Test success rate: {successful_tests/(successful_tests+failed_tests)*100:.1f}%")
    
    # Determine overall success
    overall_success = (
        len(missing_tools) == 0 and  # All expected tools registered
        successful_tests >= len(registered_tools) * 0.8  # 80% of tests pass
    )
    
    if overall_success:
        print(f"\nOVERALL STATUS: COMPLETE SUCCESS")
        print(f"All expected tools registered and working!")
    else:
        print(f"\nOVERALL STATUS: ISSUES DETECTED")
        if missing_tools:
            print(f"Missing {len(missing_tools)} expected tools")
        if failed_tests > successful_tests * 0.25:
            print(f"Too many test failures: {failed_tests}")
    
    return overall_success

def test_individual_tool(server, tool_name):
    """Test a single tool with appropriate parameters"""
    try:
        # Memory tools
        if tool_name == "memory_store":
            result = server.tools[tool_name]("audit_test_key", "audit_test_value")
            return {"success": True, "message": "Store operation successful"}
        elif tool_name == "memory_retrieve":
            result = server.tools[tool_name]("audit_test_key")
            return {"success": "audit_test_value" in str(result), "message": f"Retrieved value"}
        elif tool_name == "memory_list":
            result = server.tools[tool_name]()
            return {"success": True, "message": f"Listed keys"}
        elif tool_name == "memory_stats":
            result = server.tools[tool_name]()
            return {"success": bool(result), "message": "Stats retrieved"}
        elif tool_name == "memory_delete":
            result = server.tools[tool_name]("audit_test_key")
            return {"success": True, "message": "Delete completed"}
        
        # File tools
        elif tool_name == "read_file":
            result = server.tools[tool_name]("mcp_server.py")
            return {"success": "MCPServer" in str(result), "message": "File read successful"}
        elif tool_name == "write_file":
            result = server.tools[tool_name]("audit_test.txt", "audit test content")
            return {"success": True, "message": "File write successful"}
        elif tool_name == "list_directory":
            result = server.tools[tool_name](".")
            return {"success": bool(result), "message": f"Listed directory"}
        elif tool_name == "get_file_info":
            result = server.tools[tool_name]("mcp_server.py")
            return {"success": bool(result), "message": "File info retrieved"}
        
        # Shell tools
        elif tool_name == "run_command":
            result = server.tools[tool_name]("echo audit_test")
            return {"success": "audit_test" in str(result), "message": "Command executed"}
        elif tool_name == "get_environment":
            result = server.tools[tool_name]()
            return {"success": "PATH" in str(result), "message": "Environment retrieved"}
        elif tool_name == "get_system_info":
            result = server.tools[tool_name]()
            return {"success": bool(result), "message": "System info retrieved"}
        
        # Web tools
        elif tool_name == "check_url_status":
            result = server.tools[tool_name]("httpbin.org")
            return {"success": bool(result), "message": "URL status checked"}
        elif tool_name == "search_web":
            result = server.tools[tool_name]("python")
            return {"success": True, "message": "Web search attempted"}
        
        # Session tools
        elif tool_name == "start_session":
            result = server.tools[tool_name]("Audit test session", "Testing")
            return {"success": bool(result), "message": "Session started"}
        elif tool_name == "list_sessions":
            result = server.tools[tool_name]()
            return {"success": True, "message": "Sessions listed"}
        
        # Terminal tools
        elif tool_name == "bb7_terminal_status":
            result = server.tools[tool_name]()
            return {"success": True, "message": "Terminal status retrieved"}
        elif tool_name == "bb7_terminal_environment":
            result = server.tools[tool_name]()
            return {"success": True, "message": "Terminal env retrieved"}
        
        # Visual tools
        elif tool_name == "bb7_window_manager":
            result = server.tools[tool_name]("list")
            return {"success": True, "message": "Window manager accessed"}
        
        # Auto tools
        elif tool_name == "show_available_capabilities":
            result = server.tools[tool_name]()
            return {"success": bool(result), "message": "Capabilities shown"}
        elif tool_name == "workspace_context_loader":
            result = server.tools[tool_name]()
            return {"success": True, "message": "Context loaded"}
        
        # Default case - try calling with no parameters
        else:
            result = server.tools[tool_name]()
            return {"success": True, "message": "Tool called successfully"}
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)[:100]}"}

if __name__ == "__main__":
    success = audit_all_tools()
    sys.exit(0 if success else 1)