# AAOC (Average Age of Credit) Calculator

A comprehensive Python application for managing credit accounts and planning credit-related financial scenarios.<br>
https://github.com/THuynh-91/AAOC/blob/main/main.py (Old Version)<br>
Decided to implement a improved version of this CLI with more features, and OOP

**Try it in your browser: https://thuynh-91.github.io/aaoc-planner/** (no install; your accounts stay in your browser)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Web View (Rust + WebAssembly)](#web-view-rust--webassembly)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Core Classes](#core-classes)
- [Planning Scenarios](#planning-scenarios)
- [Data Import/Export](#data-importexport)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Overview

The AAOC Calculator helps users manage their credit accounts and plan future credit decisions. Average Age of Credit is a crucial factor in credit scoring - this tool allows you to:

- Track your real credit accounts (cards, loans, etc.)
- Calculate your current Average Age of Credit
- Run "what-if" scenarios for future planning
- Determine optimal timing for opening new accounts
- Import/export your portfolio data

## Features

### Portfolio Management
- **Account CRUD Operations**: Add, remove, view, and modify credit accounts
- **Real Account Validation**: Ensures only past/present dates for actual accounts
- **Multiple Portfolio Support**: Create and manage separate portfolios
- **AAOC Calculation**: Calculate current Average Age of Credit with detailed formatting
- **AAOC Timeline**: An ASCII bar per account showing its age, flagging which accounts pull the average up (`+`) or down (`v`)

### Planning Scenarios
1. **Future AAOC Projection**: "What will my AAOC be on a specific date?"
2. **New Account Impact**: "How will opening a new account affect my AAOC?"
3. **Time to Target**: "When will I reach my target AAOC?"
4. **Earliest New Account Date**: "When can I safely open a new account?"

### Data Management
- **Export/Import**: Save and load portfolios using encoded strings (Inspired by CTF Challenges from MetaCTF)
- **Multiple Portfolios**: Manage different account collections
- **Data Validation**: Comprehensive input validation and error handling

## Web View (Rust + WebAssembly)

The browser version at https://thuynh-91.github.io/aaoc-planner/ runs the same math as the CLI, ported to Rust and compiled to
WebAssembly (about 22 KB, no dependencies). The page is TypeScript with no framework: an account editor, the AAOC with a
timeline of which accounts raise or lower it, and the four planning scenarios. Portfolio codes are shared with the CLI, so
a code exported in one imports in the other.

- `web/core/`: the Rust crate. Dates are whole days since 1970 (a Gregorian calendar from scratch, month stepping that
  clamps Jan 31 to Feb 28/29 like the Python `add_months`), and the WebAssembly boundary is hand-written: accounts go
  into the module's memory as pairs of integers.
- `web/gen_parity.py`: runs the Python package on 400 random portfolios (plus 32-account portfolios that land exactly
  on half a month, where Python's half-to-even rounding matters) and records its 2,005 answers.
  `cargo test` must reproduce every one word for word, and CI regenerates the file and fails if it changed, so the
  two implementations cannot drift apart.
- `web/app/`: the page (`index.html`, `style.css`, `src/*.ts`).
- `.github/workflows/web.yml`: tests, builds and publishes to GitHub Pages on every push to `main`.

Build it locally:

```bash
rustup target add wasm32-unknown-unknown
cargo test --manifest-path web/core/Cargo.toml
cargo build --release --target wasm32-unknown-unknown --manifest-path web/core/Cargo.toml
cp web/core/target/wasm32-unknown-unknown/release/aaoc_core.wasm web/app/
cd web/app && npm ci && npm run build && python -m http.server 8000
```

## Installation

### Prerequisites
- Python 3.10+ (the code uses the `str | None` type syntax)
- No external dependencies required (uses only standard library)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/THuynh-91/aaoc-planner.git
cd aaoc-planner
```

2. Run the application from the repository root (`aaoc_project` is a package):
```bash
python -m aaoc_project
```

### Optional Web UI (Streamlit)
An interactive web UI is built on the same core classes. It is the only part of the project that needs a third-party package:
```bash
pip install streamlit
python -m streamlit run streamlit_app.py
```
It offers a portfolio editor, the AAOC metric, a horizontal age-timeline chart (flagging which accounts are above or below the average), the four planning scenarios as forms, and export/import. The command-line tool stays dependency-free.

### Running the Tests
The tests use the standard library's `unittest`, so there is nothing to install:
```bash
python -m unittest discover -s aaoc_project -p "test_*.py"
```
GitHub Actions runs the same command on Python 3.10 to 3.13 for every push and pull request.

## Usage

### Quick Start
1. **Create a Portfolio**: Start by creating a new portfolio with a descriptive name
2. **Add Accounts**: Add your credit accounts with opening dates and status
3. **Calculate AAOC**: View your current Average Age of Credit
4. **Plan Scenarios**: Create a planner to run future projections

### Account Input Format
When adding accounts, use this format:
```
Name, Open_Date, Status, Close_Date, Type
```

**Examples:**
```
Chase Freedom, 03-15-2020, Yes, , Credit Card
Old Discover, 01-10-2018, No, 05-20-2022, Credit Card  
Chase, 03-15-2020
```

**Rules:**
- Name and Open_Date are required
- Status: 'Yes' (open) or 'No' (closed)
- If Status is 'No', Close_Date is required
- If Status is 'Yes', Close_Date should be empty
- Type is optional (Credit Card, Loan, or leave empty)

### Main Menu Navigation
```
Portfolio:
  1. Create Portfolio      - Start a new portfolio
  2. Select Portfolio      - Switch between portfolios
  3. List Portfolios       - View all portfolios
  4. Delete Portfolio      - Remove portfolio
  5. Import Portfolio      - Load a saved portfolio code
Planner:
  6. Create Planner        - Run planning scenarios (needs a portfolio with accounts)
  7. Select Planner        - Switch planners
  8. List Planners         - View all planners
  9. Delete Planner        - Remove planner
Other:
  10. How to Use           - Detailed tutorial
  0. Exit                  - Close application
```
Leaving any prompt blank cancels it, and Ctrl-C exits safely from anywhere.

## Project Structure

```
aaoc-planner/
├── README.md              # This file
├── requirements.txt       # No runtime dependencies (documents Python 3.10+)
├── streamlit_app.py       # Optional web UI (needs streamlit)
├── web/                   # Browser version: Rust core (core/) -> WebAssembly, TypeScript page (app/), parity cases
└── aaoc_project/          # The package
    ├── __init__.py        # Public API: Account, Portfolio, Planner, date helpers
    ├── __main__.py        # Lets `python -m aaoc_project` start the CLI
    ├── models.py          # Account class with validation and age calculations
    ├── portfolio.py       # Portfolio class: accounts, AAOC, timeline breakdown
    ├── planner.py         # Planner class for scenario planning
    ├── cli.py             # Command-line interface
    ├── utils.py           # Date/age helpers, timeline rendering and tutorial
    ├── test_aaoc.py       # unittest suite for the core and planner math
    └── test_cli.py        # CLI tests that drive every menu flow with mocked input
```

## Core Classes

### Account Class
Represents individual credit accounts with comprehensive validation.

**Key Methods:**
- `rename(new_name)`: Change account name
- `close(on_date)`: Close account with date
- `reopen()`: Reopen closed account
- `current_age()`: Get current age in days
- `age_on(as_of_date)`: Calculate age on specific date

**Business Rules:**
- Open accounts cannot have close dates
- Closed accounts must have close dates
- Accounts cannot be opened in the future
- Account names cannot be blank

### Portfolio Class
Manages collections of real credit accounts.

**Key Features:**
- Unique account names within portfolio
- AAOC calculation with formatted output
- Export/import functionality using Base64 encoding
- Comprehensive CRUD operations

**Validation:**
- Only allows past/present dates
- Prevents duplicate account names
- Validates all account data before adding

### Planner Class
Handles hypothetical scenarios and future planning.

**Design Philosophy:**
- Works with copies (original portfolio untouched)
- Allows future dates and hypothetical accounts
- Cannot transfer hypothetical data back to Portfolio
- Supports complex "what-if" analysis

## Planning Scenarios

### 1. Future AAOC Projection
Calculate what your AAOC will be on any future date with no account changes.

**Use Case**: "What will my AAOC be in 2030?"

### 2. New Account Impact Analysis
See how opening a new account on a specific date affects your AAOC on a target date.

**Use Case**: "If I open a new card in 2027, what's my AAOC in 2030?"

### 3. Time to Target AAOC
Find when you'll reach a specific AAOC goal.

**Use Case**: "When will I reach 8 years AAOC?"
**Output**: "To reach AAOC of 8 years 0 months, you will need to wait 2 years 4 months or until 01-16-2028"

### 4. Earliest New Account Date
Determine the earliest date you can open a new account while maintaining minimum AAOC.

**Use Case**: "When can I open a new card and keep at least 5 years AAOC?"

## Data Import/Export

### Export Format
Portfolios are exported as Base64-encoded JSON strings containing:
- Portfolio name
- All account details (name, dates, status, type)
- Account relationships and validation data

### Security Notice
Export codes contain all your account information. Keep them secure and only share with trusted parties.

### Example Export Code
```
eyJuYW1lIjogIlRlc3QgUG9ydGZvbGlvIiwgImFjY291bnRzIjogW3sibmFtZSI6ICJTdHVkZW50IERpc2NvdmVyIiwgImRhdGVfb3BlbmVkIjogIjA0LTIyLTIwMTAiLCAiaXNfb3BlbiI6IHRydWUsICJjbG9zZWRfZGF0ZSI6IG51bGwsICJ0eXBlIjogIkNyZWRpdCBDYXJkIn0sIHsibmFtZSI6ICJCYW5rIG9mIEFtZXJpY2EiLCAiZGF0ZV9vcGVuZWQiOiAiMDgtMTMtMjAxNSIsICJpc19vcGVuIjogdHJ1ZSwgImNsb3NlZF9kYXRlIjogbnVsbCwgInR5cGUiOiAiQ3JlZGl0IENhcmQifSwgeyJuYW1lIjogIkNGVSIsICJkYXRlX29wZW5lZCI6ICIxMi0xMy0yMDI0IiwgImlzX29wZW4iOiB0cnVlLCAiY2xvc2VkX2RhdGUiOiBudWxsLCAidHlwZSI6ICJDcmVkaXQgQ2FyZCJ9LCB7Im5hbWUiOiAiU29GaSIsICJkYXRlX29wZW5lZCI6ICIxMi0xMy0yMDI0IiwgImlzX29wZW4iOiB0cnVlLCAiY2xvc2VkX2RhdGUiOiBudWxsLCAidHlwZSI6ICJDcmVkaXQgQ2FyZCJ9LCB7Im5hbWUiOiAiV0lUIExvYW4xIiwgImRhdGVfb3BlbmVkIjogIjA5LTIzLTIwMjMiLCAiaXNfb3BlbiI6IGZhbHNlLCAiY2xvc2VkX2RhdGUiOiAiMDQtMDUtMjAyNCIsICJ0eXBlIjogIkxvYW4ifSwgeyJuYW1lIjogIldJVCBMb2FuMiIsICJkYXRlX29wZW5lZCI6ICIwOS0yMy0yMDIzIiwgImlzX29wZW4iOiBmYWxzZSwgImNsb3NlZF9kYXRlIjogIjA0LTA1LTIwMjQiLCAidHlwZSI6ICJMb2FuIn0sIHsibmFtZSI6ICJORVUgTG9hbjEiLCAiZGF0ZV9vcGVuZWQiOiAiMTAtMDQtMjAyNCIsICJpc19vcGVuIjogdHJ1ZSwgImNsb3NlZF9kYXRlIjogbnVsbCwgInR5cGUiOiAiTG9hbiJ9LCB7Im5hbWUiOiAiTkVVIExvYW4yIiwgImRhdGVfb3BlbmVkIjogIjEwLTA0LTIwMjQiLCAiaXNfb3BlbiI6IHRydWUsICJjbG9zZWRfZGF0ZSI6IG51bGwsICJ0eXBlIjogIkxvYW4ifSwgeyJuYW1lIjogIkNpdGkiLCAiZGF0ZV9vcGVuZWQiOiAiMTItMDYtMjAyNCIsICJpc19vcGVuIjogdHJ1ZSwgImNsb3NlZF9kYXRlIjogbnVsbCwgInR5cGUiOiAiQ3JlZGl0IENhcmQifV19
```

## Examples

### Basic Workflow
```python
# Create portfolio
portfolio = Portfolio("My Credit Cards")

# Add accounts
account1 = Account("Chase Freedom", "03-15-2020", "Yes", None, "Credit Card")
portfolio.add_account(account1)

# Calculate AAOC
current_aaoc = portfolio.calculate_aaoc()
print(current_aaoc)  # "5 years and 6 months"

# Plan scenarios
planner = Planner(portfolio)
future_aaoc = planner.calculate_future_aaoc("01-01-2030")
```

### Planning Example
```python
# Time to target scenario
planner = Planner(portfolio)
result = planner.time_to_target_aaoc(8, 0)  # 8 years, 0 months
# Output: "To reach AAOC of 8 years 0 months, you will need to wait 2 years 4 months or until 01-16-2028"

# New account impact
impact = planner.calculate_aaoc_with_new_account("06-01-2027", "01-01-2030")
# Output: "7 years and 3 months"
```

## Technical Details

### Date Handling
- **Portfolio**: Uses `valid_date()` - rejects future dates
- **Planner**: Uses `valid_planning_date()` - allows future dates
- **Format**: MM-DD-YYYY consistently throughout application

### Age Calculations
- **Open Accounts**: Current date - opening date
- **Closed Accounts**: Closing date - opening date (frozen)
- **Precision**: Uses 365.25 days per year for accuracy

### Error Handling
Comprehensive validation with descriptive error messages:
- Date format validation
- Business rule enforcement
- Input sanitization
- Edge case handling

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to public methods
- Include comprehensive error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built as a learning project for object-oriented programming
- Inspired by the importance of credit age in financial planning
- Designed with extensibility and maintainability in mind
