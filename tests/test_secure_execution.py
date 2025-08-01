from tools.enhanced_code_analysis_tool import CodeAnalysisTool

tool = CodeAnalysisTool()

print("Testing improved secure Python execution:")

# Test 1: Basic math with sum
test_code1 = """
x = [1, 2, 3, 4, 5]
y = sum(x)
print("Sum:", y)
result = y * 2
print("Result:", result)
"""

result = tool.bb7_python_execute_secure(test_code1)
print("Test 1 Result:")
print(result)
print("-" * 50)

# Test 2: More complex example
test_code2 = """
numbers = list(range(1, 11))
total = sum(numbers)
average = total / len(numbers)
print(f"Numbers: {numbers}")
print(f"Total: {total}")
print(f"Average: {average}")
"""

result = tool.bb7_python_execute_secure(test_code2)
print("Test 2 Result:")
print(result)
print("-" * 50)

# Test 3: Test security - should be blocked
test_code3 = """
import os
os.system("echo hello")
"""

result = tool.bb7_python_execute_secure(test_code3)
print("Test 3 (Security test) Result:")
print(result)
