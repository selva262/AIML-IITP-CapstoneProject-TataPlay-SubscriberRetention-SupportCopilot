"""
====================================================================
Capstone Project: Tata Play Subscriber Retention & Support Copilot
====================================================================

b1_frame_split_leakage.py  --  Part-B, Task-1 & Task-2
====================================================
Purpose : (1) Report the Class Balance for the Framing Table,
          (2) Build the Modelling Table and Report the recency_days gap,
          (3) Make the 60/20/20 split and Report its Sizes,
          (4) PROVE the damage caused by Leaky Columns.
Reads   : data/clean/*.csv (through features.py)
Writes  : Nothing(Prints the Results to the Terminal, Manually Copy-Paste the Output to README.md)
Run     : python b1_frame_split_leakage.py
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

import features as ft


def report_class_balance(df):
    """Print how many subscribers churned (the class balance)."""

    # Calculate the number of Churned Subscribers and the Total number of Subscribers
    n, churned = len(df), int(df[ft.TARGET].sum())
    print(f"class balance: {churned} of {n} churned ({churned / n * 100:.2f}%)")


def report_split(train_df, val_df, test_df):
    """Print the size and number of churners in each of the three sets."""

    # Calculate the Size and number of Churners in each Set
    for name, part in [("train", train_df), ("validation", val_df), ("test", test_df)]:
        print(f"{name:<11}: {len(part)} rows, {int(part[ft.TARGET].sum())} churners")


def fit_and_score(train_df, val_df, numeric, categorical):
    """Train a random forest on train rows, score it on validation rows.

    Args:
        train_df, val_df: the train and validation DataFrames.
        numeric, categorical: the feature column lists to use.

    Returns:
        (accuracy, churn-class F1) on the validation set.
    """

    # Build a Model Pipeline with the Specified Features and Fit it to the Train Set
    cols = numeric + categorical
    model = ft.make_model_pipeline(
        RandomForestClassifier(n_estimators=100, random_state=ft.RANDOM_STATE),
        numeric, categorical)
    model.fit(train_df[cols], train_df[ft.TARGET])
    pred = model.predict(val_df[cols])
    return (accuracy_score(val_df[ft.TARGET], pred),
            f1_score(val_df[ft.TARGET], pred, pos_label=1))


def leakage_experiment(train_df, val_df):
    """Compare a model WITH the two leaky columns against one WITHOUT them.

    closure_request_logged is treated as categorical and
    next_cycle_recharge_inr as numeric. Its blanks are left blank and
    handled by the same median imputer inside the pipeline (filling them
    with 0 would turn the column into a perfect copy of the label).
    """

    # Fit and Score the Two Models (WITH and WITHOUT the Leaky Columns)
    clean_acc, clean_f1 = fit_and_score(
        train_df, val_df, ft.NUMERIC_FEATURES, ft.CATEGORICAL_FEATURES)
    leaky_acc, leaky_f1 = fit_and_score(
        train_df, val_df,
        ft.NUMERIC_FEATURES + ["next_cycle_recharge_inr"],
        ft.CATEGORICAL_FEATURES + ["closure_request_logged"])

    print("\nLeakage experiment (validation set, random forest 100 trees):")
    print(f"  WITH leaky columns   : Accuracy {leaky_acc:.3f}  Churn F1 {leaky_f1:.3f}")
    print(f"  WITHOUT leaky columns: Accuracy {clean_acc:.3f}  Churn F1 {clean_f1:.3f}")


def main():
    """Run Tasks 1 and 2 of Part B."""

    # Load the Framing Table, Report Class Balance, and Report recency_days Gap
    df = ft.load_modelling_table()
    report_class_balance(df)
    print("recency_days missing for:", int(df["recency_days"].isna().sum()), "subscribers")
    print("n_success_6m total:", int(df["n_success_6m"].sum()),
          "| n_failed_6m total:", int(df["n_failed_6m"].sum()))

    train_df, val_df, test_df = ft.make_splits(df)
    print()
    report_split(train_df, val_df, test_df)
    leakage_experiment(train_df, val_df)


if __name__ == "__main__":
    main()