import datetime

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
            break

        elif not user_input:
            print("Input cannot be empty. Please try again.")

            continue

        # Checks if the year is over the current year, or if the month is not yet reached in the current year
        elif((int( user_input[-4:]) > c_year) or 
             ((int( user_input[-7:-5]) > c_month) and  int(user_input[-4:]) == c_year )):
            



c_year = datetime.datetime.now().year
c_month = datetime.datetime.now().month

print(c_month == int('04'))



print (c_year, c_month)
aaoc()