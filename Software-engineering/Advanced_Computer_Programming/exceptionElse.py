#1.Modify the program from Task 2.
#2.Use else to print "Successful Execution" if no errors occur.
#3.Use finally to print "Program execution completed."

try:
    num1 = int(input("Enter a first number: "))
    num2 = int(input("Enter a second number: "))
    print(f"{num1} / {num2} = {num1/num2}")
except ZeroDivisionError:
    print(f"num2 {num2} must be greater than zero")
except ValueError:
    print(f" num1 and num2 must be a number")
else:
    print(f"Successful Execution")
finally:
    print("Program execution completed.")

