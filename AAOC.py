import re
from datetime import datetime, date

DATE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$") #MM-DD-YYYY format

def main():
    print('Welcome to the Average Age of Credit Calculator!!')
    entries = menu()

    print("\nCollected entries:")

    if not entries:
        print("No entries.")
        return 

    for name, opened in entries:
        print(f' - {name}: {opened:%m-%d-%Y}')

    print("\nAverage Age of Credit:")
    print(calculate_aaoc(entries))

def menu():
    choice = input("Would you like calculate your AAOC? (Yes/No): ").strip().lower()

    if choice.lower() != "yes":
        print("No worries! Have a good day.")
        return []

    print("Please enter credit and date opened.")
    print("Ex: Student Discover, 08-12-2015  (MM-DD-YYYY)")
    print("Once done, enter \"done\".")

    credit = []

    while True:
        try:
            credit_input = input(":").strip()

            if credit_input.lower() == "done":
                break

            parts = [p.strip() for p in credit_input.split(",", 1)]

            if len(parts) != 2:
                print("Invalid format! Use: Name, MM-DD-YYYY")
                continue
        
            name_part, date_part = parts

            if not name_part:
                print("Name cannot be empty!")
                continue

            valid, opened_date = validate_date(date_part)

            if not valid:
                print("Invalid date! Use MM-DD-YYYY and real calendar dates!")
                continue
            
            credit.append((name_part, opened_date))
            print(f"Added: {name_part} - {opened_date:%m-%d-%Y}")
        
        except Exception as e:
            print(f"There is an eror in your input!: {e}")
    return credit

def validate_date(date_str: str):
    given_date = date_str.strip()

    if not DATE_PATTERN.match(given_date):
        return False, None
    
    try:
        dt = datetime.strptime(given_date, "%m-%d-%Y").date()

        if dt > date.today():
            return False, None

        return True, dt
    except ValueError:
        return False, None
    
def calculate_aaoc(credit_list: list):
    if not credit_list:
        return "0.00 years"
    
    today = date.today()
    ages_in_days = [(today - opened).days for name, opened in credit_list]

    avg_days = sum(ages_in_days) / len(ages_in_days)
    avg_years = avg_days / 365.25

    return f"{avg_years:.2f} years or {format_years_months(avg_years)}"

def format_years_months(avg_years: float):
    years = int(avg_years)
    months = round((avg_years - years) * 12)
    if months == 12:
        years += 1
        months = 0

    return f'{years} years and {months} months.'


if __name__ == "__main__":
    main()
