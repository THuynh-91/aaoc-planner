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