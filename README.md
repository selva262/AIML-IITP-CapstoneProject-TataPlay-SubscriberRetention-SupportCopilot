
# Tata Play Subscriber Retention & Support Copilot

## Overview


## Reproduce


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

Rows: 2415
Exact Duplicate Rows: 15
Distinct subscriber_id: 2400
Blank age: 99
Age outside 10-100: 6
Blank payment_mode: 116
Distinct Raw City Spellings: 22
Distinct Raw auto_renew Spellings: 6
Blank next_cycle_recharge_inr: 516


### **===== Recharges CSV Figures Report =====**

Rows: 13055
Exact Duplicate Rows: 60
Distinct recharge_id: 12995
amount_inr not Plain Numbers: 366
Distinct Raw Status Spellings: 6
Orphan subscriber_id Rows: 10


### A2. Clean the Data & Store it
### A2. Raw data audit

## Part B
## Part C
## Part D
## Limitations and Next Steps
