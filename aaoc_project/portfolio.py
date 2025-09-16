from datetime import date
from models import Account
from utils import valid_date, age_format
import json
import base64

class Portfolio():
    def __init__(self, name: str):
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

    def export_to_code(self):
        portfolio_data = {
            'name': self.name,
            'accounts': []
        }
        
        for account in self.accounts.values():
            account_data = {
                'name': account.name,
                'date_opened': account.date_opened.strftime('%m-%d-%Y'),
                'is_open': account.is_open,
                'closed_date': account.closed_date.strftime('%m-%d-%Y') if account.closed_date else None,
                'type': account.type
            }
            portfolio_data['accounts'].append(account_data)

        json_string = json.dumps(portfolio_data)
        encoded_bytes = base64.b64encode(json_string.encode('utf-8'))
        return encoded_bytes.decode('utf-8')

    @classmethod
    def import_from_code(cls, code):
        
        try:
            decoded_bytes = base64.b64decode(code.encode('utf-8'))
            json_string = decoded_bytes.decode('utf-8')
            portfolio_data = json.loads(json_string)

            portfolio = cls(portfolio_data['name'])
            
            for account_data in portfolio_data['accounts']:
                account = Account(
                    name=account_data['name'],
                    date_opened=account_data['date_opened'],
                    is_open="Yes" if account_data['is_open'] else "No",
                    closed_date=account_data['closed_date'],
                    type=account_data['type']
                )
                portfolio.add_account(account)
            
            return portfolio
            
        except Exception as e:
            raise ValueError(f"Invalid or corrupted portfolio code: {e}")
        
