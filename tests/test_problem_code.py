from tools.enhanced_code_analysis_tool import CodeAnalysisTool

tool = CodeAnalysisTool()

print("Testing the exact code that failed:")

# The code that failed in the demo
problem_code = '''
# Data analysis example
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = sum(data)
average = total / len(data)
variance = sum((x - average) ** 2 for x in data) / len(data)

print(f"Dataset: {data}")
print(f"Total: {total}")
print(f"Average: {average:.2f}")
print(f"Variance: {variance:.2f}")

# Find min and max
min_val = min(data)
max_val = max(data)
print(f"Range: {min_val} to {max_val}")
'''

result = tool.bb7_python_execute_secure(problem_code)
print(result)
