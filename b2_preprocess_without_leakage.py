"""
====================================================================
Capstone Project: Tata Play Subscriber Retention & Support Copilot
====================================================================

b2_preprocess.py  --  Part-B, Task-3: Preprocess without Leakage
================================================================
Purpose : Fit the preprocessor on TRAINING rows only, then report what it learned.
Reads   : data/clean/*.csv (through features.py)
Writes  : Nothing(Prints the Results to the Terminal, Manually Copy-Paste the Output to README.md)
Run     : python b2_preprocess.py
"""

import numpy as np

import features as ft


def main():
    """Fit the ColumnTransformer on the train set and print the facts the brief asks for."""

    # Load the Modelling Table and Make the 60/20/20 Split
    df = ft.load_modelling_table()
    train_df, val_df, test_df = ft.make_splits(df)

    prep = ft.build_preprocessor()
    prep.fit(train_df[ft.FEATURES])                       # Learns from TRAIN rows only
    train_t = prep.transform(train_df[ft.FEATURES])
    val_t = prep.transform(val_df[ft.FEATURES])           # Transform only, never fit

    # 1. Number of Output Columns
    names = prep.get_feature_names_out()
    print("output columns:", len(names))

    # 2. What the Imputer learned for Age (Median of TRAIN Ages)
    num_pipe = prep.named_transformers_["num"]
    medians = num_pipe.named_steps["impute"].statistics_
    age_idx = ft.NUMERIC_FEATURES.index("age")
    print("median age learned by the imputer:", medians[age_idx])

    # 3. What the Scaler learned for tenure_months vs the full-data Mean
    scaler_mean = num_pipe.named_steps["scale"].mean_
    ten_idx = ft.NUMERIC_FEATURES.index("tenure_months")
    print(f"tenure_months mean: scaler (train only) {scaler_mean[ten_idx]:.2f}"
          f"  vs full data {df['tenure_months'].mean():.2f}")

    # 4. Proof that No Missing Value remains
    print("missing values after transform: train", int(np.isnan(train_t).sum()),
          "| validation", int(np.isnan(val_t).sum()))
    assert not np.isnan(train_t).any() and not np.isnan(val_t).any()
    print("assertion passed: no missing values remain")


if __name__ == "__main__":
    main()