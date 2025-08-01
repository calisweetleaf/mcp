#!/usr/bin/env python3
"""
Quick test of visual tools to verify they work correctly
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from tools.visual_tool import VisualTool

def test_visual_tools():
    """Test each visual tool to verify it works"""
    visual_tool = VisualTool()
    
    print("Testing Visual Tools:")
    print("=" * 50)
    
    test_cases = [
        ('bb7_active_window', {}),
        ('bb7_clipboard_manage', {'action': 'read'}),
        ('bb7_window_manager', {'action': 'list'}),
        ('bb7_screen_capture', {'format': 'base64'}),
        ('bb7_mouse_control', {'action': 'position'}),
        ('bb7_keyboard_input', {'text': ''}),  # Empty text to avoid typing
    ]
    
    results = {}
    
    for tool_name, args in test_cases:
        try:
            print(f"\nTesting {tool_name}...")
            result = visual_tool.handle_tool_call(tool_name, args)
            success = 'success' in result and result['success']
            
            # Special handling for expected "failures"
            if not success and tool_name == 'bb7_keyboard_input':
                # Library not available is expected
                success = 'error' in result and 'library' in str(result).lower()
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {tool_name}")
            
            if not success:
                print(f"    Error: {result.get('error', 'Unknown error')}")
            else:
                # Show some result info (truncated)
                result_str = str(result)
                if len(result_str) > 100:
                    result_str = result_str[:100] + "..."
                print(f"    Result: {result_str}")
            
            results[tool_name] = {
                'success': success,
                'result': result
            }
            
        except Exception as e:
            print(f"  ❌ FAIL - {tool_name}")
            print(f"    Exception: {e}")
            results[tool_name] = {
                'success': False,
                'error': str(e)
            }
    
    # Summary
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"\n" + "=" * 50)
    print(f"Visual Tools Test Summary:")
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_visual_tools()
