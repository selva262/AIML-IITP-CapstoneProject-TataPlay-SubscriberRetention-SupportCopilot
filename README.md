
# Tata Play Subscriber Retention & Support Copilot

## Overview

two or three sentences on what the project is, plus the Python and library versions used (3.11.x, and the versions from requirements.txt).

## Reproduce

numbered shell commands, from creating the venv to the last script. A grader will run these in order, so every script must be listed in the order it has to run. Add each new script as you create it.

## Part A


## A1. Audit the Raw Data

### **===== Subscribers CSV Audit =====**

Shape: (2415, 17)

dtypes:

| Column Name | Data Type |
|---|---|
| subscriber_id | str |
| city | str |
| plan_id | str |
| tenure_months | int64 |
| age | float64 |
| payment_mode | str |
| auto_renew | str |
| add_on_count | int64 |
| monthly_recharge_inr | int64 |
| hours_watched_per_week | float64 |
| hd_hours_per_week | float64 |
| sports_hours_per_week | float64 |
| channels_watched | int64 |
| support_calls_90d | int64 |
| closure_request_logged | str |
| next_cycle_recharge_inr | float64 |
| churned | int64 |
dtype: object

Missing Values:

| Column Name | Missing | Percent (%) |
|---|---:|---:|
| subscriber_id | 0 | 0.00 |
| city | 0 | 0.00 |
| plan_id | 0 | 0.00 |
| tenure_months | 0 | 0.00 |
| age | 99 | 4.10 |
| payment_mode | 116 | 4.80 |
| auto_renew | 0 | 0.00 |
| add_on_count | 0 | 0.00 |
| monthly_recharge_inr | 0 | 0.00 |
| hours_watched_per_week | 0 | 0.00 |
| hd_hours_per_week | 0 | 0.00 |
| sports_hours_per_week | 0 | 0.00 |
| channels_watched | 0 | 0.00 |
| support_calls_90d | 0 | 0.00 |
| closure_request_logged | 0 | 0.00 |
| next_cycle_recharge_inr | 516 | 21.37 |
| churned | 0 | 0.00 |


### **===== Recharges CSV Audit =====**

Shape: (13055, 6)

dtypes:

| Column Name | Data Type |
|---|---|
| recharge_id | str |
| subscriber_id | str |
| recharge_date | str |
| amount_inr | str |
| status | str |
| channel | str |
dtype: object

Missing Values:

| Column Name | Missing | Percent (%) |
|---|---:|---:|
| recharge_id | 0 | 0.0 |
| subscriber_id | 0 | 0.0 |
| recharge_date | 0 | 0.0 |
| amount_inr | 0 | 0.0 |
| status | 0 | 0.0 |
| channel | 0 | 0.0 |


### **===== Subscribers CSV Figures Report =====**

Total Rows: 2415
Exact Duplicate Rows: 15
Distinct subscriber_id: 2400
Blank age: 99
Age outside 10-100: 6
Blank payment_mode: 116
Distinct Raw City Spellings: 22
Distinct Raw auto_renew Spellings: 6
Blank next_cycle_recharge_inr: 516


### **===== Recharges CSV Figures Report =====**

Total Rows: 13055
Exact Duplicate Rows: 60
Distinct recharge_id: 12995
amount_inr not Plain Numbers: 366
Distinct Raw Status Spellings: 6
Orphan subscriber_id Rows: 10


## A2. Clean the Data & Store it

### **===== CLEANING SUBSCRIBERS TABLE(CSV) =====**

Duplicates Removed: 15 -> Total Rows after Duplicates Removal: 2400
Impossible Ages set to Missing Count: 6

City Counts:
| city | |
|---|---:|
| Mumbai | 524 |
| Delhi | 436 |
| Chennai | 391 |
| Bengaluru | 386 |
| Hyderabad | 262 |
| Pune | 245 |
| Kolkata | 156 |
Name: count, dtype: int64

Auto_Renew Counts:
| auto_renew | |
|---|---:|
| No | 1355 |
| Yes | 1045 |
Name: count, dtype: int64

Missing Age Count: 104
Missing payment_mode Count: 114
Total Churned Count: 514 (21.42%)


### **===== CLEANING RECHARGES TABLE(CSV) =====**

Duplicates Removed: 60 -> Total Rows after Duplicates Removal: 12995
Orphan Rows Removed: 10 -> Total Rows after Orphans Removal: 12985
Amounts Rebuilt Count: 364

Status Counts:
| status |  |
|---|---:|
| Success | 11442 |
| Failed | 1422 |
| Pending | 121 |
Name: count, dtype: int64

Total Successful Amount: 6457573.0

Final Summary:Saved clean CSVs in data/clean folder, created data/tataplay.db and saved the three CSVs as three tables in it.


## A3. SQL Queries Results

Q1 - Revenue by Plan (SQL):
| Index | plan_name | revenue | avg_amount | n_subscribers |
|---:|---|---:|---:|---:|
| 0 | Premium | 1471199.0 | 860.35 | 339 |
| 1 | Standard | 1323622.0 | 492.60 | 559 |
| 2 | Standard HD | 1283471.0 | 645.61 | 407 |
| 3 | Premium Plus | 1262398.0 | 1075.30 | 228 |
| 4 | Basic | 782554.0 | 326.61 | 493 |
| 5 | Basic Lite | 334329.0 | 224.83 | 298 |

*** Independent Cross-Check using Pandas(No SQL) for Premium Plan alone: (Sum = 1471199.0 | Mean = 860.35 | Distinct Subscribers = 339)


Q2 - Subscribers who Never Successfully Recharged: 76 | of whom 'tenure_months = 0' is: 68
*** Using an INNER JOIN hides 76 Subscribers, because INNER JOINS keeps only the rows subscribers that have at least one matching row. So someone with zero successful recharges has nothing to match and silently disappears, with no error and no warning.


Q3 - Subscribers with RANK() = 1, per City:
| city | |
|---|---:|
| Bengaluru | 10 |
| Chennai | 10 |
| Delhi | 5 |
| Hyderabad | 5 |
| Kolkata | 2 |
| Mumbai | 6 |
| Pune | 4 |
dtype: int64

Q3 - Subscribers with ROW_NUMBER() = 1, per City:
| city | |
|---|---:|
| Bengaluru | 1 |
| Chennai | 1 |
| Delhi | 1 |
| Hyderabad | 1 |
| Kolkata | 1 |
| Mumbai | 1 |
| Pune | 1 |
dtype: int64

Q3 - Kolkata's, First Four Rows:
| Index | subscriber_id | city | total | rnk | dense_rnk | row_num |
|---:|---|---|---:|---:|---:|---:|
| 1425 | TP00074 | Kolkata | 6876.0 | 1 | 1 | 1 |
| 1426 | TP00917 | Kolkata | 6876.0 | 1 | 1 | 2 |
| 1427 | TP00143 | Kolkata | 6582.0 | 3 | 2 | 3 |
| 1428 | TP01355 | Kolkata | 6582.0 | 3 | 2 | 4 |

*** I would use "ROW_NUMBER()" WINDOW function for "top spender per city". The Other 2 WINDOW functions "RANK, DENSE_RANK" would give Wrong list for the Same Values or a Tie among the 2 Subscribers(E.g: Kolkata).


Q4 - Running Total for the Subscriber TP00010:
| Index | recharge_id | recharge_date | amount_inr | running_total |
|---:|---|---|---:|---:|
| 0 | R000053 | 2025-10-15 | 498.0 | 498.0 |
| 1 | R000055 | 2025-12-15 | 498.0 | 996.0 |
| 2 | R000056 | 2026-01-15 | 498.0 | 1494.0 |
| 3 | R000057 | 2026-02-15 | 498.0 | 1992.0 |
| 4 | R000058 | 2026-03-13 | 498.0 | 2490.0 |


## A4. SQL Queries Execution using a Python Script

1. I have prepared "a3_run_queries.py" python script to run/execute the queries.sql file which consists of 4 SQL queries in a single go/click through the Python setup.
2. The "a3_run_queries.py" python script file is available in the Repository along with other Part-A files.



## Part B



## Part C



## Part D



## Limitations and Next Steps



