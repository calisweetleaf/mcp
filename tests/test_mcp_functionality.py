# Test MCP Server Functionality

import json
import requests

# Define the server URL
server_url = 'http://localhost:5000'

# Function to send a request to the MCP server
def send_request(method, params=None):
    request_data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params or {},
        'id': 1
    }
    response = requests.post(server_url, json=request_data)
    return response.json()

# Test starting a session
start_session_response = send_request('start_session', {'goal': 'Test cognitive session management'})
print('Start Session Response:', start_session_response)

# Test logging an event
log_event_response = send_request('log_event', {'event_type': 'code_written', 'description': 'Implemented SessionTool class'})
print('Log Event Response:', log_event_response)

# Test capturing an insight
capture_insight_response = send_request('capture_insight', {'insight': 'Three-tier memory enables true cognitive continuity', 'concept': 'cognitive_architecture', 'relationships': ['episodic_memory', 'semantic_memory']})
print('Capture Insight Response:', capture_insight_response)

# Test updating focus
update_focus_response = send_request('update_focus', {'focus_areas': ['session_management', 'cognitive_architecture'], 'energy_level': 'high', 'momentum': 'flowing'})
print('Update Focus Response:', update_focus_response)

# Test pausing session
pause_session_response = send_request('pause_session', {'reason': 'Testing complete'})
print('Pause Session Response:', pause_session_response)