"""Streamlit web UI for the AAOC (Average Age of Credit) toolkit.

This app is a thin presentation layer built on top of the existing
``aaoc_project`` package. It does not modify any package module; it only
imports the public API and renders an interactive UI.

Run with::

    python -m streamlit run streamlit_app.py
"""
from __future__ import annotations

from datetime import date

import streamlit as st

from aaoc_project import Account, Portfolio, Planner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fmt_date(d: date) -> str:
    """Convert a datetime.date (from st.date_input) into the MM-DD-YYYY
    string the package API expects."""
    return d.strftime("%m-%d-%Y")


def get_portfolio() -> Portfolio:
    """Return the Portfolio stored in session state, creating a default one
    on first use so the rest of the app can assume it always exists."""
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = Portfolio("My Credit Portfolio")
    return st.session_state.portfolio


def set_portfolio(portfolio: Portfolio) -> None:
    st.session_state.portfolio = portfolio


# ---------------------------------------------------------------------------
# Portfolio panel
# ---------------------------------------------------------------------------
def render_portfolio_panel(portfolio: Portfolio) -> None:
    st.header("Portfolio")

    # Portfolio name (rename by rebuilding while preserving accounts).
    new_name = st.text_input("Portfolio name", value=portfolio.name)
    if new_name and new_name.strip() and new_name.strip() != portfolio.name:
        try:
            portfolio.name = new_name.strip()
        except Exception as exc:  # pragma: no cover - defensive
            st.error(str(exc))

    # ---- Add account form -------------------------------------------------
    st.subheader("Add an account")
    with st.form("add_account_form", clear_on_submit=True):
        name = st.text_input("Account name")
        date_opened = st.date_input(
            "Date opened",
            value=date.today(),
            max_value=date.today(),
        )
        status = st.radio("Status", options=["Open", "Closed"], horizontal=True)
        closed_date = st.date_input(
            "Closed date (only used if Closed)",
            value=date.today(),
            max_value=date.today(),
        )
        acc_type = st.text_input("Type (optional)", placeholder="e.g. Credit Card")
        submitted = st.form_submit_button("Add account")

    if submitted:
        try:
            is_open = "Yes" if status == "Open" else "No"
            closed = fmt_date(closed_date) if status == "Closed" else None
            account = Account(
                name=name,
                date_opened=fmt_date(date_opened),
                is_open=is_open,
                closed_date=closed,
                type=acc_type or None,
            )
            portfolio.add_account(account)
            st.success(f"Added account '{account.name}'.")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover - defensive
            st.error(f"Unexpected error: {exc}")

    # ---- Accounts table ---------------------------------------------------
    st.subheader("Accounts")
    accounts = portfolio.list_accounts()
    if not accounts:
        st.info("No accounts yet. Add one above to get started.")
        return

    table_rows = []
    for acc in accounts:
        table_rows.append(
            {
                "Name": acc.name,
                "Opened": acc.date_opened.strftime("%m-%d-%Y"),
                "Status": "Open" if acc.is_open else "Closed",
                "Closed": acc.closed_date.strftime("%m-%d-%Y")
                if acc.closed_date
                else "",
                "Type": acc.type or "",
            }
        )
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    # ---- Remove account ---------------------------------------------------
    col_rm1, col_rm2 = st.columns([3, 1])
    with col_rm1:
        to_remove = st.selectbox(
            "Remove account", options=[acc.name for acc in accounts]
        )
    with col_rm2:
        st.write("")  # spacing to align button with selectbox
        st.write("")
        if st.button("Remove"):
            try:
                msg = portfolio.remove_account(to_remove)
                st.success(msg)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    # ---- Current AAOC metric ---------------------------------------------
    try:
        aaoc_str = portfolio.calculate_aaoc()
        aaoc_years = portfolio.aaoc_years()
        st.metric("Current AAOC", aaoc_str, delta=f"{aaoc_years:.2f} years")
    except ValueError as exc:
        st.warning(str(exc))


# ---------------------------------------------------------------------------
# Timeline visualization
# ---------------------------------------------------------------------------
def render_timeline(portfolio: Portfolio) -> None:
    st.header("Timeline")

    if not portfolio.accounts:
        st.info("Add accounts to see the age timeline.")
        return

    try:
        rows = portfolio.account_breakdown()
        aaoc_years = portfolio.aaoc_years()
    except ValueError as exc:
        st.warning(str(exc))
        return

    st.caption(
        f"Average Age of Credit: {aaoc_years:.2f} years. "
        "Accounts at or above the average help your AAOC; "
        "those below pull it down."
    )

    # Bar chart of age in years, keyed by account name (oldest first).
    chart_data = {r["name"]: r["age_years"] for r in rows}
    st.bar_chart(chart_data, horizontal=True, x_label="Age (years)")

    # Above / below average detail table.
    detail = []
    for r in rows:
        detail.append(
            {
                "Account": r["name"],
                "Age (years)": round(r["age_years"], 2),
                "Status": r["status"],
                "vs Average": "Above (helps)"
                if r["age_years"] >= aaoc_years
                else "Below (lowers)",
            }
        )
    st.dataframe(detail, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Planner panel
# ---------------------------------------------------------------------------
def render_planner_panel(portfolio: Portfolio) -> None:
    st.header("Planner")

    if not portfolio.accounts:
        st.info("Add at least one account to use the planner.")
        return

    try:
        planner = Planner(portfolio)
    except ValueError as exc:
        st.warning(str(exc))
        return

    # 1. Future AAOC ------------------------------------------------------
    st.subheader("1. Future AAOC")
    future_date = st.date_input(
        "Project AAOC on this date",
        value=date.today(),
        key="future_aaoc_date",
    )
    if st.button("Calculate future AAOC"):
        try:
            result = planner.calculate_future_aaoc(fmt_date(future_date))
            st.success(f"AAOC on {fmt_date(future_date)}: {result}")
        except ValueError as exc:
            st.error(str(exc))

    # 2. AAOC with a new account -----------------------------------------
    st.subheader("2. AAOC with a new account")
    col_a, col_b = st.columns(2)
    with col_a:
        new_acc_date = st.date_input(
            "New account opened on", value=date.today(), key="new_acc_date"
        )
    with col_b:
        target_date = st.date_input(
            "Measure AAOC on", value=date.today(), key="new_acc_target_date"
        )
    if st.button("Calculate AAOC with new account"):
        try:
            result = planner.calculate_aaoc_with_new_account(
                fmt_date(new_acc_date), fmt_date(target_date)
            )
            st.success(
                f"AAOC on {fmt_date(target_date)} with a new account "
                f"opened {fmt_date(new_acc_date)}: {result}"
            )
        except ValueError as exc:
            st.error(str(exc))

    # 3. Time to reach a target AAOC -------------------------------------
    st.subheader("3. Time to reach a target AAOC")
    col_c, col_d = st.columns(2)
    with col_c:
        tgt_years = st.number_input(
            "Target years", min_value=0, value=8, step=1, key="ttt_years"
        )
    with col_d:
        tgt_months = st.number_input(
            "Target months", min_value=0, max_value=11, value=0, step=1, key="ttt_months"
        )
    if st.button("Calculate time to target"):
        try:
            result = planner.time_to_target_aaoc(int(tgt_years), int(tgt_months))
            st.success(result)
        except ValueError as exc:
            st.error(str(exc))

    # 4. Earliest safe new-account date ----------------------------------
    st.subheader("4. Earliest date to open a new account")
    col_e, col_f = st.columns(2)
    with col_e:
        min_years = st.number_input(
            "Minimum AAOC years", min_value=0, value=5, step=1, key="ena_years"
        )
    with col_f:
        min_months = st.number_input(
            "Minimum AAOC months", min_value=0, max_value=11, value=0, step=1, key="ena_months"
        )
    if st.button("Find earliest new-account date"):
        try:
            result = planner.earliest_new_account_date(
                int(min_years), int(min_months)
            )
            st.success(result)
        except ValueError as exc:
            st.error(str(exc))


# ---------------------------------------------------------------------------
# Export / import panel
# ---------------------------------------------------------------------------
def render_export_import(portfolio: Portfolio) -> None:
    st.header("Export / Import")

    st.subheader("Export code")
    if portfolio.accounts:
        try:
            code = portfolio.export_to_code()
            st.code(code, language="text")
            st.caption("Copy this code to save your portfolio.")
        except Exception as exc:  # pragma: no cover - defensive
            st.error(f"Could not export: {exc}")
    else:
        st.info("Add accounts to generate an export code.")

    st.subheader("Import code")
    import_code = st.text_area("Paste a portfolio code here", key="import_code")
    if st.button("Import"):
        if not import_code.strip():
            st.error("Please paste a portfolio code first.")
        else:
            try:
                imported = Portfolio.import_from_code(import_code.strip())
                set_portfolio(imported)
                st.success(
                    f"Imported portfolio '{imported.name}' with "
                    f"{len(imported.accounts)} account(s)."
                )
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="AAOC Planner", layout="wide")
    st.title("AAOC - Average Age of Credit")
    st.caption(
        "Track your credit accounts, see your Average Age of Credit, "
        "and run what-if planning scenarios."
    )

    portfolio = get_portfolio()

    left, right = st.columns(2)
    with left:
        render_portfolio_panel(portfolio)
        render_timeline(portfolio)
    with right:
        render_planner_panel(portfolio)
        render_export_import(portfolio)


if __name__ == "__main__":
    main()
