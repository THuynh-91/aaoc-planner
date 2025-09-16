from models import Account
from portfolio import Portfolio
from planner import Planner
from utils import show_tutorial

class CLI:
    def __init__(self):
        self.portfolios = {}
        self.planners = {}
        self.current_portfolio = None
        self.current_planner = None

    def run(self):
        self.show_welcome()
        while True:
            self.show_main_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.create_portfolio()
            elif choice == "2":
                self.create_planner()
            elif choice == "3":
                print("Thank you for using AAOC Calculator!")
                break
            elif choice == "4":
                self.import_portfolio()
            elif choice == "5":
                show_tutorial()
            elif choice == "6":
                self.select_portfolio()
            elif choice == "7":
                self.list_portfolios()
            elif choice == "8":
                self.delete_portfolio()
            elif choice == "9":
                self.select_planner()
            elif choice == "10":
                self.list_planners()
            elif choice == "11":
                self.delete_planner()
            else:
                print("Invalid choice. Please try again.")
    
    def show_welcome(self):
        print("Welcome! This is AAOC (Average Age of Credit Calculator)")
        print("This tool helps you manage your credit accounts and plan future scenarios.")
        print()
    
    def show_main_menu(self):
        print("Main Menu:")
        print("1. Create Portfolio")
        print("2. Create Planner (Must have a useable Portfolio)")
        print("3. Exit")
        print("4. Import")
        print("5. How to Use")
        print("6. Select Portfolio")
        print("7. List Portfolios")  
        print("8. Delete Portfolio")
        print("9. Select Planner")
        print("10. List Planners")
        print("11. Delete Planner")
        print()

    def portfolio_menu(self):
        while True:
            print(f"\n--- PORTFOLIO: {self.current_portfolio.name} ---")
            print("1. Add Account")
            print("2. Remove Account") 
            print("3. View Accounts")
            print("4. Calculate AAOC")
            print("5. Export Portfolio")
            print("6. Return to Main Menu")
            
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.add_account()
            elif choice == "2":
                self.remove_account()
            elif choice == "3":
                self.view_accounts()
            elif choice == "4":
                self.calculate_current_aaoc()
            elif choice == "5":
                self.export_portfolio()
            elif choice == "6":
                break
            else:
                print("Invalid choice.")

    def add_account(self):
        print("Enter account details in this format:")
        print("Name, Open_Date, Status, Close_Date, Type")
        print()
        print("RULES:")
        print("- Name and Open_Date are required")
        print("- Status: 'Yes' (open) or 'No' (closed)")
        print("- If Status is 'No', Close_Date is REQUIRED")
        print("- If Status is 'Yes', Close_Date should be empty")
        print("- Type is optional (Credit Card, Loan, or leave empty)")
        print()
        print("EXAMPLES:")
        print("Open account: Chase Freedom, 03-15-2020, Yes, , Credit Card")
        print("Closed account: Old Discover, 01-10-2018, No, 05-20-2022, Credit Card")
        print("Minimum input: Chase, 03-15-2020")
        print()

        user_input = input("Account details: ").strip()

        try:
            parts = [p.strip() for p in user_input.split(",")]
            
            if len(parts) < 2:
                print("Error: Name and date are required")
                return

            if len(parts) == 2:
                account = Account(parts[0], parts[1])
            elif len(parts) == 3:
                account = Account(parts[0], parts[1], parts[2])
            elif len(parts) == 4:
                account = Account(parts[0], parts[1], parts[2], parts[3] if parts[3] else None)
            elif len(parts) == 5:
                account = Account(parts[0], parts[1], parts[2], parts[3] if parts[3] else None, parts[4] if parts[4] else None)
            else:
                print("Error: Too many fields provided")
                return
            
            self.current_portfolio.add_account(account)
            print("Account added successfully!")
            
        except Exception as e:
            print(f"Error: {e}")

    def remove_account(self):
        if not self.current_portfolio.accounts:
            print("No accounts in portfolio to remove.")
            return
        
        print("\nCurrent accounts:")
        for name in self.current_portfolio.accounts.keys():
            print(f"- {name}")
        
        account_name = input("\nEnter name of account to remove: ").strip()
        
        if not account_name:
            print("Account name cannot be empty.")
            return
        
        try:
            result = self.current_portfolio.remove_account(account_name)
            print(result)  
        except ValueError as e:
            print(f"Error: {e}")

    def view_accounts(self):
        if not self.current_portfolio.accounts:
            print("No accounts in portfolio.")
            return
        
        print(f"\n--- PORTFOLIO: {self.current_portfolio.name} ---")
        print(f"Total accounts: {len(self.current_portfolio.accounts)}")
        print("\nAccounts:")
        
        for account in self.current_portfolio.list_accounts():
            status = "Open" if account.is_open else "Closed"
            print(f"- {account.name}")
            print(f"  Opened: {account.date_opened.strftime('%m-%d-%Y')}")
            print(f"  Status: {status}")
            if not account.is_open and account.closed_date:
                print(f"  Closed: {account.closed_date.strftime('%m-%d-%Y')}")
            if account.type:
                print(f"  Type: {account.type}")
            print()

    def calculate_current_aaoc(self):
        if not self.current_portfolio.accounts:
            print("Cannot calculate AAOC - no accounts in portfolio.")
            return
        
        try:
            aaoc_result = self.current_portfolio.calculate_aaoc()
            print(f"\nCurrent AAOC: {aaoc_result}")
        except Exception as e:
            print(f"Error calculating AAOC: {e}")

    def planning_menu(self):
        while True:
            print(f"\n--- PLANNING SCENARIOS ---")
            print(f"Using portfolio: {self.current_portfolio.name}")
            print("1. Future AAOC Projection")
            print("2. AAOC with New Account")
            print("3. Time to Target AAOC") 
            print("4. Earliest New Account Date")
            print("5. Return to Main Menu")
            
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.scenario_future_aaoc()
            elif choice == "2":
                self.scenario_new_account()
            elif choice == "3":
                self.scenario_target_time()
            elif choice == "4":
                self.scenario_earliest_date()
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def create_portfolio(self):
        print("\n--- CREATE PORTFOLIO ---")
        name = input("Enter portfolio name: ").strip()
        
        if not name:
            print("Portfolio name cannot be empty.")
            return
        
        try:
            self.portfolios[name] = Portfolio(name)
            self.current_portfolio = self.portfolios[name]
            print(f"Portfolio '{name}' created successfully!")
            self.portfolio_menu()  
        except ValueError as e:
            print(f"Error: {e}")

    def create_planner(self):
        if self.current_portfolio is None:
            print("Error: You must create a portfolio first before using the planner.")
            return
        
        if not self.current_portfolio.accounts:
            print("Error: Portfolio must contain at least one account to create planner.")
            return
        
        portfolio_name = self.current_portfolio.name
        
        if portfolio_name in self.planners:
            print(f"Planner for '{portfolio_name}' already exists. Using existing planner.")
            self.current_planner = self.planners[portfolio_name]
        else:
            try:
                self.planners[portfolio_name] = Planner(self.current_portfolio)
                self.current_planner = self.planners[portfolio_name]
                print(f"Planner created using portfolio '{portfolio_name}'")
            except Exception as e:
                print(f"Error creating planner: {e}")
                return
        
        self.planning_menu()

    def scenario_future_aaoc(self):
        print("\n--- FUTURE AAOC PROJECTION ---")
        print("Calculate what your AAOC will be on a specific future date")
        print("Format: MM-DD-YYYY")
        
        target_date = input("Enter target date: ").strip()
        
        if not target_date:
            print("Date cannot be empty.")
            return
        
        try:
            result = self.current_planner.calculate_future_aaoc(target_date)
            print(f"\nResult: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

    def scenario_new_account(self):
        print("\n--- AAOC WITH NEW ACCOUNT ---")
        print("See how opening a new account on a specific date affects your AAOC")
        print("Format: MM-DD-YYYY")
        
        new_account_date = input("Enter new account opening date: ").strip()
        if not new_account_date:
            print("Account opening date cannot be empty.")
            return
        
        target_date = input("Enter target calculation date: ").strip()
        if not target_date:
            print("Target date cannot be empty.")
            return
        
        try:
            result = self.current_planner.calculate_aaoc_with_new_account(new_account_date, target_date)
            print(f"\nResult: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

    def scenario_target_time(self):
        print("\n--- TIME TO TARGET AAOC ---")
        print("Find out when you'll reach a specific AAOC target")
        
        try:
            target_years = int(input("Enter target years: ").strip())
            target_months = int(input("Enter target months (0-11): ").strip())
            
            if target_years < 0 or target_months < 0 or target_months > 11:
                print("Invalid input. Years must be >= 0, months must be 0-11.")
                return
            
            result = self.current_planner.time_to_target_aaoc(target_years, target_months)
            print(f"\nResult: {result}")
        except ValueError:
            print("Error: Please enter valid numbers for years and months.")
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

    def scenario_earliest_date(self):
        print("\n--- EARLIEST NEW ACCOUNT DATE ---")
        print("Find the earliest date you can open a new account while maintaining minimum AAOC")
        
        try:
            min_years = int(input("Enter minimum AAOC years: ").strip())
            min_months = int(input("Enter minimum AAOC months (0-11): ").strip())
            
            if min_years < 0 or min_months < 0 or min_months > 11:
                print("Invalid input. Years must be >= 0, months must be 0-11.")
                return
            
            result = self.current_planner.earliest_new_account_date(min_years, min_months)
            print(f"\nResult: {result}")
        except ValueError:
            print("Error: Please enter valid numbers for years and months.")
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

    def list_portfolios(self):
        if not self.portfolios:
            print("No portfolios created yet.")
            return
        
        print("\nAvailable portfolios:")
        for name in self.portfolios.keys():
            print(f"- {name}")

    def select_portfolio(self):
        self.list_portfolios()
        if not self.portfolios:
            return
        
        name = input("\nEnter portfolio name to select: ").strip()
        if name in self.portfolios:
            self.current_portfolio = self.portfolios[name]
            self.current_planner = self.planners.get(name) 
            print(f"Selected portfolio: {name}")
            self.portfolio_menu()
        else:
            print("Portfolio not found.")

    def delete_portfolio(self):
        self.list_portfolios()
        if not self.portfolios:
            return
    
        name = input("\nEnter portfolio name to delete: ").strip()
        if name in self.portfolios:
            del self.portfolios[name]
            if name in self.planners:
                del self.planners[name]
            if self.current_portfolio and self.current_portfolio.name == name:
                self.current_portfolio = None
                self.current_planner = None
            print(f"Portfolio '{name}' deleted.")
        else:
            print("Portfolio not found.")

    def list_planners(self):
        if not self.planners:
            print("No planners created yet.")
            return
        
        print("\nAvailable planners:")
        for portfolio_name in self.planners.keys():
            print(f"- Planner for '{portfolio_name}'")

    def select_planner(self):
        self.list_planners()
        if not self.planners:
            return
        
        portfolio_name = input("\nEnter portfolio name for planner: ").strip()
        if portfolio_name in self.planners:
            self.current_planner = self.planners[portfolio_name]
            self.current_portfolio = self.portfolios[portfolio_name] 
            print(f"Selected planner for portfolio: {portfolio_name}")
            self.planning_menu()
        else:
            print("Planner not found.")

    def delete_planner(self):
        self.list_planners()
        if not self.planners:
            return
        
        portfolio_name = input("\nEnter portfolio name for planner to delete: ").strip()
        if portfolio_name in self.planners:
            del self.planners[portfolio_name]
            if self.current_planner and portfolio_name == self.current_portfolio.name:
                self.current_planner = None
            print(f"Planner for '{portfolio_name}' deleted.")
        else:
            print("Planner not found.")

    def import_portfolio(self):
        print("\n--- IMPORT PORTFOLIO ---")
        print("Enter the portfolio code you received from export:")
        
        code = input("Portfolio code: ").strip()
        
        if not code:
            print("Code cannot be empty.")
            return
        
        try:
            imported_portfolio = Portfolio.import_from_code(code)
            
            if imported_portfolio.name in self.portfolios:
                overwrite = input(f"Portfolio '{imported_portfolio.name}' already exists. Overwrite? (yes/no): ").strip().lower()
                if overwrite != "yes":
                    print("Import cancelled.")
                    return
            
            self.portfolios[imported_portfolio.name] = imported_portfolio
            self.current_portfolio = imported_portfolio
            
            print(f"Portfolio '{imported_portfolio.name}' imported successfully!")
            print(f"Accounts imported: {len(imported_portfolio.accounts)}")
            
            menu_choice = input("Go to portfolio menu? (yes/no): ").strip().lower()
            if menu_choice == "yes":
                self.portfolio_menu()
                
        except Exception as e:
            print(f"Error importing portfolio: {e}")

    def export_portfolio(self):
        if self.current_portfolio is None:
            print("Error: No portfolio selected to export.")
            return
        
        if not self.current_portfolio.accounts:
            print("Warning: Portfolio is empty. Exporting anyway.")
        
        try:
            export_code = self.current_portfolio.export_to_code()
            
            print(f"\n--- EXPORT CODE FOR '{self.current_portfolio.name}' ---")
            print(f"Portfolio: {self.current_portfolio.name}")
            print(f"Accounts: {len(self.current_portfolio.accounts)}")
            print(f"\nYour export code:")
            print(f"{export_code}")
            print("\nSave this code to import your portfolio later.")
            print("Warning: Keep this code secure - anyone with it can recreate your portfolio.")
            
        except Exception as e:
            print(f"Error exporting portfolio: {e}")
        
        input("\nPress Enter to continue...")

def main():
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()