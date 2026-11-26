"""
Data Quality Check: Tata Play Subscriber Retention & Support Copilot
====================================================================

a1_audit.py  --  Part A, Step 1: Audit the raw tables
=====================================================
Purpose:
    First-look health check of the two raw input files i.e, Measure the "mess" in the raw exports BEFORE cleaning anything.

Inputs:
    data/raw/subscribers.csv : one row per subscriber (age, city, payment mode, etc.)
    data/raw/recharges.csv   : one row per recharge transaction

What this script reports:
    1. Basic profile of each file (shape, column data types, missing values)
    2. Specific quality checks on subscribers (duplicates, bad ages, messy text)
    3. Specific quality checks on recharges (bad amounts, messy status, orphan rows)

Writes: 
    The complete audit report to README.md
    and also prints it to the terminal.

Note: 
    This script only READS and REPORTS. It does not modify or fix any data.

Run     : python a1_audit.py
"""

import io
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------
# 1. BASIC CONFIGURATION
# ----------------------------------------------------------------------
SUBS_PATH = "data/raw/subscribers.csv"
RECH_PATH = "data/raw/recharges.csv"
README_PATH = "README.md"


# ----------------------------------------------------------------------
# 2. GENERIC AUDIT (works for any DataFrame)
# ----------------------------------------------------------------------
def audit_table(name, df):
    """Print shape, data types and the missing-value count/percent of every column.

    Args:
        name: a label for the table, used in the printed heading.
        df:   the pandas DataFrame to audit.
    """
    print(f"\n===== {name} =====")

    # Size of the Table: (number of rows, number of columns)
    print("Shape:", df.shape)

    # Data type of each Column (int, float, text, etc.)
    print("\ndtypes:\n", df.dtypes)

    # Missing Values: Count and Percentage per Column
    missing = pd.DataFrame({
        "Missing": df.isna().sum(),                    # count of blanks per column
        "Percent(%)": (df.isna().mean() * 100).round(2),      # percentage of blanks per column
    })
    print("\nMissing Values:\n", missing)


# ----------------------------------------------------------------------
# 3. TABLE-SPECIFIC FIGURES (the numbers the brief asks us to report)
# ----------------------------------------------------------------------

# =============================================================================
# 3.a. SUBSCRIBERS: DETAILED QUALITY CHECKS
# =============================================================================
def subscriber_figures(subs):
    """Print the specific data-quality figures for the Subscribers Table.

    Args:
        subs: the raw subscribers DataFrame.
    """
    print("\n===== Subscribers CSV Figures =====")

    # --- Volume and Duplicates ---
    print("Rows:", len(subs))                                           # Total Records
    print("Exact Duplicate Rows:", subs.duplicated().sum())             # Fully Identical Rows
    print("Distinct subscriber_id:", subs["subscriber_id"].nunique())   # Should Equal Rows if IDs are Unique

    # --- Age Checks ---
    print("Blank age:", subs["age"].isna().sum())                        # Missing Ages
    # An age below 10 or above 100 is impossible, so we count it as bad data.
    print("Age outside 10-100:", ((subs["age"] < 10) | (subs["age"] > 100)).sum())
    
    # --- Other Missing Values ---
    print("Blank payment_mode:", subs["payment_mode"].isna().sum())

    # --- Inconsistent Text Spellings ---
    # If "Mumbai", "mumbai", "MUMBAI " are all present, each counts as separate,
    # So a high number here hints at messy spellings needing cleanup.
    print("Distinct Raw City Spellings:", subs["city"].nunique())
    print("Distinct Raw auto_renew Spellings:", subs["auto_renew"].nunique())               # e.g. Yes/Y/yes/TRUE

    # --- Missing Target-related Value ---
    print("Blank next_cycle_recharge_inr:", subs["next_cycle_recharge_inr"].isna().sum())   


# =============================================================================
# 3.b. RECHARGES: DETAILED QUALITY CHECKS
# =============================================================================
def recharge_figures(rech, subs):
    """Print the specific data-quality figures for the recharges table.

    Args:
        rech: the raw recharges DataFrame.
        subs: the raw subscribers DataFrame (used to detect orphan rows).
    """
    print("\n===== Recharges CSV Figures =====")

    # --- Volume and Duplicates ---
    print("Rows:", len(rech))                                       # Total Records
    print("Exact Duplicate Rows:", rech.duplicated().sum())          # Fully Identical Rows
    print("Distinct recharge_id:", rech["recharge_id"].nunique())   # Should Equal Rows if IDs are Unique

    # --- Amount Column: Find Values that are not proper numbers ---
    # errors="coerce" turns anything Non-Numeric (e.g. "Rs.199", "abc") into NaN,
    # So counting NaN afterwards tells us how many bad entries exist.
    amount_num = pd.to_numeric(rech["amount_inr"], errors="coerce")
    print("amount_inr not Plain Numbers:", amount_num.isna().sum())

    # --- Inconsistent Text Spellings ---
    print("Distinct Raw Status Spellings:", rech["status"].nunique())   # e.g. Success/success/SUCCESS   

    # --- Orphan Check (Referential Integrity) ---
    # An "orphan" is a recharge whose subscriber_id does not exist in the subscribers table.
    # isin() checks membership; ~ flips it, so we count the IDs that are NOT found.
    orphans = ~rech["subscriber_id"].isin(subs["subscriber_id"])
    print("Orphan subscriber_id Rows:", orphans.sum())


# ----------------------------------------------------------------------
# 4. MAIN
# ----------------------------------------------------------------------
def main():
    """Load the raw files, and print the full audit report, and save the printed reports manually to the README.md."""
    subs = pd.read_csv(SUBS_PATH)
    rech = pd.read_csv(RECH_PATH)

    audit_table("Subscribers CSV Audit", subs)
    audit_table("Recharges CSV Audit", rech)
    subscriber_figures(subs)
    recharge_figures(rech, subs)


if __name__ == "__main__":
    main()