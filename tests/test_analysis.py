def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    result = factorial(5)
    print(f"Factorial of 5 is: {result}")

if __name__ == "__main__":
    main()
