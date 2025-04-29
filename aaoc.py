def main_menu():
    # Select an option on which definition to use
    print("""Select an option:

1: Calculate Average Age of Credit
2: Plan a New Credit Card

Selection: """, end="") # Added end="" here

    option = input()

    if option == "1":
        print("You chose to calculate AAOC")
        aaoc()

    elif option == "2":
        print("You chose to plan a new credit card")
        # Credit card plan function

    else:
        print("Not an option")
        # Exit

def aaoc():

    # Finds out the average age of history of account opening dates.
    print("Enter each credit account's opening date in the format 'Account Name MM/YYYY'")
    print("ex: Discover 09/2024")
    print("Type 'finish' when you are done.")

    account_dates = []
    
    while True: 
        user_input = input("Enter account info (or 'finish'): ")

        if user_input.lower() == 'finish':
            break

aaoc()