from datetime import date
from .models import Account
from .utils import valid_date, age_format
import json
import base64

class Portfolio():
    def __init__(self, name: str):
        if name is None or not name.strip():
            raise ValueError("Name cannot be blank")

        self.name = name.strip()
        self.accounts = {}

    def add_account(self, account: Account):
        if not isinstance(account, Account):
            raise ValueError("add_account expects an Account instance.")
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
        if new_name is None or not new_name.strip():
            raise ValueError("Name cannot be blank")
        new_name = new_name.strip()
        if old_name not in self.accounts:
            raise ValueError(f"Account '{old_name}' does not exist in portfolio.")
        elif new_name in self.accounts and new_name != old_name:
            raise ValueError(f"Account '{new_name}' already exists in portfolio.")
        self.accounts[new_name] = self.accounts.pop(old_name)

    def list_accounts(self):
        return list(self.accounts.values())

    def calculate_aaoc(self):
        if not self.accounts:
            raise ValueError("Cannot calculate AAOC with no accounts in portfolio.")

        total_days = 0
        for account in self.accounts.values():
            total_days += account.current_age()

        avg_days = total_days / len(self.accounts)
        return age_format(avg_days)

    def aaoc_days(self):
        """Return the current AAOC as a raw average number of days."""
        if not self.accounts:
            raise ValueError("Cannot calculate AAOC with no accounts in portfolio.")
        total_days = sum(account.current_age() for account in self.accounts.values())
        return total_days / len(self.accounts)

    def aaoc_years(self):
        """Return the current AAOC as a float number of years."""
        return self.aaoc_days() / 365.25

    def account_breakdown(self):
        """Return a list of per-account age details, sorted oldest first.

        Each item is a dict with: name, age_days, age_years, status, type.
        Useful for showing which accounts pull the AAOC up or down.
        """
        rows = []
        for account in self.accounts.values():
            age_days = account.current_age()
            rows.append({
                "name": account.name,
                "age_days": age_days,
                "age_years": age_days / 365.25,
                "status": "Open" if account.is_open else "Closed",
                "type": account.type or "",
                "date_opened": account.date_opened,
            })
        rows.sort(key=lambda r: r["age_days"], reverse=True)
        return rows

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
        
        if not code or not isinstance(code, str):
            raise ValueError("Invalid or corrupted portfolio code: no code provided")

        try:
            decoded_bytes = base64.b64decode(code.encode('utf-8'), validate=True)
            json_string = decoded_bytes.decode('utf-8')
            portfolio_data = json.loads(json_string)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted portfolio code: {e}")

        if not isinstance(portfolio_data, dict):
            raise ValueError("Invalid or corrupted portfolio code: expected an object")
        if 'name' not in portfolio_data:
            raise ValueError("Invalid or corrupted portfolio code: missing 'name'")

        try:
            portfolio = cls(portfolio_data['name'])

            for account_data in portfolio_data.get('accounts', []):
                if not isinstance(account_data, dict):
                    raise ValueError("account entry must be an object")
                if 'name' not in account_data or 'date_opened' not in account_data:
                    raise ValueError("account is missing required 'name' or 'date_opened'")
                account = Account(
                    name=account_data['name'],
                    date_opened=account_data['date_opened'],
                    is_open="Yes" if account_data.get('is_open', True) else "No",
                    closed_date=account_data.get('closed_date'),
                    type=account_data.get('type')
                )
                portfolio.add_account(account)

            return portfolio

        except Exception as e:
            raise ValueError(f"Invalid or corrupted portfolio code: {e}")
        
