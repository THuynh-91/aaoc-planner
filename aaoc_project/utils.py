from datetime import datetime, date
import re

DATE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$") #MM-DD-YYYY format

def _parse_date(given_date: str) -> date:
    """Parse an MM-DD-YYYY string into a date, with clear error messages.

    Shared by valid_date and valid_planning_date so the format contract and
    error wording stay in one place.
    """
    if given_date is None:
        raise ValueError("Date cannot be empty! Use: MM-DD-YYYY")

    if not isinstance(given_date, str):
        raise ValueError("Date must be a string in MM-DD-YYYY format")

    given_date = given_date.strip()
    if not given_date:
        raise ValueError("Date cannot be empty! Use: MM-DD-YYYY")

    if not DATE_PATTERN.match(given_date):
        raise ValueError("This formatting is invalid! Use: MM-DD-YYYY")

    try:
        return datetime.strptime(given_date, '%m-%d-%Y').date()
    except ValueError:
        raise ValueError("This is an invalid date")

def valid_date(given_date: str):
    dt = _parse_date(given_date)

    if dt > date.today():
        raise ValueError("Date cannot be in the future.")
    return dt

def valid_closed_date(open_date: date, closed_date: date):
    return closed_date > open_date

def age_format(total_days: int):
    if total_days is None:
        raise ValueError("Cannot format age from None")

    # Guard against negative inputs (e.g. bad date math) by clamping to zero
    # so callers always get a sensible, non-negative duration string.
    if total_days < 0:
        total_days = 0

    years_float = total_days / 365.25
    years = int(years_float)
    months = round((years_float - years) * 12)

    if months == 12:
        years += 1
        months = 0
    return f'{years} years and {months} months'

def valid_planning_date(given_date: str):
    return _parse_date(given_date)

def show_tutorial():
    print("\n" + "="*60)
    print("                   AAOC CALCULATOR GUIDE")
    print("="*60)
    
    print("\nWHAT IS AVERAGE AGE OF CREDIT (AAOC)?")
    print("AAOC measures how long your credit accounts have been open on average.")
    print("A higher AAOC generally helps your credit score.")
    
    print("\nFEATURES:")
    print("1. PORTFOLIO MANAGEMENT")
    print("   - Create and manage your real credit accounts")
    print("   - Add/remove accounts with validation")
    print("   - Calculate current AAOC")
    print("   - Export/import portfolios for saving")
    
    print("\n2. PLANNING SCENARIOS")
    print("   - Project future AAOC on any date")
    print("   - See impact of opening new accounts")
    print("   - Find when you'll reach target AAOC")
    print("   - Determine earliest safe date for new accounts")
    
    print("\nHOW TO USE:")
    print("Step 1: Create a Portfolio")
    print("        - Give it a name (e.g., 'My Credit Cards')")
    print("        - Add your real accounts one by one")
    
    print("\nStep 2: Add Accounts")
    print("        Format: Name, MM-DD-YYYY, Status, Type")
    print("        Example: Chase Freedom, 03-15-2020, Yes, Credit Card")
    print("        Minimum: Name and Date required")
    
    print("\nStep 3: Use Planning Scenarios")
    print("        - Create a Planner using your Portfolio")
    print("        - Run 'what-if' scenarios without affecting real data")
    
    print("\nEXAMPLE SCENARIOS:")
    print("- 'What will my AAOC be in 2030?'")
    print("- 'If I open a new card in 2027, what happens to my AAOC?'")
    print("- 'When will I reach 8 years AAOC?'")
    print("- 'When can I safely open a new card?'")
    
    print("\nTIPS:")
    print("- Portfolio contains only real accounts (past/present dates)")
    print("- Planner allows hypothetical future scenarios")
    print("- Closed accounts stop aging at their close date")
    print("- Export codes let you save and reload portfolios")
    
    print("\n" + "="*60)
    
    input("\nPress Enter to return to main menu...")


def render_breakdown(rows, aaoc_years, bar_width: int = 30):
    """Return a multi-line string visualizing each account's age as a bar.

    `rows` is the output of Portfolio.account_breakdown(); `aaoc_years` is the
    portfolio average. Accounts above the average are flagged as helping the
    AAOC, those below as dragging it down.
    """
    if not rows:
        return "No accounts to display."

    max_years = max((r["age_years"] for r in rows), default=0) or 1
    lines = []
    name_width = max((len(r["name"]) for r in rows), default=4)
    name_width = max(name_width, 4)

    for r in rows:
        filled = int(round((r["age_years"] / max_years) * bar_width))
        bar = "#" * filled + "-" * (bar_width - filled)
        marker = "+" if r["age_years"] >= aaoc_years else "v"
        lines.append(
            f"  {r['name']:<{name_width}} | {bar} | "
            f"{r['age_years']:5.2f}y {marker} ({r['status']})"
        )

    lines.append("")
    lines.append(f"  Average Age of Credit: {age_format(aaoc_years * 365.25)} "
                 f"({aaoc_years:.2f} years)")
    lines.append("  Legend: + above average (helps AAOC), "
                 "v below average (lowers AAOC)")
    return "\n".join(lines)
