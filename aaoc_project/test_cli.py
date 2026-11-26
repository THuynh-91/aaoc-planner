"""CLI integration tests for the AAOC calculator.

These drive the interactive ``CLI`` class by mocking ``builtins.input`` with a
scripted ``side_effect`` list and capturing stdout. We assert on key output
substrings to verify end-to-end flows.

Run from the project root (the directory that contains the ``aaoc_project``
package):

    python -m unittest aaoc_project.test_cli -v
"""
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from io import StringIO
from unittest import mock

if __package__:
    from .cli import CLI
    from .portfolio import Portfolio
    from .models import Account
else:  # pragma: no cover - fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from aaoc_project.cli import CLI
    from aaoc_project.portfolio import Portfolio
    from aaoc_project.models import Account


def days_ago(n):
    """Return an MM-DD-YYYY string for the date n days before today."""
    return (date.today() - timedelta(days=n)).strftime('%m-%d-%Y')


def days_from_now(n):
    return (date.today() + timedelta(days=n)).strftime('%m-%d-%Y')


def run_cli(inputs):
    """Run CLI.run() feeding ``inputs`` to input(); return captured stdout.

    The scripted list should normally terminate the program with the Exit
    choice ("0" at the main menu). If the script runs out of inputs, input()
    raises StopIteration; the CLI catches EOFError/KeyboardInterrupt but NOT
    StopIteration, so callers should always feed a clean exit. To exercise the
    EOF path use ``run_cli_eof``.
    """
    buf = StringIO()
    cli = CLI()
    with mock.patch("builtins.input", side_effect=inputs):
        with redirect_stdout(buf):
            cli.run()
    return buf.getvalue(), cli


def run_cli_eof(inputs):
    """Like run_cli but raises EOFError when the scripted inputs run out,
    simulating a real terminal hitting end-of-file / Ctrl-D."""
    buf = StringIO()
    cli = CLI()

    seq = iter(inputs)

    def fake_input(prompt=""):
        try:
            return next(seq)
        except StopIteration:
            raise EOFError

    with mock.patch("builtins.input", side_effect=fake_input):
        with redirect_stdout(buf):
            cli.run()
    return buf.getvalue(), cli


class TestCLIBasics(unittest.TestCase):
    def test_welcome_and_exit(self):
        out, cli = run_cli(["0"])
        self.assertIn("AAOC - Average Age of Credit Calculator", out)
        self.assertIn("Goodbye", out)

    def test_invalid_menu_choice(self):
        out, _ = run_cli(["99", "0"])
        self.assertIn("Invalid choice", out)

    def test_blank_menu_choice(self):
        out, _ = run_cli(["", "0"])
        self.assertIn("Please enter a choice", out)

    def test_eof_exits_gracefully(self):
        # No inputs at all -> first prompt raises EOFError -> graceful exit.
        out, _ = run_cli_eof([])
        self.assertIn("Exiting AAOC Calculator", out)

    def test_tutorial_choice(self):
        # Tutorial calls input() itself ("Press Enter..."), then we exit.
        out, _ = run_cli(["10", "", "0"])
        self.assertIn("AAOC CALCULATOR GUIDE", out)


class TestCLIPortfolioFlow(unittest.TestCase):
    def test_create_add_calculate(self):
        # Create portfolio -> add two accounts -> calculate AAOC -> return -> exit
        inputs = [
            "1",                       # main: Create Portfolio
            "MyCards",                 # portfolio name
            "1", f"A, {days_ago(730)}",   # portfolio menu: add account A (2 yrs)
            "1", f"B, {days_ago(0)}",     # add account B (brand new)
            "4",                       # Calculate AAOC
            "0",                       # return to main
            "0",                       # exit
        ]
        out, cli = run_cli(inputs)
        self.assertIn("created successfully", out)
        self.assertIn("added successfully", out)
        self.assertIn("Current AAOC", out)
        self.assertIn("1 years and 0 months", out)
        self.assertIn("MyCards", cli.portfolios)
        self.assertEqual(set(cli.portfolios["MyCards"].accounts), {"A", "B"})

    def test_add_closed_account(self):
        inputs = [
            "1", "P",
            "1", f"Old, {days_ago(800)}, No, {days_ago(100)}, Credit Card",
            "3",          # view accounts
            "0", "0",
        ]
        out, cli = run_cli(inputs)
        self.assertIn("added successfully", out)
        self.assertIn("Old", out)
        self.assertIn("Closed", out)
        self.assertFalse(cli.portfolios["P"].accounts["Old"].is_open)

    def test_view_accounts_empty(self):
        inputs = ["1", "P", "3", "0", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("No accounts in portfolio", out)

    def test_remove_account(self):
        inputs = [
            "1", "P",
            "1", f"A, {days_ago(100)}",
            "2", "A",      # remove account A
            "0", "0",
        ]
        out, cli = run_cli(inputs)
        self.assertIn("removed from", out)
        self.assertNotIn("A", cli.portfolios["P"].accounts)

    def test_remove_account_empty_portfolio(self):
        inputs = ["1", "P", "2", "0", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("No accounts in portfolio to remove", out)

    def test_calculate_aaoc_empty_portfolio(self):
        inputs = ["1", "P", "4", "0", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("no accounts", out.lower())

    def test_timeline_view(self):
        inputs = [
            "1", "P",
            "1", f"Old, {days_ago(730)}",
            "1", f"New, {days_ago(0)}",
            "5", "",      # view timeline + press enter to continue
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("AAOC TIMELINE", out)
        self.assertIn("Average Age of Credit", out)

    def test_portfolio_submenu_invalid_and_blank(self):
        inputs = ["1", "P", "x", "", "0", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Invalid choice", out)
        self.assertIn("Please enter a choice (0-6)", out)

    def test_create_portfolio_blank_name_cancel(self):
        inputs = ["1", "", "0"]
        out, cli = run_cli(inputs)
        self.assertIn("cannot be empty", out)
        self.assertEqual(cli.portfolios, {})

    def test_duplicate_portfolio_name(self):
        inputs = [
            "1", "P", "0",   # create P, return
            "1", "P",        # try to create P again
            "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("already exists", out)


class TestCLIAddAccountParser(unittest.TestCase):
    """Exercise the comma-field parser in add_account for 2/3/4/5 fields and
    too-many-fields."""

    def _add(self, account_line):
        inputs = ["1", "P", "1", account_line, "0", "0"]
        return run_cli(inputs)

    def test_two_fields(self):
        out, cli = self._add(f"Acc, {days_ago(100)}")
        self.assertIn("added successfully", out)
        self.assertTrue(cli.portfolios["P"].accounts["Acc"].is_open)

    def test_three_fields_status(self):
        out, cli = self._add(f"Acc, {days_ago(100)}, Yes")
        self.assertIn("added successfully", out)
        self.assertTrue(cli.portfolios["P"].accounts["Acc"].is_open)

    def test_four_fields_closed(self):
        out, cli = self._add(f"Acc, {days_ago(400)}, No, {days_ago(50)}")
        self.assertIn("added successfully", out)
        self.assertFalse(cli.portfolios["P"].accounts["Acc"].is_open)

    def test_five_fields_with_type(self):
        out, cli = self._add(f"Acc, {days_ago(100)}, Yes, , Loan")
        self.assertIn("added successfully", out)
        self.assertEqual(cli.portfolios["P"].accounts["Acc"].type, "Loan")

    def test_too_many_fields(self):
        out, cli = self._add(f"Acc, {days_ago(100)}, Yes, , Loan, extra")
        self.assertIn("Too many fields", out)
        self.assertEqual(cli.portfolios["P"].accounts, {})

    def test_missing_required_fields(self):
        out, cli = self._add("OnlyName")
        self.assertIn("required", out)
        self.assertEqual(cli.portfolios["P"].accounts, {})

    def test_blank_input_cancels(self):
        out, cli = self._add("")
        self.assertIn("Cancelled", out)
        self.assertEqual(cli.portfolios["P"].accounts, {})

    def test_invalid_date_reports_error(self):
        out, cli = self._add("Acc, 99-99-9999")
        self.assertIn("Error", out)
        self.assertEqual(cli.portfolios["P"].accounts, {})

    def test_duplicate_account_via_cli(self):
        inputs = [
            "1", "P",
            "1", f"Acc, {days_ago(100)}",
            "1", f"Acc, {days_ago(50)}",
            "0", "0",
        ]
        out, cli = run_cli(inputs)
        self.assertIn("already exists", out)
        self.assertEqual(len(cli.portfolios["P"].accounts), 1)


class TestCLIExportImport(unittest.TestCase):
    def test_export_then_import_roundtrip(self):
        # Build a portfolio with one account, export to grab the code.
        p = Portfolio("Src")
        p.add_account(Account("A", days_ago(365), type="Credit Card"))
        code = p.export_to_code()

        # Import via the main menu (choice 5), decline the portfolio menu.
        inputs = ["5", code, "no", "0"]
        out, cli = run_cli(inputs)
        self.assertIn("imported successfully", out)
        self.assertIn("Accounts imported: 1", out)
        self.assertIn("Src", cli.portfolios)
        self.assertEqual(set(cli.portfolios["Src"].accounts), {"A"})

    def test_import_invalid_code(self):
        inputs = ["5", "!!!not-base64!!!", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Error importing portfolio", out)

    def test_import_blank_cancels(self):
        inputs = ["5", "", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Cancelled", out)

    def test_export_from_menu(self):
        inputs = [
            "1", "P",
            "1", f"A, {days_ago(100)}",
            "6", "",       # export + press enter to continue
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("EXPORT CODE FOR", out)
        # The export code is valid base64; importing it back should work.

    def test_export_import_full_roundtrip_via_menu(self):
        # Create + add account, export and capture the code from stdout.
        inputs = [
            "1", "Wallet",
            "1", f"Visa, {days_ago(900)}, No, {days_ago(100)}, Credit Card",
            "6", "",
            "0", "0",
        ]
        out, cli = run_cli(inputs)
        code = cli.portfolios["Wallet"].export_to_code()
        restored = Portfolio.import_from_code(code)
        self.assertEqual(restored.name, "Wallet")
        self.assertFalse(restored.accounts["Visa"].is_open)
        self.assertEqual(restored.accounts["Visa"].type, "Credit Card")


class TestCLIPlannerFlow(unittest.TestCase):
    def _make_cli_with_portfolio(self):
        """Return scripted-prefix inputs that create a portfolio + planner."""
        return [
            "1", "P",
            "1", f"A, {days_ago(365)}",
            "0",        # return to main menu
        ]

    def test_create_planner_and_future_aaoc(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",                       # create planner for P
            "1", days_from_now(365), "",    # scenario 1: future projection
            "0",                            # return to main
            "0",                            # exit
        ]
        out, cli = run_cli(inputs)
        self.assertIn("Planner created", out)
        self.assertIn("Projected AAOC", out)
        self.assertIn("2 years and 0 months", out)
        self.assertIn("P", cli.planners)

    def test_planner_new_account_scenario(self):
        today = date.today().strftime('%m-%d-%Y')
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "2", today, today, "",     # scenario 2: new account both today
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("AAOC with new account", out)
        self.assertIn("0 years and 6 months", out)

    def test_planner_time_to_target_scenario(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "3", "0", "6", "",     # scenario 3: already achieved (0y6m)
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("already achieved", out)

    def test_planner_earliest_date_scenario(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "4", "0", "0", "",     # scenario 4: minimum 0y0m -> immediate
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("can open a new account", out)

    def test_planner_invalid_scenario_choice(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "x", "",      # invalid then blank
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("Invalid choice", out)
        self.assertIn("Please enter a choice (0-4)", out)

    def test_create_planner_no_portfolio(self):
        inputs = ["6", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("No portfolios available", out)

    def test_create_planner_empty_portfolio_rejected(self):
        inputs = [
            "1", "P", "0",     # create empty portfolio, return
            "6", "P",          # try to make planner -> rejected
            "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("at least one account", out)

    def test_target_time_invalid_numbers(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "3", "abc", "0", "",    # non-numeric years
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("valid whole numbers", out)

    def test_target_time_out_of_range_months(self):
        inputs = self._make_cli_with_portfolio() + [
            "6", "P",
            "3", "1", "12", "",    # months out of 0-11 range
            "0", "0",
        ]
        out, _ = run_cli(inputs)
        self.assertIn("Invalid input", out)


class TestCLIManagement(unittest.TestCase):
    def test_list_portfolios_empty(self):
        out, _ = run_cli(["3", "0"])
        self.assertIn("No portfolios created yet", out)

    def test_list_planners_empty(self):
        out, _ = run_cli(["8", "0"])
        self.assertIn("No planners created yet", out)

    def test_select_nonexistent_portfolio(self):
        inputs = ["1", "P", "0", "2", "Nope", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Portfolio not found", out)

    def test_delete_portfolio(self):
        inputs = ["1", "P", "0", "4", "P", "0"]
        out, cli = run_cli(inputs)
        self.assertIn("deleted", out)
        self.assertNotIn("P", cli.portfolios)

    def test_delete_nonexistent_portfolio(self):
        inputs = ["1", "P", "0", "4", "Nope", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Portfolio not found", out)

    def test_select_planner_nonexistent(self):
        inputs = self._prefix() + ["7", "Nope", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Planner not found", out)

    def test_list_planners_after_create(self):
        inputs = self._prefix() + ["8", "0"]
        out, _ = run_cli(inputs)
        self.assertIn("Planner for 'P'", out)

    def test_delete_planner(self):
        inputs = self._prefix() + ["9", "P", "0"]
        out, cli = run_cli(inputs)
        self.assertIn("Planner for 'P' deleted", out)
        self.assertNotIn("P", cli.planners)

    def _prefix(self):
        """Create portfolio P with an account and a planner, return to main."""
        return [
            "1", "P",
            "1", f"A, {days_ago(365)}",
            "0",
            "6", "P", "0",     # create planner, return from planning menu
        ]


if __name__ == "__main__":
    unittest.main()
