#1.Modify the program from Task 1.
#2.Add exception handling for invalid inputs (non-numeric values).
#3.Handle both ZeroDivisionError and ValueError.

try:
    num1 = int(input("Enter a first number: "))
    num2 = int(input("Enter a second number: "))
    print(f"{num1} / {num2} = {num1/num2}")
except ZeroDivisionError:
    print(f"num2 {num2} must be greater than zero")
except ValueError:
    print(f" num1 and num2 must be a number")