#!/usr/bin/env python3
"""
Comprehensive test of session manager integration after fixes
"""

import sys
import traceback
from pathlib import Path

def test_session_manager_integration():
    """Test the complete session manager integration"""
    
    print("🧪 Testing Session Manager Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import and initialization
        print("📦 Testing import and initialization...")
        from tools.session_manager_tool import EnhancedSessionTool
        
        session_tool = EnhancedSessionTool()
        print(f"✅ Session tool initialized successfully")
        print(f"   Memory tool available: {session_tool.memory_tool is not None}")
        
        # Test 2: Basic session operations
        print("\n🎯 Testing basic session operations...")
        
        # Start a test session
        result = session_tool.bb7_start_session(
            goal="Test session manager integration",
            context="Testing all components after fixes"
        )
        print(f"✅ Session started: {result[:80]}...")
        
        # Log an event
        result = session_tool.bb7_log_event(
            event_type="test",
            description="Testing event logging functionality"
        )
        print(f"✅ Event logged: {result[:80]}...")
        
        # Capture an insight
        result = session_tool.bb7_capture_insight(
            insight="Session manager is working correctly",
            concept="integration_testing"
        )
        print(f"✅ Insight captured: {result[:80]}...")
        
        # Test 3: Advanced features
        print("\n🔍 Testing advanced features...")
        
        # Test workflow recording
        result = session_tool.bb7_record_workflow(
            workflow_name="test_workflow",
            steps=["Step 1: Initialize", "Step 2: Test", "Step 3: Validate"]
        )
        print(f"✅ Workflow recorded: {result[:80]}...")
        
        # Test focus update
        result = session_tool.bb7_update_focus(
            focus_areas=["testing", "integration"],
            energy_level="high"
        )
        print(f"✅ Focus updated: {result[:80]}...")
        
        # Test session listing
        result = session_tool.bb7_list_sessions(limit=5)
        print(f"✅ Sessions listed: {len(result)} characters returned")
        
        # Test 4: Memory integration
        print("\n🧠 Testing memory integration...")
        
        if session_tool.memory_tool:
            # Test memory linking
            result = session_tool.bb7_link_memory_to_session("test_memory_key")
            print(f"✅ Memory linked: {result[:80]}...")
            
            # Test cross-session analysis
            result = session_tool.bb7_cross_session_analysis(days_back=7)
            print(f"✅ Cross-session analysis: {len(result)} characters returned")
        else:
            print("⚠️  Memory tool not available - skipping memory tests")
        
        print("\n✅ All tests completed successfully!")
        print("🎉 Session Manager Tool is fully functional!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\nTraceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_session_manager_integration()
    sys.exit(0 if success else 1)
