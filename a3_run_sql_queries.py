"""
====================================================================
Capstone Project: Tata Play Subscriber Retention & Support Copilot
====================================================================

a3_run_queries.py  --  Part-A, Step-4: Run the four SQL queries from Python
===========================================================================
Purpose : Run sql/queries.sql against data/tataplay.db, print each result,
          and confirm one row of Q1 with an independent pandas calculation.
Reads   : sql/queries.sql, data/tataplay.db, data/clean/*.csv
Writes  : Nothing (Prints the Results to the Terminal, Manually copy-paste the output to README.md)
Run     : python a3_run_queries.py
"""

import re
import sqlite3

import pandas as pd

# ======================================================================
# 1. BASIC CONFIGURATION
# ======================================================================
DB_PATH = "data/tataplay.db"
SQL_PATH = "sql/queries.sql"

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


# ======================================================================
# 2. HELPERS
# ======================================================================
def load_queries(path):
    """Split the SQL file into separate queries.

    Each query in the file starts with a marker line such as "-- Q1 ...".

    Args:
        path: path to sql/queries.sql.

    Returns:
        A dict like {"Q1": "SELECT ...", "Q2": "SELECT ...", ...}.
    """
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"^-- (Q\d)\b.*$", text, flags=re.M)
    # parts = [header, "Q1", body1, "Q2", body2, ...]
    return dict(zip(parts[1::2], parts[2::2]))


def run_query(con, sql):
    """Run one SQL query and return the result as a DataFrame.

    Args:
        con: an open sqlite3 connection.
        sql: the SQL text of one query.
    """
    return pd.read_sql_query(sql, con)


# ======================================================================
# 3. THE FOUR QUERIES
# ======================================================================
def show_q1(con, queries):
    """Q1: Revenue by Plan, plus a Independent Pandas Cross-Check of One Row(Premium)."""
    q1 = run_query(con, queries["Q1"])
    print("Q1 - Revenue by Plan (SQL):\n", q1)

    # Additional Check: Independent Cross-Check using only Pandas, No SQL
    subs = pd.read_csv("data/clean/subscribers.csv")
    rech = pd.read_csv("data/clean/recharges.csv")
    plans = pd.read_csv("data/clean/plans.csv")
    merged = (
        rech[rech["status"] == "success"]
        .merge(subs[["subscriber_id", "plan_id"]], on="subscriber_id")
        .merge(plans[["plan_id", "plan_name"]], on="plan_id")
    )
    check = merged.groupby("plan_name")["amount_inr"].agg(["sum", "mean"])
    n_subs = merged.groupby("plan_name")["subscriber_id"].nunique()
    print(f"\n*** Independent Cross-Check using Pandas(No SQL) for Premium Plan alone: (Sum = {check.loc['Premium', 'sum']} | Mean = {round(check.loc['Premium', 'mean'], 2)} | Distinct Subscribers = {n_subs['Premium']})")

def show_q2(con, queries):
    """Q2: Subscribers who never had a Successful Recharge."""
    q2 = run_query(con, queries["Q2"])
    print("\nQ2 - Subscribers who Never Successfully Recharged:", len(q2),
          "| of whom 'tenure_months = 0' is:", (q2["tenure_months"] == 0).sum())


def show_q3(con, queries):
    """Q3: City rankings. Prints Rank-1 counts per city and Kolkata's First Four Rows."""
    q3 = run_query(con, queries["Q3"])
    print("\nQ3 - Subscribers with RANK() = 1, per City:")
    print(q3[q3["rnk"] == 1].groupby("city").size())
    print("\nQ3 - Subscribers with ROW_NUMBER() = 1, per City:")
    print(q3[q3["row_num"] == 1].groupby("city").size())
    print("\nQ3 - Kolkata's, First Four Rows:")
    print(q3[q3["city"] == "Kolkata"].head(4))


def show_q4(con, queries):
    """Q4: Running Total of Successful Recharges for the Subscriber TP00010."""
    q4 = run_query(con, queries["Q4"])
    print("\nQ4 - Running Total for the Subscriber TP00010:\n", q4)


# ======================================================================
# 4. MAIN
# ======================================================================
def main():
    """Open the Database, Run all Four queries and Print the Results."""
    queries = load_queries(SQL_PATH)
    con = sqlite3.connect(DB_PATH)
    show_q1(con, queries)
    show_q2(con, queries)
    show_q3(con, queries)
    show_q4(con, queries)
    con.close()


if __name__ == "__main__":
    main()