try:
    salary = int(input("Enter salary:"))
    tax = salary * 0.10
    print("Tax Calculated:", tax)
except ValueError:
    print("Error: kirpya sirf number dale")
finally:
    print("Execution Complete.")