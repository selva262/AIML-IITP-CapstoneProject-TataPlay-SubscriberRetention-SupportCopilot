"""
====================================================================
Capstone Project: Tata Play Subscriber Retention & Support Copilot
====================================================================

a2_clean_store.py  --  Part-A, Step-2: Clean the data and store it
==================================================================
Purpose : Turn the messy raw exports into trusted Clean Tables, then Save
          them as CSV files and as a SQLite database.
Reads   : data/raw/subscribers.csv, data/raw/recharges.csv, data/raw/plans.csv
Writes  : data/clean/subscribers.csv, data/clean/recharges.csv, data/clean/plans.csv
          data/tataplay.db  (Tables: Subscribers, Recharges, Plans)
Run     : python a2_clean_store.py

IMPORTANT RULE: 
1. No Missing Value is filled in this Script.
2. Filling blanks (imputation) happens inside the Part B pipeline, AFTER the
train/test split, so that no test row can influence the filled values
(which would be data leakage).
"""

import os
import sqlite3

import numpy as np
import pandas as pd

# =============================================================================
# 1. BASIC CONFIGURATION
# =============================================================================

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"
DB_PATH = "data/tataplay.db"

# Alternative City Names -> The one Official Name (Keys are Lower-Case).
# A Dictionary, a Lookup Table of "Old Name → Correct Name."
CITY_MAP = {
    "bangalore": "Bengaluru",
    "Bangalore": "Bengaluru",
    "bombay": "Mumbai",
    "Bombay": "Mumbai",
    "madras": "Chennai",
    "Madras": "Chennai",
    "calcutta": "Kolkata",
    "Calcutta": "Kolkata",
    "new delhi": "Delhi",
    "New Delhi": "Delhi",
    "hyd": "Hyderabad",
    "Hyd": "Hyderabad",
}

# All raw auto_renew Spellings -> Yes / No (Keys are Lower-Case).
# A Dictionary, a Lookup Table of "Old Name → Correct Name."
AUTO_MAP = {"y": "Yes", "yes": "Yes", "n": "No", "no": "No"}


# =============================================================================
# 2. LOADING the RAW CSVs(Subscribers, Recharges, Plans Tables)
# =============================================================================
def load_raw():
    """Read the Three raw CSV files.

    Returns:
        A Tuple (subs, rech, plans) of Pandas DataFrames.
    """
    # Read the Three raw CSVs into Pandas DataFrames.
    subs = pd.read_csv(os.path.join(RAW_DIR, "subscribers.csv"))
    rech = pd.read_csv(os.path.join(RAW_DIR, "recharges.csv"))
    plans = pd.read_csv(os.path.join(RAW_DIR, "plans.csv"))
    return subs, rech, plans


# =============================================================================
# 3. CLEANING: SUBSCRIBERS TABLE(CSV)
# =============================================================================
def clean_city(value):
    """Return the Standard City Name for One raw City Value.

    Steps: Trim Spaces, ignore case, map known alternative names
    (e.g. Bangalore -> Bengaluru), otherwise return Title Case.

    Args:
        Value: A Raw City string such as " BENGALURU " or "Madras".
    """

    # Trim Spaces, ignore case, map known alternative names (e.g. Bangalore -> Bengaluru), otherwise return Title Case.
    key = str(value).strip().lower()
    return CITY_MAP.get(key, key.title())


def clean_subscribers(subs):
    """Clean the Subscribers Table. Missing Values are NOT filled.

    Rules applied (Each prints how many Rows/Values it changed):
      1. Drop exact Duplicate Rows.
      2. Standardise City to exactly Seven Names.
      3. Map auto_renew to Yes / No.
      4. Turn Ages outside 10-100 into Missing Values (NaN).

    Args:
        subs: The raw Subscribers DataFrame.

    Returns:
        The cleaned Subscribers DataFrame.
    """

    print("===== CLEANING SUBSCRIBERS TABLE(CSV) =====\n")

    # Rule-1: Duplicate Rows Removal
    s0 = len(subs)
    subs = subs.drop_duplicates().reset_index(drop=True)
    print("Duplicates Removed:", s0 - len(subs), "-> Total Rows after Duplicates Removal:", len(subs))

    # Rule-2: Standardize 'city' Column Names i.e, Fix City Name as Trimmed, Lower-Case, Mapped to Official Names
    subs["city"] = subs["city"].apply(clean_city)

    # Rule-3: Standardize 'auto_renew' Column i.e, Fix Auto_Renew Value as Trimmed, Lower-Case, Mapped to Standard Value
    subs["auto_renew"] = (
        subs["auto_renew"].astype(str).str.strip().str.lower().map(AUTO_MAP)
    )

    # Rule-4: Handle Impossible Ages - Impossible Ages become Missing Values
    # We do not fill the Missing Values in this stage
    bad_age = (subs["age"] < 10) | (subs["age"] > 100)
    print("Impossible Ages set to Missing Count:", bad_age.sum())
    subs.loc[bad_age, "age"] = np.nan

    # Print Summary for the Subscribers Table(CSV)
    print("\nCity Counts:\n", subs["city"].value_counts())
    print("\nAuto_Renew Counts:\n", subs["auto_renew"].value_counts())
    print("\nMissing Age Count:", subs["age"].isna().sum())
    print("Missing payment_mode Count:", subs["payment_mode"].isna().sum())
    print("Total Churned Count:", subs["churned"].sum(), f"({subs['churned'].mean() * 100:.2f}%)")
    return subs


# =============================================================================
# 4. CLEANING: RECHARGES TABLE(CSV)
# =============================================================================
def clean_recharges(rech, subs):
    """Clean the Recharges Table.

    Rules applied (Each prints how many Rows/Values it changed):
      1. Drop exact Duplicate Rows.
      2. Drop Rows whose Subscriber does not exist (Orphans).
      3. Lower-Case the Status Column.
      4. Convert amount_inr to Numbers; where that is impossible
         (e.g. "INR 498"), rebuild it as the Subscriber's
         monthly_recharge_inr.
      5. Parse recharge_date as a Real Date.

    Args:
        rech: The raw Recharges DataFrame.
        subs: The CLEAN Subscribers DataFrame (needed for rules 2 and 4).

    Returns:
        The cleaned Recharges DataFrame.
    """

    print("\n\n===== CLEANING RECHARGES TABLE(CSV) =====\n")

    # Rule-1: Duplicate Rows Removal
    r0 = len(rech)
    rech = rech.drop_duplicates().reset_index(drop=True)
    print("Duplicates Removed:", r0 - len(rech), "-> Total Rows after Duplicates Removal:", len(rech))

    # Rule-2: Remove Orphan Rows(subscriber_id not present in Subscribers Table(CSV))
    r1 = len(rech)
    rech = rech[rech["subscriber_id"].isin(subs["subscriber_id"])].reset_index(drop=True)
    print("Orphan Rows Removed:", r1 - len(rech), "-> Total Rows after Orphans Removal:", len(rech))

    # Rule-3: Standardize 'Status' Column i.e, Lower-Case and Trimmed
    rech["status"] = rech["status"].astype(str).str.strip().str.lower()

    # Rule-4: Fix Bad Amounts in 'amount_inr' Column. Text becomes NaN first, then we rebuild those values.
    rech["amount_inr"] = pd.to_numeric(rech["amount_inr"], errors="coerce")
    bad_amount = rech["amount_inr"].isna()

     # We rebuild the bad amounts using the Subscriber's monthly_recharge_inr from the Subscribers Table(CSV)
     # monthly is a lookup table: "subscriber ID → that subscriber's usual monthly recharge amount."
     # For each row with a bad amount, it looks up that subscriber's ID and fills in their usual monthly recharge.
    monthly = subs.set_index("subscriber_id")["monthly_recharge_inr"]
    rech.loc[bad_amount, "amount_inr"] = rech.loc[bad_amount, "subscriber_id"].map(monthly)
    print("Amounts Rebuilt Count:", bad_amount.sum())

    # Rule-5: Convert Dates i.e, Parse'recharge_date' column value to a Real Date.
    rech["recharge_date"] = pd.to_datetime(rech["recharge_date"])

    # Print Summary for the Recharges Table(CSV)
    print("\nStatus Counts:\n", rech["status"].value_counts())
    success = rech["status"] == "success"
    print("\nTotal Successful Amount:", rech.loc[success, "amount_inr"].sum())
    return rech


# =============================================================================
# 5. SAVING: CLEAN DATA CSVs & SQLite DATABASE
# =============================================================================
def save_clean_csvs(subs, rech, plans):
    """Save the Three clean Tables as CSV files in data/clean/.

    Args:
        subs, rech, plans: The clean DataFrames (plans is unchanged).
    """

    # Saving the clean CSVs into the data/clean/ folder. If the folder does not exist, it is created.
    os.makedirs(CLEAN_DIR, exist_ok=True)
    subs.to_csv(os.path.join(CLEAN_DIR, "subscribers.csv"), index=False)
    rech.to_csv(os.path.join(CLEAN_DIR, "recharges.csv"), index=False)
    plans.to_csv(os.path.join(CLEAN_DIR, "plans.csv"), index=False)


def save_to_sqlite(subs, rech, plans):
    """Write the Three clean Tables into the SQLite Database file.

    Dates are stored as text in YYYY-MM-DD form, which SQLite sorts
    correctly. An existing database file is deleted first, so the script
    can be re-run safely.

    Args:
        subs, rech, plans: The clean DataFrames.
    """

    # Duplicate the Recharges Table, so the changes here don't affect the original DataFrame.
    # SQLite does not have a native date type, so convert the recharge_date to text in YYYY-MM-DD format.
    rech_db = rech.copy()
    rech_db["recharge_date"] = rech_db["recharge_date"].dt.strftime("%Y-%m-%d")

    # Save the clean tables into a SQLite database file. 
    # If an Old DB file already exists, it is deleted first. Otherwise, running the script twice would try to create tables that already exist and cause an error.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = sqlite3.connect(DB_PATH)                  # Opens (and Creates) the database file.
    subs.to_sql("subscribers", con, index=False)    # Saves the Subscribers DataFrame as a table named "subscribers" in the database.
    rech_db.to_sql("recharges", con, index=False)   # Saves the Recharges DataFrame as a table named "recharges" in the database.
    plans.to_sql("plans", con, index=False)         # Saves the Plans DataFrame as a table named "plans" in the database.
    con.close()                                     # Closes the Database connection, ensuring all changes are saved and resources are freed.


# =============================================================================
# 6. MAIN
# =============================================================================
def main():
    """Run the Full Part-A cleaning pipeline: Load, Clean, Save."""
    subs, rech, plans = load_raw()
    subs = clean_subscribers(subs)
    rech = clean_recharges(rech, subs)
    save_clean_csvs(subs, rech, plans)
    save_to_sqlite(subs, rech, plans)
    print("\n\nSummary: Saved clean CSVs in data/clean folder, created data/tataplay.db and saved the three CSVs as three tables in it.")


if __name__ == "__main__":
    main()