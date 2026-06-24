"""Unit tests for the AAOC calculator core and planner math.

Run from the project root (the directory that contains the `aaoc_project`
package):

    python -m unittest aaoc_project.test_aaoc -v

or discover all tests (keep the top-level dir as the import root):

    python -m unittest discover -s aaoc_project -t . -v
"""
import os
import sys
import unittest
from datetime import date, timedelta

# Support being run as a package module (`python -m aaoc_project.test_aaoc`,
# `unittest discover`) and also when this file is executed directly from inside
# the package directory (`python test_aaoc.py`).
if __package__:
    from .models import Account
    from .portfolio import Portfolio
    from .planner import Planner, add_months
    from .utils import (
        age_format, valid_date, valid_closed_date, valid_planning_date,
        render_breakdown,
    )
else:  # pragma: no cover - fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from aaoc_project.models import Account
    from aaoc_project.portfolio import Portfolio
    from aaoc_project.planner import Planner, add_months
    from aaoc_project.utils import (
        age_format, valid_date, valid_closed_date, valid_planning_date,
        render_breakdown,
    )


def days_ago(n):
    """Return an MM-DD-YYYY string for the date n days before today."""
    return (date.today() - timedelta(days=n)).strftime('%m-%d-%Y')


class TestUtils(unittest.TestCase):
    def test_age_format_basic(self):
        # 365.25 days == exactly 1 year, 0 months.
        self.assertEqual(age_format(365.25), "1 years and 0 months")

    def test_age_format_zero(self):
        self.assertEqual(age_format(0), "0 years and 0 months")

    def test_age_format_month_rounding_rolls_to_year(self):
        # ~11.5 months should round up to 12 and roll into the next year.
        days = 365.25 * (11.6 / 12)
        result = age_format(days)
        # Should never report "12 months"; it must roll to the next year.
        self.assertNotIn("12 months", result)

    def test_valid_date_rejects_bad_format(self):
        with self.assertRaises(ValueError):
            valid_date("2020-01-01")

    def test_valid_date_rejects_future(self):
        future = (date.today() + timedelta(days=30)).strftime('%m-%d-%Y')
        with self.assertRaises(ValueError):
            valid_date(future)

    def test_valid_date_rejects_invalid_calendar_date(self):
        with self.assertRaises(ValueError):
            valid_date("13-45-2020")

    def test_valid_planning_date_allows_future(self):
        future = (date.today() + timedelta(days=400)).strftime('%m-%d-%Y')
        self.assertEqual(valid_planning_date(future),
                         date.today() + timedelta(days=400))

    def test_valid_closed_date(self):
        self.assertTrue(valid_closed_date(date(2020, 1, 1), date(2021, 1, 1)))
        self.assertFalse(valid_closed_date(date(2021, 1, 1), date(2020, 1, 1)))


class TestAddMonths(unittest.TestCase):
    def test_simple_add(self):
        self.assertEqual(add_months(date(2020, 1, 15), 1), date(2020, 2, 15))

    def test_year_rollover(self):
        self.assertEqual(add_months(date(2020, 12, 10), 1), date(2021, 1, 10))

    def test_end_of_month_clamping(self):
        # Jan 31 + 1 month -> Feb 29 (2020 is a leap year), clamped.
        self.assertEqual(add_months(date(2020, 1, 31), 1), date(2020, 2, 29))

    def test_multi_year(self):
        self.assertEqual(add_months(date(2020, 6, 15), 24), date(2022, 6, 15))


class TestAccount(unittest.TestCase):
    def test_blank_name_rejected(self):
        with self.assertRaises(ValueError):
            Account("   ", days_ago(100))

    def test_closed_account_requires_close_date(self):
        with self.assertRaises(ValueError):
            Account("X", days_ago(100), is_open="No")

    def test_open_account_cannot_have_close_date(self):
        with self.assertRaises(ValueError):
            Account("X", days_ago(100), is_open="Yes", closed_date=days_ago(10))

    def test_current_age_open(self):
        acc = Account("X", days_ago(365))
        self.assertEqual(acc.current_age(), 365)

    def test_age_on_caps_at_close_date(self):
        acc = Account("X", days_ago(400), is_open="No", closed_date=days_ago(100))
        # Asking for age "today" should cap at the close date span (300 days).
        result = acc.age_on(date.today().strftime('%m-%d-%Y'))
        self.assertEqual(result, 300)

    def test_age_on_before_open_raises(self):
        acc = Account("X", days_ago(100))
        before = (date.today() - timedelta(days=200)).strftime('%m-%d-%Y')
        with self.assertRaises(ValueError):
            acc.age_on(before)

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            Account("X", days_ago(100), is_open="maybe")


class TestPortfolio(unittest.TestCase):
    def test_calculate_aaoc(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(730)))   # 2 years
        p.add_account(Account("B", days_ago(0)))      # brand new
        # Average ~365 days ~ 1 year.
        self.assertEqual(p.calculate_aaoc(), "1 years and 0 months")

    def test_calculate_aaoc_empty_raises(self):
        p = Portfolio("P")
        with self.assertRaises(ValueError):
            p.calculate_aaoc()

    def test_duplicate_account_rejected(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(100)))
        with self.assertRaises(ValueError):
            p.add_account(Account("A", days_ago(50)))

    def test_export_import_roundtrip(self):
        p = Portfolio("MyP")
        p.add_account(Account("A", days_ago(365), type="Credit Card"))
        p.add_account(Account("B", days_ago(800), is_open="No",
                              closed_date=days_ago(100)))
        code = p.export_to_code()
        restored = Portfolio.import_from_code(code)
        self.assertEqual(restored.name, "MyP")
        self.assertEqual(set(restored.accounts.keys()), {"A", "B"})
        self.assertFalse(restored.accounts["B"].is_open)

    def test_import_invalid_code_raises(self):
        with self.assertRaises(ValueError):
            Portfolio.import_from_code("not-valid-base64-json!!!")


class TestPlanner(unittest.TestCase):
    def make_portfolio(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(365)))
        return p

    def test_empty_portfolio_rejected(self):
        with self.assertRaises(ValueError):
            Planner(Portfolio("empty"))

    def test_none_portfolio_rejected(self):
        with self.assertRaises(ValueError):
            Planner(None)

    def test_future_aaoc_grows(self):
        planner = Planner(self.make_portfolio())
        # One account opened 365 days ago, projected one more year forward.
        future = (date.today() + timedelta(days=365)).strftime('%m-%d-%Y')
        self.assertEqual(planner.calculate_future_aaoc(future), "2 years and 0 months")

    def test_new_account_lowers_aaoc(self):
        planner = Planner(self.make_portfolio())
        today_str = date.today().strftime('%m-%d-%Y')
        # Existing account ~1 yr + brand new account today -> average ~0.5 yr.
        result = planner.calculate_aaoc_with_new_account(today_str, today_str)
        self.assertEqual(result, "0 years and 6 months")

    def test_time_to_target_already_achieved(self):
        planner = Planner(self.make_portfolio())
        result = planner.time_to_target_aaoc(0, 6)
        self.assertIn("already achieved", result)

    def test_time_to_target_future(self):
        planner = Planner(self.make_portfolio())
        result = planner.time_to_target_aaoc(2, 0)
        self.assertIn("wait", result)

    def test_time_to_target_negative_rejected(self):
        planner = Planner(self.make_portfolio())
        with self.assertRaises(ValueError):
            planner.time_to_target_aaoc(-1, 0)

    def test_earliest_new_account_date_negative_rejected(self):
        planner = Planner(self.make_portfolio())
        with self.assertRaises(ValueError):
            planner.earliest_new_account_date(-1, 0)

    def test_hypothetical_account_isolated_from_original(self):
        portfolio = self.make_portfolio()
        planner = Planner(portfolio)
        planner.add_hypothetical_account(Account("Hypo", days_ago(10)))
        # Original portfolio should not be mutated.
        self.assertNotIn("Hypo", portfolio.accounts)
        self.assertIn("Hypo", planner.working_accounts)


class TestAccountMutations(unittest.TestCase):
    def test_rename(self):
        acc = Account("Old", days_ago(100))
        acc.rename("  New  ")
        self.assertEqual(acc.name, "New")

    def test_rename_blank_rejected(self):
        acc = Account("Old", days_ago(100))
        with self.assertRaises(ValueError):
            acc.rename("   ")

    def test_close_then_reopen(self):
        acc = Account("X", days_ago(400))
        acc.close(days_ago(100))
        self.assertFalse(acc.is_open)
        self.assertEqual(acc.current_age(), 300)
        acc.reopen()
        self.assertTrue(acc.is_open)
        self.assertIsNone(acc.closed_date)

    def test_close_before_open_rejected(self):
        acc = Account("X", days_ago(100))
        with self.assertRaises(ValueError):
            acc.close(days_ago(200))

    def test_close_already_closed_rejected(self):
        acc = Account("X", days_ago(400), is_open="No", closed_date=days_ago(100))
        with self.assertRaises(ValueError):
            acc.close(days_ago(50))

    def test_reopen_already_open_rejected(self):
        acc = Account("X", days_ago(100))
        with self.assertRaises(ValueError):
            acc.reopen()

    def test_status_aliases_accepted(self):
        for status in ("y", "true", "YES"):
            self.assertTrue(Account("X", days_ago(10), is_open=status).is_open)
        for status in ("n", "false", "NO"):
            acc = Account("X", days_ago(10), is_open=status, closed_date=days_ago(5))
            self.assertFalse(acc.is_open)


class TestPortfolioAnalytics(unittest.TestCase):
    def test_aaoc_years_matches_days(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(365)))
        p.add_account(Account("B", days_ago(0)))
        self.assertAlmostEqual(p.aaoc_years(), p.aaoc_days() / 365.25, places=9)

    def test_account_breakdown_sorted_oldest_first(self):
        p = Portfolio("P")
        p.add_account(Account("Young", days_ago(100)))
        p.add_account(Account("Old", days_ago(1000)))
        rows = p.account_breakdown()
        self.assertEqual([r["name"] for r in rows], ["Old", "Young"])
        self.assertEqual(rows[0]["status"], "Open")

    def test_account_breakdown_marks_closed(self):
        p = Portfolio("P")
        p.add_account(Account("Closed", days_ago(500), is_open="No",
                              closed_date=days_ago(100)))
        rows = p.account_breakdown()
        self.assertEqual(rows[0]["status"], "Closed")

    def test_aaoc_days_empty_raises(self):
        with self.assertRaises(ValueError):
            Portfolio("P").aaoc_days()

    def test_rename_account_in_portfolio(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(100)))
        p.rename_account("A", "B")
        self.assertIn("B", p.accounts)
        self.assertNotIn("A", p.accounts)

    def test_rename_account_conflict_rejected(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(100)))
        p.add_account(Account("B", days_ago(50)))
        with self.assertRaises(ValueError):
            p.rename_account("A", "B")


class TestRenderBreakdown(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(render_breakdown([], 0), "No accounts to display.")

    def test_contains_account_and_average(self):
        p = Portfolio("P")
        p.add_account(Account("Visa", days_ago(730)))
        p.add_account(Account("New", days_ago(0)))
        out = render_breakdown(p.account_breakdown(), p.aaoc_years())
        self.assertIn("Visa", out)
        self.assertIn("New", out)
        self.assertIn("Average Age of Credit", out)
        # The older account should be flagged as helping (+), the new one (v).
        self.assertIn("+", out)
        self.assertIn("v", out)


class TestPlannerExtra(unittest.TestCase):
    def make_portfolio(self):
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(365)))
        return p

    def test_new_account_after_target_rejected(self):
        planner = Planner(self.make_portfolio())
        new = (date.today() + timedelta(days=400)).strftime('%m-%d-%Y')
        target = (date.today() + timedelta(days=100)).strftime('%m-%d-%Y')
        with self.assertRaises(ValueError):
            planner.calculate_aaoc_with_new_account(new, target)

    def test_future_excludes_not_yet_opened_accounts(self):
        # An account opened in the future should be excluded until its date.
        p = Portfolio("P")
        p.add_account(Account("A", days_ago(365)))
        planner = Planner(p)
        # Add a hypothetical account opening 200 days from now.
        future = (date.today() + timedelta(days=200))
        hypo = Account("Future", days_ago(0))
        hypo.date_opened = future
        planner.working_accounts["Future"] = hypo
        # Target 100 days out: only "A" is open, so AAOC keeps climbing.
        target = (date.today() + timedelta(days=100)).strftime('%m-%d-%Y')
        result = planner.calculate_future_aaoc(target)
        self.assertEqual(result, "1 years and 3 months")

    def test_earliest_new_account_zero_target_immediate(self):
        planner = Planner(self.make_portfolio())
        result = planner.earliest_new_account_date(0, 0)
        self.assertIn("can open a new account", result)

    def test_earliest_new_account_high_target_delayed(self):
        planner = Planner(self.make_portfolio())
        result = planner.earliest_new_account_date(5, 0)
        # Either it finds a date or reports unreachable, but must not crash.
        self.assertTrue(
            "can open a new account" in result or "not reachable" in result
        )

    def test_remove_hypothetical_account(self):
        planner = Planner(self.make_portfolio())
        planner.add_hypothetical_account(Account("Hypo", days_ago(10)))
        planner.remove_account("Hypo")
        self.assertNotIn("Hypo", planner.working_accounts)

    def test_remove_nonexistent_hypothetical_rejected(self):
        planner = Planner(self.make_portfolio())
        with self.assertRaises(ValueError):
            planner.remove_account("Nope")

    def test_duplicate_hypothetical_rejected(self):
        planner = Planner(self.make_portfolio())
        planner.add_hypothetical_account(Account("Hypo", days_ago(10)))
        with self.assertRaises(ValueError):
            planner.add_hypothetical_account(Account("Hypo", days_ago(5)))


if __name__ == "__main__":
    unittest.main()
