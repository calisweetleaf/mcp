from tools.enhanced_code_analysis_tool import CodeAnalysisTool

tool = CodeAnalysisTool()

print("=== Testing Enhanced Code Analysis Tool ===")

# Test 1: Complete code analysis
print("\n1. Testing Complete Code Analysis:")
result = tool.bb7_analyze_code_complete('test_analysis.py')
print(result)

# Test 2: Secure Python execution
print("\n2. Testing Secure Python Execution:")
test_code = """
x = [1, 2, 3, 4, 5]
y = sum(x)
print(f"Sum: {y}")
result = y * 2
print(f"Result: {result}")
"""
exec_result = tool.bb7_python_execute_secure(test_code)
print(exec_result)

# Test 3: Security audit
print("\n3. Testing Security Audit:")
audit_result = tool.bb7_security_audit('test_analysis.py')
print(audit_result)

# Test 4: Execution audit log
print("\n4. Testing Execution Audit Log:")
audit_log = tool.bb7_get_execution_audit(5)
print(audit_log)

print("\n=== All tests completed ===")
