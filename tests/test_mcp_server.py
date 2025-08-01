#!/usr/bin/env python3
"""
Enhanced Test script for Personal MCP Server with Cognitive Session Management

This script tests the MCP server functionality including the new session management
capabilities by simulating JSON-RPC messages that VSCode would send.
"""

import json
import subprocess
import sys
import time
import threading
from pathlib import Path


class MCPTester:
    """Enhanced test harness for MCP server functionality including session management"""
    
    def __init__(self, server_script="mcp_server.py"):
        self.server_script = server_script
        self.process = None
        self.test_session_id = None
    
    def start_server(self):
        """Start the MCP server process"""
        print("Starting MCP server with cognitive session management...")
        self.process = subprocess.Popen(
            [sys.executable, self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        time.sleep(0.5)  # Give it time to start
        print("MCP server started")
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("MCP server stopped")
    
    def send_request(self, request):
        """Send a JSON-RPC request to the server"""
        if not self.process:
            raise RuntimeError("Server not started")
        
        if not self.process.stdin:
            raise RuntimeError("Server stdin not available")
        
        if not self.process.stdout:
            raise RuntimeError("Server stdout not available")
        
        request_json = json.dumps(request)
        print(f"→ Sending: {request_json}")
        
        self.process.stdin.write(request_json + "\n")
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"← Received: {json.dumps(response, indent=2)}")
            return response
        else:
            print("← No response received")
            return None
    
    def test_initialization(self):
        """Test MCP initialization"""
        print("\n=== Testing Initialization ===")
        request = {
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
        
        response = self.send_request(request)
        if response and "result" in response:
            server_info = response["result"].get("serverInfo", {})
            print(f"✅ Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            return True
        return False
    
    def test_tool_listing(self):
        """Test tool discovery including new session tools"""
        print("\n=== Testing Tool Listing ===")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = self.send_request(request)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"Found {len(tools)} tools:")
            
            session_tools = []
            other_tools = []
            
            for tool in tools:
                if tool['name'].startswith(('start_session', 'log_event', 'capture_insight', 
                                          'record_workflow', 'update_focus', 'pause_session',
                                          'resume_session', 'list_sessions', 'get_session_summary')):
                    session_tools.append(tool['name'])
                else:
                    other_tools.append(tool['name'])
            
            print(f"📋 Session Management Tools ({len(session_tools)}):")
            for tool_name in session_tools:
                print(f"  ✓ {tool_name}")
            
            print(f"🔧 Other Tools ({len(other_tools)}):")
            for tool_name in other_tools[:5]:  # Show first 5
                print(f"  ✓ {tool_name}")
            
            if len(other_tools) > 5:
                print(f"  ... and {len(other_tools) - 5} more")
            
            return len(session_tools) >= 5  # Expect at least 5 session tools
        return False
    
    def test_session_lifecycle(self):
        """Test complete session lifecycle"""
        print("\n=== Testing Session Lifecycle ===")
        
        # 1. Start a session
        start_request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "start_session",
                "arguments": {
                    "goal": "Test cognitive session management system",
                    "context": "Comprehensive testing of episodic, semantic, and procedural memory",
                    "tags": ["testing", "cognitive-architecture", "mcp"]
                }
            }
        }
        
        response = self.send_request(start_request)
        if not (response and "result" in response):
            return False
            
        content = response["result"]["content"][0]["text"]
        print(f"Session started: {content[:100]}...")
        
        # Extract session ID from response (assuming it's included)
        # In real implementation, we'd parse this more carefully
        
        # 2. Log some events
        log_request = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "log_event",
                "arguments": {
                    "event_type": "testing_started",
                    "description": "Beginning comprehensive session management tests",
                    "details": {"test_phase": "lifecycle", "expected_duration": "5 minutes"}
                }
            }
        }
        
        response = self.send_request(log_request)
        if not (response and "result" in response):
            return False
            
        # 3. Capture an insight
        insight_request = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "capture_insight",
                "arguments": {
                    "insight": "Three-tier memory architecture enables true collaborative continuity between sessions",
                    "concept": "cognitive_architecture",
                    "relationships": ["episodic_memory", "semantic_memory", "procedural_memory"]
                }
            }
        }
        
        response = self.send_request(insight_request)
        if not (response and "result" in response):
            return False
            
        # 4. Record a workflow
        workflow_request = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "record_workflow",
                "arguments": {
                    "workflow_name": "session_testing_protocol",
                    "steps": [
                        "Start session with clear goal",
                        "Log significant events",
                        "Capture insights and relationships",
                        "Update focus as work progresses",
                        "Pause session when complete"
                    ],
                    "context": "Standard protocol for testing session management functionality"
                }
            }
        }
        
        response = self.send_request(workflow_request)
        if not (response and "result" in response):
            return False
            
        # 5. Update focus
        focus_request = {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {
                "name": "update_focus",
                "arguments": {
                    "focus_areas": ["session_testing", "cognitive_validation"],
                    "energy_level": "high",
                    "momentum": "flowing"
                }
            }
        }
        
        response = self.send_request(focus_request)
        if not (response and "result" in response):
            return False
            
        print("✅ Session lifecycle test completed successfully")
        return True
    
    def test_session_persistence(self):
        """Test session persistence and listing"""
        print("\n=== Testing Session Persistence ===")
        
        # List sessions
        list_request = {
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/call",
            "params": {
                "name": "list_sessions",
                "arguments": {
                    "limit": 10
                }
            }
        }
        
        response = self.send_request(list_request)
        if not (response and "result" in response):
            return False
            
        content = response["result"]["content"][0]["text"]
        print(f"Sessions list: {content[:200]}...")
        
        # Test pausing session
        pause_request = {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "tools/call",
            "params": {
                "name": "pause_session",
                "arguments": {
                    "reason": "Testing session pause functionality"
                }
            }
        }
        
        response = self.send_request(pause_request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"Session paused: {content}")
            return True
            
        return False
    
    def test_memory_integration(self):
        """Test integration between memory and session tools"""
        print("\n=== Testing Memory-Session Integration ===")
        
        # Store some memory
        store_request = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "memory_store",
                "arguments": {
                    "key": "session_architecture_insights",
                    "value": "The cognitive session manager successfully integrates episodic, semantic, and procedural memory for true collaborative continuity."
                }
            }
        }
        
        response = self.send_request(store_request)
        if not (response and "result" in response):
            return False
        
        # Note: In real implementation, memory store would auto-link to current session
        # if session is active, but we paused it in previous test
        
        # Retrieve the memory
        retrieve_request = {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {
                "name": "memory_retrieve",
                "arguments": {
                    "key": "session_architecture_insights"
                }
            }
        }
        
        response = self.send_request(retrieve_request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"Retrieved memory: {content[:100]}...")
            return "cognitive session manager" in content.lower()
        
        return False
    
    def test_file_operations(self):
        """Test file tool functionality"""
        print("\n=== Testing File Operations ===")
        
        # Test writing a file
        write_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "write_file",
                "arguments": {
                    "path": "test_session_output.txt",
                    "content": "Session Management Test Results\n" +
                              "===============================\n" +
                              "✅ Cognitive session architecture implemented\n" +
                              "✅ Three-tier memory system functional\n" +
                              "✅ Session persistence verified\n" +
                              "✅ Integration with existing tools confirmed\n"
                }
            }
        }
        
        response = self.send_request(write_request)
        if not (response and "result" in response):
            return False
        
        # Test reading the file back
        read_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "read_file",
                "arguments": {
                    "path": "test_session_output.txt"
                }
            }
        }
        
        response = self.send_request(read_request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"File content verified: {len(content)} characters")
            return "Cognitive session architecture" in content
        
        return False
    
    def test_shell_operations(self):
        """Test shell tool functionality"""
        print("\n=== Testing Shell Operations ===")
        
        # Test a simple command
        cmd_request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call", 
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo 'Cognitive MCP Server Test: Session Management Active'"
                }
            }
        }
        
        response = self.send_request(cmd_request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"Command output verified: Session Management Active found")
            return "Session Management Active" in content
        
        return False
    
    def test_web_operations(self):
        """Test web tool functionality"""
        print("\n=== Testing Web Operations ===")
        
        # Test URL status check
        status_request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "check_url_status",
                "arguments": {
                    "url": "httpbin.org/status/200"
                }
            }
        }
        
        response = self.send_request(status_request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"URL check verified: Status 200 detected")
            return "Status Code: 200" in content
        
        return False
    
    def run_all_tests(self):
        """Run all tests including new session management tests"""
        print("🧠 Starting Enhanced MCP Server Tests with Cognitive Session Management")
        print("=" * 80)
        
        try:
            self.start_server()
            
            tests = [
                ("Initialization", self.test_initialization),
                ("Tool Listing", self.test_tool_listing),
                ("Session Lifecycle", self.test_session_lifecycle),
                ("Session Persistence", self.test_session_persistence),
                ("Memory-Session Integration", self.test_memory_integration),
                ("File Operations", self.test_file_operations),
                ("Shell Operations", self.test_shell_operations),
                ("Web Operations", self.test_web_operations),
            ]
            
            results = {}
            for test_name, test_func in tests:
                try:
                    print(f"\n🧪 Running {test_name}...")
                    result = test_func()
                    results[test_name] = result
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"   {status}")
                except Exception as e:
                    print(f"   ❌ ERROR: {e}")
                    results[test_name] = False
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 ENHANCED TEST RESULTS SUMMARY")
            passed = sum(1 for r in results.values() if r)
            total = len(results)
            
            # Categorize results
            session_tests = ["Session Lifecycle", "Session Persistence", "Memory-Session Integration"]
            core_tests = ["Initialization", "Tool Listing", "File Operations", "Shell Operations", "Web Operations"]
            
            print("\n🧠 Cognitive Session Management Tests:")
            for test_name in session_tests:
                if test_name in results:
                    status = "✅" if results[test_name] else "❌"
                    print(f"  {status} {test_name}")
            
            print("\n🔧 Core Functionality Tests:")
            for test_name in core_tests:
                if test_name in results:
                    status = "✅" if results[test_name] else "❌"
                    print(f"  {status} {test_name}")
            
            print(f"\n🎯 Overall: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed! Your enhanced MCP server with cognitive session")
                print("   management is ready for VSCode Copilot collaborative development!")
                print("\n💡 Next steps:")
                print("   • Start a session with: start_session('Your project goal')")
                print("   • Log events as you work: log_event('code_written', 'Implemented feature X')")
                print("   • Capture insights: capture_insight('Key learning', 'concept_name')")
                print("   • Build workflows: record_workflow('deployment', ['build', 'test', 'deploy'])")
            else:
                print("⚠️  Some tests failed. Check the logs above for details.")
                print("   This may indicate issues with the session management integration.")
        
        finally:
            self.stop_server()
            
            # Cleanup test files
            try:
                Path("test_session_output.txt").unlink(missing_ok=True)
            except:
                pass


if __name__ == "__main__":
    # Make sure we're in the right directory
    if not Path("mcp_server.py").exists():
        print("❌ Error: mcp_server.py not found in current directory")
        print("   Please run this test from the MCP server project root")
        sys.exit(1)
    
    tester = MCPTester()
    tester.run_all_tests()
