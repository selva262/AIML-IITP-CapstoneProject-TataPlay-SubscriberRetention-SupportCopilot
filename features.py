"""
====================================================================
Capstone Project: Tata Play Subscriber Retention & Support Copilot
====================================================================

features.py  --  Shared Feature Building, Splitting and Preprocessing
======================================================================
Used by : Every Part-B script and (later) copilot.py in Part-D.
Purpose : One Single place that defines
            - Which Columns are Features, which is the Target, which are Leaky
            - How Recharge Features are computed as of 2026-03-31
            - The 60/20/20 ratio train/validation/test split
            - The preprocessing (Impute + Scale + One-Hot Encoding) and Model Pipeline
Reads   : data/clean/subscribers.csv, data/clean/recharges.csv (via load_modelling_table)
Writes  : Nothing(Prints the Results to the Terminal, Manually Copy-Paste the Output to README.md)
Note    : Run Scripts from the Project Root so that "Import Features" Works.
"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# =============================================================================
# 1. BASIC CONFIGURATION
# =============================================================================
SNAPSHOT = pd.Timestamp("2026-03-31")   # The Day we "Stand On" when predicting
RANDOM_STATE = 42                       # For Reproducible train/val/test Splits and Model Training

TARGET = "churned"                      # The Column using we are trying to Predict (1=churned, 0=retained)

# Features that are used to Predict the Target. They are all in the Clean Subscribers table, except for the Three Recharge features which are computed from the Clean Recharges Table.
NUMERIC_FEATURES = [
    "tenure_months", "age", "add_on_count", "monthly_recharge_inr",
    "hours_watched_per_week", "hd_hours_per_week", "sports_hours_per_week",
    "channels_watched", "support_calls_90d",
    "n_success_6m", "n_failed_6m", "recency_days",
]
CATEGORICAL_FEATURES = ["city", "plan_id", "payment_mode", "auto_renew"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Columns that do NOT exist at Prediction Time (See the data dictionary, "Known when" column).
# They must never be used as Features.
LEAKY_COLUMNS = ["closure_request_logged", "next_cycle_recharge_inr"]


# =============================================================================
# 2. FEATURES BUILDING 
# =============================================================================
def compute_recharge_features(subs, rech, snapshot=SNAPSHOT):
    """Add n_success_6m, n_failed_6m and recency_days to a subscribers table.

    - n_success_6m : Number of Successful Recharges up to the Snapshot date
    - n_failed_6m  : Number of Failed Recharges up to the Snapshot date
    - recency_days : Days from the Snapshot to the Last Successful Recharge
                     (stays missing/NaN if the subscriber has none)
    Subscribers with no recharge rows get 0 for both Counts.

    The Same Function is used in Part-D for a Single Subscriber, so it must
    work for any Subscribers/Recharges pair of DataFrames.

    Args:
        subs: DataFrame with at least a subscriber_id Column.
        rech: DataFrame with subscriber_id, recharge_date, status Columns.
        snapshot: The "as of" date (default 2026-03-31).

    Returns:
        A Copy of subs with the Three new Columns added.
    """

    rech = rech.copy()
    rech["recharge_date"] = pd.to_datetime(rech["recharge_date"])
    rech = rech[rech["recharge_date"] <= snapshot]        # Nothing after the Snapshot

    success = rech[rech["status"] == "success"]
    failed = rech[rech["status"] == "failed"]

    # Compute the Three Features by Grouping on subscriber_id
    n_success = success.groupby("subscriber_id").size()
    n_failed = failed.groupby("subscriber_id").size()
    last_success = success.groupby("subscriber_id")["recharge_date"].max()

    out = subs.copy()
    out["n_success_6m"] = out["subscriber_id"].map(n_success).fillna(0).astype(int)
    out["n_failed_6m"] = out["subscriber_id"].map(n_failed).fillna(0).astype(int)
    out["recency_days"] = (snapshot - out["subscriber_id"].map(last_success)).dt.days
    return out


def load_modelling_table():
    """Read the clean Part-A Tables and return as One Row per Subscriber with all Features.

    Returns:
        DataFrame of 2,400 rows: The Clean Subscriber Columns plus the Three
        Recharge Features.
    """

    subs = pd.read_csv("data/clean/subscribers.csv")
    rech = pd.read_csv("data/clean/recharges.csv")
    return compute_recharge_features(subs, rech)


# =============================================================================
# 3. SPLITTING THE DATASET
# =============================================================================
def make_splits(df):
    """Split the Modelling table as Three-Way Split into train / validation / test (60/20/20).

    Step-1: Hold out 20% as the TEST set.
    Step-2: Split the remaining 80% into train (75%) and validation (25%),
            which gives 60% / 20% / 20% of All Rows.
    Both Steps are Stratified on the Target so every Set has the same
    Churn rate, and use random_state=42 so results are Reproducible.

    Args:
        df: The Modelling Table from load_modelling_table().

    Returns:
        (train_df, val_df, test_df): Full DataFrames (all columns kept,
        including subscriber_id and the leaky columns).
    """

    # Step-1: Split into train/validation/test sets - Hold out 20% as the TEST set
    rest_df, test_df = train_test_split(
        df, test_size=0.2, stratify=df[TARGET], random_state=RANDOM_STATE)
    # Step-2: Split the Rest(remaining) 80% into train/validation sets
    train_df, val_df = train_test_split(
        rest_df, test_size=0.25, stratify=rest_df[TARGET], random_state=RANDOM_STATE)
    return train_df, val_df, test_df


# =============================================================================
# 4. PREPROCESSING AND MODEL PIPELINE
# =============================================================================
def build_preprocessor(numeric=None, categorical=None):
    """Build the ColumnTransformer (not yet fitted).

    Numeric columns : Median Imputation, then Standard Scaling.
    Categorical     : Most-Frequent Imputation, then One-Hot Encoding
                      (Unseen Categories are ignored instead of Crashing).

    Args:
        numeric: List of Numeric Column Names (default NUMERIC_FEATURES).
        categorical: List of Categorical Column Names (default CATEGORICAL_FEATURES).
    """

    numeric = NUMERIC_FEATURES if numeric is None else numeric
    categorical = CATEGORICAL_FEATURES if categorical is None else categorical

    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, numeric),
        ("cat", categorical_pipe, categorical),
    ])


def make_model_pipeline(estimator, numeric=None, categorical=None):
    """Bundle the Preprocessor and a Model into one Pipeline.

    The Steps are named "prep" and "model" in every Pipeline of this project,
    so later code can always find them with pipeline.named_steps["prep"].

    Args:
        estimator: Any scikit-learn Classifier or Regressor.
    """

    return Pipeline([("prep", build_preprocessor(numeric, categorical)),
                     ("model", estimator)])