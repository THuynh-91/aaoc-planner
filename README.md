# AAOC (Average Age of Credit) Calculator

A comprehensive Python application for managing credit accounts and planning credit-related financial scenarios.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
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

### Planning Scenarios
1. **Future AAOC Projection**: "What will my AAOC be on a specific date?"
2. **New Account Impact**: "How will opening a new account affect my AAOC?"
3. **Time to Target**: "When will I reach my target AAOC?"
4. **Earliest New Account Date**: "When can I safely open a new account?"

### Data Management
- **Export/Import**: Save and load portfolios using encoded strings (Inspired by CTF Challenges from MetaCTF)
- **Multiple Portfolios**: Manage different account collections
- **Data Validation**: Comprehensive input validation and error handling

## Installation

### Prerequisites
- Python 3.8+
- No external dependencies required (uses only standard library)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/THuynh-91/aaoc-calculator.git
cd aaoc-calculator
```

2. Run the application:
```bash
python cli.py
```

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
1. Create Portfolio        - Start a new portfolio
2. Create Planner          - Run planning scenarios
3. Exit                    - Close application
4. Import                  - Load saved portfolio
5. How to Use              - Detailed tutorial
6. Select Portfolio        - Switch between portfolios
7. List Portfolios         - View all portfolios
8. Delete Portfolio        - Remove portfolio
9. Select Planner          - Switch planners
10. List Planners          - View all planners
11. Delete Planner         - Remove planner
```

## Project Structure

```
aaoc_project/
├── models.py          # Account class with validation and age calculations
├── portfolio.py       # Portfolio class for account management
├── planner.py         # Planner class for scenario planning
├── cli.py             # Command-line interface
├── utils.py           # Utility functions and tutorial
└── README.md          # This file
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
