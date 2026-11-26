from .models import Account
from .portfolio import Portfolio
from .planner import Planner
from .utils import show_tutorial, render_breakdown


class CLI:
    def __init__(self):
        self.portfolios = {}
        self.planners = {}
        self.current_portfolio = None
        self.current_planner = None

    # ------------------------------------------------------------------ #
    # Input helpers (robust against empty input / EOF / Ctrl-C)
    # ------------------------------------------------------------------ #
    def _prompt(self, message):
        """Read a line of input, stripping whitespace.

        Raises EOFError / KeyboardInterrupt up to the caller so the main loop
        can exit gracefully instead of printing a traceback.
        """
        return input(message).strip()

    def _pause(self):
        """Wait for the user to acknowledge before redrawing a menu."""
        try:
            input("\nPress Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            # Treat an interrupted pause as "continue" rather than crashing.
            print()

    @staticmethod
    def _header(title):
        line = "=" * 60
        return f"\n{line}\n{title}\n{line}"

    # ------------------------------------------------------------------ #
    # Main loop
    # ------------------------------------------------------------------ #
    def run(self):
        self.show_welcome()
        while True:
            try:
                self.show_main_menu()
                choice = self._prompt("Enter your choice: ")

                if choice == "1":
                    self.create_portfolio()
                elif choice == "2":
                    self.select_portfolio()
                elif choice == "3":
                    self.list_portfolios()
                elif choice == "4":
                    self.delete_portfolio()
                elif choice == "5":
                    self.import_portfolio()
                elif choice == "6":
                    self.create_planner()
                elif choice == "7":
                    self.select_planner()
                elif choice == "8":
                    self.list_planners()
                elif choice == "9":
                    self.delete_planner()
                elif choice == "10":
                    show_tutorial()
                elif choice == "0":
                    print("\nThank you for using the AAOC Calculator. Goodbye!")
                    break
                elif choice == "":
                    print("Please enter a choice (0-10).")
                else:
                    print("Invalid choice. Please enter a number from 0 to 10.")
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting AAOC Calculator. Goodbye!")
                break

    def show_welcome(self):
        print(self._header("AAOC - Average Age of Credit Calculator"))
        print("This tool helps you manage your credit accounts and plan")
        print("future scenarios to understand your average age of credit.")
        print("\nTip: press Ctrl-C at any time to exit safely.")

    def show_main_menu(self):
        print("\n--- MAIN MENU ---")
        print("Portfolio:")
        print("  1. Create Portfolio")
        print("  2. Select Portfolio")
        print("  3. List Portfolios")
        print("  4. Delete Portfolio")
        print("  5. Import Portfolio")
        print("Planner:")
        print("  6. Create Planner (requires a portfolio with accounts)")
        print("  7. Select Planner")
        print("  8. List Planners")
        print("  9. Delete Planner")
        print("Other:")
        print("  10. How to Use")
        print("  0. Exit")

    # ------------------------------------------------------------------ #
    # Portfolio menu
    # ------------------------------------------------------------------ #
    def portfolio_menu(self):
        while True:
            if self.current_portfolio is None:
                return
            try:
                print(f"\n--- PORTFOLIO: {self.current_portfolio.name} ---")
                print("  1. Add Account")
                print("  2. Remove Account")
                print("  3. View Accounts")
                print("  4. Calculate AAOC")
                print("  5. View AAOC Timeline (visual breakdown)")
                print("  6. Export Portfolio")
                print("  0. Return to Main Menu")

                choice = self._prompt("Choice: ")

                if choice == "1":
                    self.add_account()
                elif choice == "2":
                    self.remove_account()
                elif choice == "3":
                    self.view_accounts()
                elif choice == "4":
                    self.calculate_current_aaoc()
                elif choice == "5":
                    self.view_timeline()
                elif choice == "6":
                    self.export_portfolio()
                elif choice == "0":
                    break
                elif choice == "":
                    print("Please enter a choice (0-6).")
                else:
                    print("Invalid choice. Please enter a number from 0 to 6.")
            except (EOFError, KeyboardInterrupt):
                print("\nReturning to main menu.")
                break

    def add_account(self):
        print("\n--- ADD ACCOUNT ---")
        print("Enter account details in this format:")
        print("  Name, Open_Date, Status, Close_Date, Type")
        print()
        print("RULES:")
        print("  - Name and Open_Date (MM-DD-YYYY) are required")
        print("  - Status: 'Yes' (open) or 'No' (closed)")
        print("  - If Status is 'No', Close_Date is REQUIRED")
        print("  - If Status is 'Yes', Close_Date should be empty")
        print("  - Type is optional (Credit Card, Loan, or leave empty)")
        print()
        print("EXAMPLES:")
        print("  Open account:   Chase Freedom, 03-15-2020, Yes, , Credit Card")
        print("  Closed account: Old Discover, 01-10-2018, No, 05-20-2022, Credit Card")
        print("  Minimum input:  Chase, 03-15-2020")
        print()

        try:
            user_input = self._prompt("Account details (or blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nAdd account cancelled.")
            return

        if not user_input:
            print("Cancelled - no account added.")
            return

        try:
            parts = [p.strip() for p in user_input.split(",")]

            if len(parts) < 2 or not parts[0] or not parts[1]:
                print("Error: Name and Open_Date are both required.")
                return

            if len(parts) == 2:
                account = Account(parts[0], parts[1])
            elif len(parts) == 3:
                account = Account(parts[0], parts[1], parts[2])
            elif len(parts) == 4:
                account = Account(parts[0], parts[1], parts[2],
                                  parts[3] if parts[3] else None)
            elif len(parts) == 5:
                account = Account(parts[0], parts[1], parts[2],
                                  parts[3] if parts[3] else None,
                                  parts[4] if parts[4] else None)
            else:
                print("Error: Too many fields provided (expected at most 5).")
                return

            self.current_portfolio.add_account(account)
            print(f"Account '{account.name}' added successfully!")

        except Exception as e:
            print(f"Error: {e}")

    def remove_account(self):
        if not self.current_portfolio.accounts:
            print("No accounts in portfolio to remove.")
            return

        print("\nCurrent accounts:")
        for name in self.current_portfolio.accounts.keys():
            print(f"  - {name}")

        try:
            account_name = self._prompt("\nEnter name of account to remove (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nRemove cancelled.")
            return

        if not account_name:
            print("Cancelled - no account removed.")
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

        print(f"\n--- ACCOUNTS IN '{self.current_portfolio.name}' ---")
        print(f"Total accounts: {len(self.current_portfolio.accounts)}")
        print()

        for account in self.current_portfolio.list_accounts():
            status = "Open" if account.is_open else "Closed"
            print(f"  - {account.name}")
            print(f"      Opened: {account.date_opened.strftime('%m-%d-%Y')}")
            print(f"      Status: {status}")
            if not account.is_open and account.closed_date:
                print(f"      Closed: {account.closed_date.strftime('%m-%d-%Y')}")
            if account.type:
                print(f"      Type:   {account.type}")
            print()

    def calculate_current_aaoc(self):
        if not self.current_portfolio.accounts:
            print("Cannot calculate AAOC - no accounts in portfolio.")
            return

        try:
            aaoc_result = self.current_portfolio.calculate_aaoc()
            print(f"\n  Current AAOC for '{self.current_portfolio.name}': {aaoc_result}")
        except Exception as e:
            print(f"Error calculating AAOC: {e}")

    def view_timeline(self):
        if not self.current_portfolio.accounts:
            print("No accounts in portfolio to visualize.")
            return

        print(f"\n--- AAOC TIMELINE: {self.current_portfolio.name} ---\n")
        try:
            rows = self.current_portfolio.account_breakdown()
            aaoc_years = self.current_portfolio.aaoc_years()
            print(render_breakdown(rows, aaoc_years))
        except Exception as e:
            print(f"Error building timeline: {e}")
        self._pause()

    # ------------------------------------------------------------------ #
    # Planning menu
    # ------------------------------------------------------------------ #
    def planning_menu(self):
        while True:
            if self.current_planner is None or self.current_portfolio is None:
                return
            try:
                print("\n--- PLANNING SCENARIOS ---")
                print(f"Using portfolio: {self.current_portfolio.name}")
                print("  1. Future AAOC Projection")
                print("  2. AAOC with New Account")
                print("  3. Time to Target AAOC")
                print("  4. Earliest New Account Date")
                print("  0. Return to Main Menu")

                choice = self._prompt("Choice: ")

                if choice == "1":
                    self.scenario_future_aaoc()
                elif choice == "2":
                    self.scenario_new_account()
                elif choice == "3":
                    self.scenario_target_time()
                elif choice == "4":
                    self.scenario_earliest_date()
                elif choice == "0":
                    break
                elif choice == "":
                    print("Please enter a choice (0-4).")
                else:
                    print("Invalid choice. Please enter a number from 0 to 4.")
            except (EOFError, KeyboardInterrupt):
                print("\nReturning to main menu.")
                break

    def create_portfolio(self):
        print("\n--- CREATE PORTFOLIO ---")
        try:
            name = self._prompt("Enter portfolio name (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCreate portfolio cancelled.")
            return

        if not name:
            print("Cancelled - portfolio name cannot be empty.")
            return

        if name in self.portfolios:
            print(f"Portfolio '{name}' already exists. Choose a different name.")
            return

        try:
            new_portfolio = Portfolio(name)
        except ValueError as e:
            print(f"Error: {e}")
            return

        self.portfolios[name] = new_portfolio
        self.current_portfolio = new_portfolio
        print(f"Portfolio '{name}' created successfully!")
        self.portfolio_menu()

    def create_planner(self):
        if not self.portfolios:
            print("Error: No portfolios available. Create a portfolio first.")
            return

        print("\n--- CREATE PLANNER ---")
        print("Available portfolios:")
        for name, portfolio in self.portfolios.items():
            account_count = len(portfolio.accounts)
            print(f"  - {name} ({account_count} accounts)")

        try:
            portfolio_name = self._prompt(
                "\nEnter portfolio name to create planner for (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCreate planner cancelled.")
            return

        if not portfolio_name:
            print("Cancelled.")
            return

        if portfolio_name not in self.portfolios:
            print("Portfolio not found.")
            return

        selected_portfolio = self.portfolios[portfolio_name]

        if not selected_portfolio.accounts:
            print("Error: Portfolio must contain at least one account to create a planner.")
            return

        if portfolio_name in self.planners:
            print(f"Planner for '{portfolio_name}' already exists. Using existing planner.")
            self.current_planner = self.planners[portfolio_name]
        else:
            try:
                self.planners[portfolio_name] = Planner(selected_portfolio)
            except Exception as e:
                print(f"Error creating planner: {e}")
                return
            self.current_planner = self.planners[portfolio_name]
            print(f"Planner created using portfolio '{portfolio_name}'.")

        # Set the current portfolio BEFORE entering planning_menu, which
        # prints self.current_portfolio.name.
        self.current_portfolio = selected_portfolio
        self.planning_menu()

    def scenario_future_aaoc(self):
        print("\n--- FUTURE AAOC PROJECTION ---")
        print("Calculate what your AAOC will be on a specific future date.")
        print("Format: MM-DD-YYYY")

        try:
            target_date = self._prompt("Enter target date (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        if not target_date:
            print("Cancelled.")
            return

        try:
            result = self.current_planner.calculate_future_aaoc(target_date)
            print(f"\n  Projected AAOC: {result}")
        except Exception as e:
            print(f"Error: {e}")

        self._pause()

    def scenario_new_account(self):
        print("\n--- AAOC WITH NEW ACCOUNT ---")
        print("See how opening a new account on a specific date affects your AAOC.")
        print("Format: MM-DD-YYYY")

        try:
            new_account_date = self._prompt("Enter new account opening date (blank to cancel): ")
            if not new_account_date:
                print("Cancelled.")
                return

            target_date = self._prompt("Enter target calculation date (blank to cancel): ")
            if not target_date:
                print("Cancelled.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        try:
            result = self.current_planner.calculate_aaoc_with_new_account(
                new_account_date, target_date)
            print(f"\n  AAOC with new account: {result}")
        except Exception as e:
            print(f"Error: {e}")

        self._pause()

    def scenario_target_time(self):
        print("\n--- TIME TO TARGET AAOC ---")
        print("Find out when you'll reach a specific AAOC target.")

        try:
            years_in = self._prompt("Enter target years: ")
            months_in = self._prompt("Enter target months (0-11): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        try:
            target_years = int(years_in)
            target_months = int(months_in)

            if target_years < 0 or target_months < 0 or target_months > 11:
                print("Invalid input. Years must be >= 0, months must be 0-11.")
                return

            result = self.current_planner.time_to_target_aaoc(target_years, target_months)
            print(f"\n  {result}")

        except ValueError:
            print("Error: Please enter valid whole numbers for years and months.")
        except Exception as e:
            print(f"Error: {e}")

        self._pause()

    def scenario_earliest_date(self):
        print("\n--- EARLIEST NEW ACCOUNT DATE ---")
        print("Find the earliest date you can open a new account while")
        print("maintaining a minimum AAOC.")

        try:
            years_in = self._prompt("Enter minimum AAOC years: ")
            months_in = self._prompt("Enter minimum AAOC months (0-11): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        try:
            min_years = int(years_in)
            min_months = int(months_in)

            if min_years < 0 or min_months < 0 or min_months > 11:
                print("Invalid input. Years must be >= 0, months must be 0-11.")
                return

            result = self.current_planner.earliest_new_account_date(min_years, min_months)
            print(f"\n  {result}")
        except ValueError:
            print("Error: Please enter valid whole numbers for years and months.")
        except Exception as e:
            print(f"Error: {e}")

        self._pause()

    # ------------------------------------------------------------------ #
    # Portfolio management
    # ------------------------------------------------------------------ #
    def list_portfolios(self):
        if not self.portfolios:
            print("No portfolios created yet.")
            return

        print("\nAvailable portfolios:")
        for name, portfolio in self.portfolios.items():
            print(f"  - {name} ({len(portfolio.accounts)} accounts)")

    def select_portfolio(self):
        self.list_portfolios()
        if not self.portfolios:
            return

        try:
            name = self._prompt("\nEnter portfolio name to select (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        if not name:
            print("Cancelled.")
            return

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

        try:
            name = self._prompt("\nEnter portfolio name to delete (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        if not name:
            print("Cancelled.")
            return

        if name in self.portfolios:
            del self.portfolios[name]
            if name in self.planners:
                del self.planners[name]
                if self.current_planner is self.planners.get(name):
                    self.current_planner = None
            if self.current_portfolio and self.current_portfolio.name == name:
                self.current_portfolio = None
                self.current_planner = None
            print(f"Portfolio '{name}' deleted.")
        else:
            print("Portfolio not found.")

    # ------------------------------------------------------------------ #
    # Planner management
    # ------------------------------------------------------------------ #
    def list_planners(self):
        if not self.planners:
            print("No planners created yet.")
            return

        print("\nAvailable planners:")
        for portfolio_name in self.planners.keys():
            print(f"  - Planner for '{portfolio_name}'")

    def select_planner(self):
        self.list_planners()
        if not self.planners:
            return

        try:
            portfolio_name = self._prompt(
                "\nEnter portfolio name for planner (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        if not portfolio_name:
            print("Cancelled.")
            return

        if portfolio_name in self.planners:
            self.current_planner = self.planners[portfolio_name]
            self.current_portfolio = self.portfolios.get(portfolio_name)
            print(f"Selected planner for portfolio: {portfolio_name}")
            self.planning_menu()
        else:
            print("Planner not found.")

    def delete_planner(self):
        self.list_planners()
        if not self.planners:
            return

        try:
            portfolio_name = self._prompt(
                "\nEnter portfolio name for planner to delete (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        if not portfolio_name:
            print("Cancelled.")
            return

        if portfolio_name in self.planners:
            del self.planners[portfolio_name]
            # Clear the current planner only if it was the one we just deleted.
            if (self.current_planner is not None
                    and self.current_portfolio is not None
                    and portfolio_name == self.current_portfolio.name):
                self.current_planner = None
            print(f"Planner for '{portfolio_name}' deleted.")
        else:
            print("Planner not found.")

    # ------------------------------------------------------------------ #
    # Import / Export
    # ------------------------------------------------------------------ #
    def import_portfolio(self):
        print("\n--- IMPORT PORTFOLIO ---")
        print("Enter the portfolio code you received from an export.")

        try:
            code = self._prompt("Portfolio code (blank to cancel): ")
        except (EOFError, KeyboardInterrupt):
            print("\nImport cancelled.")
            return

        if not code:
            print("Cancelled - code cannot be empty.")
            return

        try:
            imported_portfolio = Portfolio.import_from_code(code)
        except Exception as e:
            print(f"Error importing portfolio: {e}")
            return

        if imported_portfolio.name in self.portfolios:
            try:
                overwrite = self._prompt(
                    f"Portfolio '{imported_portfolio.name}' already exists. Overwrite? (yes/no): "
                ).lower()
            except (EOFError, KeyboardInterrupt):
                print("\nImport cancelled.")
                return
            if overwrite != "yes":
                print("Import cancelled.")
                return
            # Overwriting invalidates any existing planner for that name.
            if imported_portfolio.name in self.planners:
                del self.planners[imported_portfolio.name]

        self.portfolios[imported_portfolio.name] = imported_portfolio
        self.current_portfolio = imported_portfolio
        self.current_planner = None

        print(f"Portfolio '{imported_portfolio.name}' imported successfully!")
        print(f"Accounts imported: {len(imported_portfolio.accounts)}")

        try:
            menu_choice = self._prompt("Go to portfolio menu? (yes/no): ").lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if menu_choice == "yes":
            self.portfolio_menu()

    def export_portfolio(self):
        if self.current_portfolio is None:
            print("Error: No portfolio selected to export.")
            return

        if not self.current_portfolio.accounts:
            print("Warning: Portfolio is empty. Exporting anyway.")

        try:
            export_code = self.current_portfolio.export_to_code()
        except Exception as e:
            print(f"Error exporting portfolio: {e}")
            self._pause()
            return

        print(f"\n--- EXPORT CODE FOR '{self.current_portfolio.name}' ---")
        print(f"Portfolio: {self.current_portfolio.name}")
        print(f"Accounts:  {len(self.current_portfolio.accounts)}")
        print("\nYour export code:")
        print(f"{export_code}")
        print("\nSave this code to import your portfolio later.")
        print("Warning: Keep this code secure - anyone with it can recreate your portfolio.")

        self._pause()


def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
