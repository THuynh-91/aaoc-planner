"""AAOC - Average Age of Credit calculator and planner.

A small, dependency-free toolkit for tracking credit accounts, computing the
Average Age of Credit (AAOC), and running "what-if" planning scenarios.

Public API::

    from aaoc_project import Account, Portfolio, Planner

The interactive CLI can be launched with::

    python -m aaoc_project
"""
from .models import Account
from .portfolio import Portfolio
from .planner import Planner, add_months
from .utils import (
    valid_date,
    valid_closed_date,
    valid_planning_date,
    age_format,
)

__all__ = [
    "Account",
    "Portfolio",
    "Planner",
    "add_months",
    "valid_date",
    "valid_closed_date",
    "valid_planning_date",
    "age_format",
]

__version__ = "1.0.0"
