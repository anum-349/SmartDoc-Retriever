#1.Write a program that asks the user to enter two numbers.
#2.Perform division and display the result.
#3.Use exception handling to catch a ZeroDivisionError and print an appropriate message.

try:
    num1 = int(input("Enter a first number: "))
    num2 = int(input("Enter a second number: "))
    print(f"{num1} / {num2} = {num1/num2}")
except ZeroDivisionError:
    print(f"num2 {num2} must be greater than zero")
