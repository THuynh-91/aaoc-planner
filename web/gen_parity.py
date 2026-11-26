"""Writes web/core/tests/parity.txt: answers the Python package gives for random portfolios, which the Rust core
(web/core) must reproduce exactly (`cargo test`, tests/parity.rs).

Each case fixes "today" (the package reads date.today(), so it is patched per case), builds a portfolio through the
package's own Account and Portfolio classes, and records:
  now      the current AAOC string (Portfolio.calculate_aaoc)
  future   the AAOC string on a later date (Planner.calculate_future_aaoc)
  withnew  the AAOC string with a new account opened on one date, measured on another
  target   Planner.time_to_target_aaoc for a target in years and months
  earliest Planner.earliest_new_account_date for a minimum in years and months

Deterministic (fixed seed), so CI regenerates the file and fails if it changed: the Rust port and the Python
package cannot drift apart unnoticed.
usage (from the repository root): python web/gen_parity.py
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import aaoc_project.models as models  # noqa: E402
import aaoc_project.planner as planner  # noqa: E402
import aaoc_project.utils as utils  # noqa: E402
from aaoc_project import Account, Planner, Portfolio  # noqa: E402

OUT = ROOT / "web" / "core" / "tests" / "parity.txt"
CASES = 400


def fixed_today(day):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return day
    return FixedDate


def ymd(d):
    return d.strftime("%m-%d-%Y")


def main():
    rng = random.Random(20261125)
    lines = ["# case|today|accounts (opened:closed or opened:-)|query|args|python's answer"]
    for case in range(CASES):
        today = date(2026, 1, 1) + timedelta(days=rng.randrange(0, 900))
        patched = fixed_today(today)
        for module in (models, utils, planner):
            module.date = patched
        portfolio = Portfolio(f"case{case}")
        accounts = []
        for i in range(rng.randint(1, 8)):
            opened = today - timedelta(days=rng.randrange(1, 9000))
            closed = None
            if rng.random() < 0.3:
                span = (today - opened).days
                if span > 1:
                    closed = opened + timedelta(days=rng.randrange(1, span))
            portfolio.add_account(Account(f"a{i}", ymd(opened), "No" if closed else "Yes", ymd(closed) if closed else None))
            accounts.append(f"{ymd(opened)}:{ymd(closed) if closed else '-'}")
        head = f"{case}|{ymd(today)}|{','.join(accounts)}"
        plan = Planner(portfolio)

        lines.append(f"{head}|now||{portfolio.calculate_aaoc()}")
        later = today + timedelta(days=rng.randrange(0, 4000))
        lines.append(f"{head}|future|{ymd(later)}|{plan.calculate_future_aaoc(ymd(later))}")
        opened_new = today + timedelta(days=rng.randrange(0, 1500))
        measured = opened_new + timedelta(days=rng.randrange(0, 2000))
        lines.append(f"{head}|withnew|{ymd(opened_new)} {ymd(measured)}|{plan.calculate_aaoc_with_new_account(ymd(opened_new), ymd(measured))}")
        ty, tm = rng.randint(0, 25), rng.randint(0, 11)
        lines.append(f"{head}|target|{ty} {tm}|{plan.time_to_target_aaoc(ty, tm)}")
        my, mm = rng.randint(0, 20), rng.randint(0, 11)
        lines.append(f"{head}|earliest|{my} {mm}|{plan.earliest_new_account_date(my, mm)}")

    # Portfolios of 32 accounts whose average lands exactly on half a month (only possible at 32 or more accounts),
    # where Python's round (half to even) and a plain round (half away from zero) disagree.
    today = date(2026, 6, 1)
    patched = fixed_today(today)
    for module in (models, utils, planner):
        module.date = patched
    halves = 0
    for total in range(487, 1461 * 32 * 12, 1461):
        days = total / 32
        years_float = days / 365.25
        raw = (years_float - int(years_float)) * 12
        if raw - int(raw) != 0.5:
            continue
        ages = [total // 32] * 32
        ages[-1] += total - sum(ages)
        portfolio = Portfolio(f"half{halves}")
        accounts = []
        for i, age in enumerate(ages):
            opened = today - timedelta(days=age)
            portfolio.add_account(Account(f"h{i}", ymd(opened), "Yes", None))
            accounts.append(f"{ymd(opened)}:-")
        lines.append(f"{CASES + halves}|{ymd(today)}|{','.join(accounts)}|now||{portfolio.calculate_aaoc()}")
        halves += 1

    for module in (models, utils, planner):
        module.date = date

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {CASES + halves} cases ({halves} on an exact half month), {len(lines) - 1} answers")


if __name__ == "__main__":
    main()
