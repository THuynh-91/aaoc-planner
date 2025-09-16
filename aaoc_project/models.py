from datetime import datetime, date
from utils import valid_date, valid_closed_date, valid_planning_date


'''
classDiagram
class Account {
  - str name
  - date date_opened
  - bool is_open
  - date closed_date
  - str type

  + rename(new_name: str) void
  + edit_opened_date(new_date: date) void
  + close(on_date: date) void
  + reopen() void
  + age_on(as_of: date) int
}
'''
class Account():

    def __init__(
            self, 
            name: str, 
            date_opened: str, 
            is_open: str = "Yes", 
            closed_date: str | None = None, 
            type: str | None = None
        ):

        if not name.strip(): #Checks if name is empty or blank
            raise ValueError("Name cannot be blank")
        
        if is_open.lower() in ["yes", "y", "true"]:
            self.is_open = True
        elif is_open.lower() in ["no", "n", "false"]:
            self.is_open = False
        else:
            raise ValueError("Invalid input! Use: yes/no y/n true/false") 
        
        if closed_date:
            self.closed_date = valid_date(closed_date)
        else:
            self.closed_date = None
        
        if not self.is_open and self.closed_date is None:
            raise ValueError("If you account is not open, it needs a closed date!")
        
        if self.is_open and self.closed_date is not None:
            raise ValueError("Open accounts cannot have a closed date!")
        
        self.name = name
        self.date_opened = valid_date(date_opened)
        self.type = type

    def rename(self, new_name: str):
        if not new_name.strip():
            raise ValueError("Name cannot be blank.")
        
        self.name = new_name.strip()

    def edit_opened_date(self, new_date: str):
        self.date_opened = valid_date(new_date)
    
    def close(self, on_date: str):
        if not self.is_open:
            raise ValueError("Account is already closed")

        close_date = valid_date(on_date)
        if not valid_closed_date(self.date_opened, close_date):
            raise ValueError("Close date must be after open date")
        
        self.is_open = False
        self.closed_date = close_date
        
    def reopen(self):
        if self.is_open:
            raise ValueError("account is already open")

        self.is_open = True
        self.closed_date = None

    def current_age(self):
        if self.is_open:
            return (date.today() - self.date_opened).days
        else:
            return (self.closed_date - self.date_opened).days

    def age_on(self, as_of: str):
        as_of_date = valid_planning_date(as_of)  # Changed from valid_date
        
        if as_of_date < self.date_opened:
            raise ValueError("as_of date must be after the account opening date")
        
        if self.is_open:
            return (as_of_date - self.date_opened).days
        else:
            if as_of_date <= self.closed_date:
                return (as_of_date - self.date_opened).days
            else:
                return (self.closed_date - self.date_opened).days



