from datetime import datetime, date
from .utils import valid_date, valid_closed_date, valid_planning_date


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

        if name is None or not name.strip(): #Checks if name is empty or blank
            raise ValueError("Name cannot be blank")

        if is_open is None:
            raise ValueError("Invalid input! Use: yes/no y/n true/false")

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

        self.name = name.strip()
        self.date_opened = valid_date(date_opened)

        # A closed account must have closed strictly after it was opened.
        if self.closed_date is not None and not valid_closed_date(self.date_opened, self.closed_date):
            raise ValueError("Closed date must be after the date opened")

        # Normalize type: strip whitespace and treat an empty string as None.
        if type is not None:
            type = type.strip()
            type = type if type else None
        self.type = type

    def __repr__(self):
        return (
            f"Account(name={self.name!r}, "
            f"date_opened={self.date_opened.strftime('%m-%d-%Y')}, "
            f"is_open={self.is_open}, "
            f"closed_date="
            f"{self.closed_date.strftime('%m-%d-%Y') if self.closed_date else None}, "
            f"type={self.type!r})"
        )

    def __str__(self):
        status = "Open" if self.is_open else "Closed"
        type_part = f" [{self.type}]" if self.type else ""
        opened = self.date_opened.strftime('%m-%d-%Y')
        if self.is_open:
            return f"{self.name}{type_part} ({status}, opened {opened})"
        closed = self.closed_date.strftime('%m-%d-%Y')
        return f"{self.name}{type_part} ({status}, opened {opened}, closed {closed})"

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



