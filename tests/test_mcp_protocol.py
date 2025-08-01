#!/usr/bin/env python3
"""
Test script to verify MCP JSON-RPC protocol communication
"""

import json
import subprocess
import sys
import time
import threading
import queue

def test_mcp_protocol():
    """Test MCP server JSON-RPC protocol"""
    print("Testing MCP Server JSON-RPC Protocol...")
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        def read_stderr():
            """Read stderr in background to capture server logs"""
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                print(f"SERVER LOG: {line.strip()}", file=sys.stderr)
        
        # Start stderr reader thread
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Test 1: Initialize request
        print("Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send request
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            print(f"Initialize response: {response_line.strip()}")
            try:
                response = json.loads(response_line)
                if response.get("id") == 1 and "result" in response:
                    print("✓ Initialize request successful")
                else:
                    print("✗ Initialize request failed")
                    print(f"Response: {response}")
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON response: {e}")
                print(f"Raw response: {response_line}")
        else:
            print("✗ No response received")
        
        # Test 2: List tools request
        print("\nSending tools/list request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            print(f"Tools list response length: {len(response_line)} chars")
            try:
                response = json.loads(response_line)
                if response.get("id") == 2 and "result" in response:
                    tools = response["result"].get("tools", [])
                    print(f"✓ Tools list successful - {len(tools)} tools available")
                    
                    # Show first few tools
                    for i, tool in enumerate(tools[:5]):
                        print(f"  {i+1}. {tool.get('name', 'unknown')}")
                    if len(tools) > 5:
                        print(f"  ... and {len(tools) - 5} more tools")
                else:
                    print("✗ Tools list failed")
                    print(f"Response: {response}")
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON response: {e}")
                print(f"Raw response: {response_line[:200]}...")
        else:
            print("✗ No response received")
        
        # Test 3: Call a simple tool
        print("\nSending tools/call request...")
        call_request = {
            "jsonrpc": "2.0", 
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "bb7_memory_stats",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(call_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            print(f"Tool call response: {response_line.strip()}")
            try:
                response = json.loads(response_line)
                if response.get("id") == 3 and "result" in response:
                    print("✓ Tool call successful")
                else:
                    print("✗ Tool call failed")
                    print(f"Response: {response}")
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON response: {e}")
                print(f"Raw response: {response_line}")
        else:
            print("✗ No response received")
        
        # Clean shutdown
        print("\nShutting down test...")
        process.terminate()
        process.wait(timeout=5)
        
        print("✓ Protocol test completed")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_protocol()
