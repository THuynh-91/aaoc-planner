from datetime import datetime, date
from utils import valid_date


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
            self.closed_date = closed_date
        
        
        self.name = name
        self.date_opened = valid_date(date_opened)
        self.type = type

    def rename(self, new_name: str):
        if not new_name.strip():
            raise ValueError("Name cannot be blank.")
        
        self.name = new_name.strip()

    def edit_opened_date(self, new_date: date):
        pass


