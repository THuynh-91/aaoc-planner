import datetime

def main_menu():
    # Select an option on which definition to use
    print("""Select an option:

1: Calculate Average Age of Credit
2: Plan a New Credit Card

Selection: """, end="") 

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

def avaiable(string):
    # Checks if Account Name MM/YYYY is accurate
    exit

def aaoc():

    # Finds out the average age of history of account opening dates.
    print("Enter each credit account's opening date in the format 'Account Name MM/YYYY'")
    print("ex: Discover 09/2024")
    print("Type 'finish' when you are done.")

    account_dates = []
    
    while True: 
        user_input = input("Enter account info (or 'finish'): ")

        # Checks if the user has finished his submission
        if user_input == 'finish':

            print("Input complete")
            print(account_dates)

            break

        elif not user_input:
            print("Input cannot be empty. Please try again.")

            continue

        else:
            try:
                parts = user_input.split()
                if len(parts) < 2:
                    raise ValueError("Invalid format: Missing account name or date.")
                
                date_part = parts[-1]
                if '/' not in date_part:
                    raise ValueError("Invalid format: Date must contain '/'.")
                
                datetime.datetime.strptime(date_part, "%m/%Y")

                month_str, year_str = date_part.split('/')
                month = int(month_str)
                year = int(year_str)

                if (year > c_year) or (year == c_year and month > c_month):
                    print(f"Invalid date: {date_part} is in the future. PLease try again.")
                    continue

                print("Successfully added.")
                account_dates.append(user_input)

            except (ValueError, IndexError) as e:
                print(f"Error: {e}. PLease use 'Account Name MM/YYYY' format.")
                continue
            



c_year = datetime.datetime.now().year
c_month = datetime.datetime.now().month

print(c_month == int('04'))



print (c_year, c_month)
aaoc()