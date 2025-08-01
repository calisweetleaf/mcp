from tools.enhanced_code_analysis_tool import CodeAnalysisTool

tool = CodeAnalysisTool()

print("Testing simple variable scoping:")

# Test with simpler code that should work
simple_code = """
x = 5
y = 10
result = x + y
print("x =", x)
print("y =", y) 
print("result =", result)
"""

result = tool.bb7_python_execute_secure(simple_code)
print(result)
print("-" * 50)

# Test with list operations
list_code = """
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print("Numbers:", numbers)
print("Total:", total)
"""

result = tool.bb7_python_execute_secure(list_code)
print(result)
