from datetime import datetime

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
    print("\nEnter each credit account's opening date in the format 'Account Name MM/YYYY'")
    print("ex: Discover 09/2024")
    print("Type 'finish' when you are done.\n")

    account_list = []
    
    while True: 
        user_input = input("Enter account info (or 'finish'): ").strip()

        if user_input.lower() == 'finish':
            break

        try:
            name_part, date_part = user_input.rsplit(" ", 1)
            open_date = datetime.strptime(date_part, "%m/%Y")
            account_list.append((name_part, open_date))
        except ValueError:
            print("\nInvalid format. Please use: AccountName MM/YYYY")

    aaCalc(account_list)
    return account_list

def aaCalc(accounts):
    if not accounts:
        print("No accounts provided.")
        return
    today = datetime.now()
    total_months = 0

    for name, date in accounts:
        delta_years = today.year - date.year
        delta_months = today.month - date.month
        months = delta_years * 12 + delta_months
        total_months += months
    
    avg_months = total_months // len(accounts)
    years = avg_months // 12
    months = avg_months % 12

    print(accounts)
    print(f"\nYou entered {len(accounts)} accounts.")
    print(f"Your Average Age of Credit: {years} years and {months} months\n")

if __name__ == "__main__":
    main_menu()