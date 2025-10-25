#1.Write a program that asks the user to enter their bank balance and the amount they want to withdraw.
#2.If the withdrawal amount exceeds the balance, raise a ValueError with the message "Insufficient funds! Withdrawal denied.".
#3.If the withdrawal amount is negative, raise another ValueError with the message "Withdrawal amount must be positive.".
#4.Handle the exceptions and print appropriate messages.


try:
    balance = float(input("Enter your bank balance: "))
    withdraw = float(input("Enter amount to withdraw: "))
    if withdraw > balance:
        raise ValueError("Insufficient funds! Withdrawal denied.")
    if withdraw < 0:
        raise ValueError("Withdrawal amount must be positive.")
except Exception as e:
    print(e)
else:
    print("successfully withdrawn")
finally:
    print(f"Your current balance is: {balance-withdraw}")