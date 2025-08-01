#!/usr/bin/env python3
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
