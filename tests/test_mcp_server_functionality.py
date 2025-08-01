# Test MCP Server Functionality

import json
import subprocess
import time

# Function to send a JSON-RPC request to the MCP server

def send_request(method, params=None):
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1
    }
    process = subprocess.Popen(['python', 'c:/mcp/mcp_server.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=json.dumps(request).encode())
    return json.loads(stdout)

# Test the server initialization
response = send_request("initialize")
print("Initialization Response:", response)

# Test listing tools
response = send_request("tools/list")
print("Tools List Response:", response)

# Test starting a session
response = send_request("tools/call", {"name": "start_session", "arguments": {"goal": "Test session", "context": "Testing the MCP server functionality"}})
print("Start Session Response:", response)

# Test logging an event
response = send_request("tools/call", {"name": "log_event", "arguments": {"event_type": "code_written", "description": "Tested MCP server functionality"}})
print("Log Event Response:", response)

# Test capturing an insight
response = send_request("tools/call", {"name": "capture_insight", "arguments": {"insight": "MCP server is functional", "concept": "server functionality", "relationships": []}})
print("Capture Insight Response:", response)

# Test pausing the session
response = send_request("tools/call", {"name": "pause_session", "arguments": {"reason": "Testing complete"}})
print("Pause Session Response:", response)