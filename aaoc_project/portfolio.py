from models import Account
from utils import valid_date, valid_closed_date, age_format

class Portfolio():
    def __init__(self, name = str):
        if not name.strip():
            raise ValueError("Name cannot be blank")
        
        self.name = name.strip()
        self.accounts = {}

    def add_account(self, account: Account):
        if account.name in self.accounts:
            raise ValueError(f"Account '{account.name}' already exists in portfolio.")
        self.accounts[account.name] = account

    def remove_account(self, account_name: str):
        if account_name not in self.accounts:
            raise ValueError(f"Account '{account_name}' does not exist in portfolio.")
        del self.accounts[account_name]

        return f'{account_name} is removed from: {self.name}.'
    
    def get_account(self, account_name: str):
        if account_name not in self.accounts:
            raise ValueError(f"Account '{account_name}' does not exist in portfolio.")
        return self.accounts[account_name]
    
    def rename_account(self, old_name: str, new_name: str):
        if old_name not in self.accounts:
            raise ValueError(f"Account '{old_name}' does not exist in portfolio.")
        elif new_name in self.accounts:
            raise ValueError(f"Account '{new_name}' already exists in portfolio.")
        self.accounts[new_name] = self.accounts.pop(old_name)

    def list_accounts(self):
        return list(self.accounts.values())

    def calculate_aaoc(self):
        total_days = 0
        for account in self.accounts.values():
            total_days += account.current_age()

        avg_days = total_days / len(self.accounts)
        return age_format(avg_days)

    
