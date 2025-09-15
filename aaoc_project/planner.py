from models import Account
from portfolio import Portfolio
from utils import valid_date, age_format, valid_closed_date
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from copy import deepcopy

class Planner():
    def __init__(self, portfolio: Portfolio):
        if portfolio is None:
            raise ValueError("Portfolio cannot be None")
        if not portfolio.accounts:
            raise ValueError("Cannot create planner with empty portfolio")

        self.original_portfolio = portfolio
        self.working_accounts = self._create_working_copy()
        self.screnarios = []

    def _create_working_copy(self):
        return deepcopy(self.original_portfolio.accounts)
    
    def add_hypothetical_account(self, account: Account):
        if account.name in self.working_accounts:
            raise ValueError(f"Account {account.name} already exists in scenario")
        self.working_accounts[account.name] = account

    def remove_account(self, account_name: str):
        if account_name not in self.working_accounts:
            raise ValueError(f"Account {account_name} does not exist in scenario")
        del self.working_accounts[account_name]

    #HELPER
    def _calculate_aaoc_for_date(self, accounts: dict, target_dt: date):
        filtered_dates = self._filter_accounts_by_date(accounts, target_dt)
        total_days = 0

        for account in filtered_dates.values():
            total_days += account.age_on(target_dt.strftime('%m-%d-%Y'))

        avg_days = total_days / len(filtered_dates) 
        return age_format(avg_days)
    

    #HELPER
    def _filter_accounts_by_date(self, accounts: dict, target_dt: date):
        filtered_accounts = {}

        for name, account in accounts.items():
            if account.date_opened <= target_dt:
                filtered_accounts[name] = account
        if not filtered_accounts:
            raise ValueError("No accounts to be calculated with this date.")
        return filtered_accounts

    def calculate_aaoc_with_new_account(self, new_account_date: str, target_date: str):
        new_acc_dt = valid_date(new_account_date)
        target_dt = valid_date(target_date)
        
        if not valid_closed_date(new_acc_dt, target_dt):
            raise ValueError("New Account must be made before target date")
        else:
            temp_accounts = self.working_accounts.copy()
            temp_accounts["TempAcc"] = Account("Temp1", new_account_date)

        return self._calculate_aaoc_for_date(temp_accounts, target_dt)
                    

    def calculate_future_aaoc(self, target_date: str):
        target_dt = valid_date(target_date)
        return self._calculate_aaoc_for_date(self.working_accounts, target_dt) 
    
    def _calculate_aaoc_decimal(self, accounts, target_dt):
        filtered_dates = self._filter_accounts_by_date(accounts, target_dt)
        total_days = 0

        for account in filtered_dates.values():
            total_days += account.age_on(target_dt.strftime('%m-%d-%Y'))

        avg_days = total_days / len(filtered_dates) 
        return avg_days / 365.25

    def time_to_target_aaoc(self, target_years: int, target_months: int):
        target_decimal = target_years + (target_months / 12)
        iterations = 0
        today = date.today()
        current_aaoc = self._calculate_aaoc_decimal(self.working_accounts, today)
        if current_aaoc >= target_decimal:
            return f"Target AAOC of {target_years} years {target_months} months already achieved"

        temp_date = today
        iterations = 0

        while iterations < 9999:
            current_aaoc = self._calculate_aaoc_decimal(self.working_accounts, temp_date)

            if current_aaoc >= target_decimal:
                total_days = (temp_date - today).days
                wait_years = total_days // 365
                wait_months = (total_days % 365) // 30

                return f"To reach AAOC of {target_years} years {target_months} months, you will need to wait {wait_years} years {wait_months} months or until {temp_date.strftime('%m-%d-%Y')}" 

            iterations += 1
            temp_date += relativedelta(months=1)
        return "Target AAOC not reachable within reasonable timeframe"
        

        