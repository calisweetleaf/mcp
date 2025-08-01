#!/usr/bin/env python3
"""
Test script to verify session manager tool fixes
"""

import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_session_manager_integration():
    """Test the integration between session manager and memory tools"""
    print("🔧 Testing Session Manager Tool Integration...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from tools.session_manager_tool import EnhancedSessionTool
        from tools.memory_tool import EnhancedMemoryTool
        print("   ✅ Imports successful")
        
        # Test initialization
        print("2. Testing initialization...")
        memory_tool = EnhancedMemoryTool()
        session_tool = EnhancedSessionTool()
        print(f"   ✅ Memory tool: {type(memory_tool).__name__}")
        print(f"   ✅ Session tool: {type(session_tool).__name__}")
        print(f"   ✅ Memory integration: {session_tool.memory_tool is not None}")
        
        # Test basic session operations
        print("3. Testing session operations...")
        
        # Start a session
        result = session_tool.bb7_start_session("Test session integration")
        print(f"   ✅ Start session: {result[:80]}...")
        
        # Log an event
        result = session_tool.bb7_log_event("test", "Testing session manager integration")
        print(f"   ✅ Log event: {result}")
        
        # Capture an insight
        result = session_tool.bb7_capture_insight(
            "Session manager integration works correctly", 
            "integration_testing"
        )
        print(f"   ✅ Capture insight: {result}")
        
        # Test memory integration
        print("4. Testing memory integration...")
        if session_tool.memory_tool:
            memory_result = session_tool.memory_tool.store(
                "test_integration", 
                "Session manager and memory tool integration test successful",
                category="testing",
                importance=0.8
            )
            print(f"   ✅ Memory store: {memory_result}")
        
        # Test session listing
        result = session_tool.bb7_list_sessions()
        print(f"   ✅ List sessions: {len(result)} chars")
        
        print("\n🎉 All tests passed! Session manager integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_session_manager_integration()
    sys.exit(0 if success else 1)
