from datetime import datetime, date
import re



DATE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$") #MM-DD-YYYY format


def valid_date(given_date: str):
    if not DATE_PATTERN.match(given_date):
        raise ValueError("This formatting is invalid! Use: MM-DD-YYYY")
    
    try: 
        dt = datetime.strptime(given_date, '%m-%d-%Y').date()
    except ValueError:
        raise ValueError("This is an invalid date")
    
    if dt > date.today():
        raise ValueError("Date cannot be in the future.")
    return True

def valid_closed_date(open_date: date, closed_date: date):
    return closed_date > open_date

def main():
    date1 = "03-26-2000"
    date2 = "05-22-2015"

    print(valid_closed_date(date2,date1)) #Should return True
    x = "1"
    if x:
        print("Hello")
    else:
        print("What")


if __name__ == "__main__":
    main()
