"""
Hospital Readmission Prediction
--------------------------------
End-to-end pipeline:
- Load data
- Feature engineering (realistic)
- Train model
- Evaluate
- Predict for new patient
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


# --------------------------------------------------
# 1. Load Data
# --------------------------------------------------
def load_data(path=None):
    if path is None:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, "Data", "diabetic_data.csv")
    df = pd.read_csv(path)

    # Binary target: 1 = readmitted, 0 = not
    df["readmitted"] = df["readmitted"].apply(
        lambda x: 0 if x == "NO" else 1
    )

    # Replace missing placeholders
    df.replace("?", np.nan, inplace=True)

    # Drop columns with more than 40% missing values
    missing_ratio = df.isna().mean()
    cols_to_drop = missing_ratio[missing_ratio > 0.4].index
    df.drop(columns=cols_to_drop, inplace=True)

    # Fill remaining missing values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(df[col].median())

    return df


# --------------------------------------------------
# 2. Feature Engineering (REALISTIC)
# --------------------------------------------------
def engineer_features(df):
    # Medication aggregation
    med_cols = [
        'metformin','repaglinide','nateglinide','chlorpropamide',
        'glimepiride','acetohexamide','glipizide','glyburide',
        'tolbutamide','pioglitazone','rosiglitazone','acarbose',
        'miglitol','troglitazone','tolazamide','examide',
        'citoglipton','insulin'
    ]
    existing_med_cols = [c for c in med_cols if c in df.columns]
    df["active_med_count"] = (df[existing_med_cols] != "No").sum(axis=1)


    # Comorbidity score from diagnoses
    def comorbidity_score(row):
        score = 0
        for d in ["diag_1", "diag_2", "diag_3"]:
            val = str(row[d])
            if val.startswith("4"):      # circulatory
                score += 2
            elif val.startswith("2"):    # diabetes
                score += 1
        return score

    df["comorbidity_score"] = df.apply(comorbidity_score, axis=1)

    # A1C abnormal flag
    if "A1Cresult" in df.columns:
        df["a1c_abnormal"] = df["A1Cresult"].isin([">7", ">8"]).astype(int)
    else:
        # If A1C not available, assume normal (realistic fallback)
        df["a1c_abnormal"] = 0


    # Final realistic feature set
    features = [
        "age",
        "gender",
        "time_in_hospital",
        "num_medications",
        "num_lab_procedures",
        "number_inpatient",
        "active_med_count",
        "comorbidity_score",
        "a1c_abnormal"
    ]

    X = df[features]
    y = df["readmitted"]

    return X, y


# --------------------------------------------------
# 3. Train Model
# --------------------------------------------------
def train_model(X, y):
    categorical_cols = ["age", "gender"]
    numerical_cols = [c for c in X.columns if c not in categorical_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numerical_cols)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    print("\nClassification Report\n")
    print(classification_report(y_test, y_pred))
    print("ROC-AUC:", round(roc_auc_score(y_test, y_prob), 3))

    return pipeline


# --------------------------------------------------
# 4. Predict for a New Patient (REAL LIFE)
# --------------------------------------------------
def predict_new_patient(pipeline):
    new_patient = pd.DataFrame([{
        "age": "[30-40]",
        "gender": "Male",
        "time_in_hospital": 4,
        "num_medications": 5,
        "num_lab_procedures": 100,
        "number_inpatient": 1,
        "active_med_count": 2,
        "comorbidity_score": 3,
        "a1c_abnormal": 1
    }])

    prediction = pipeline.predict(new_patient)[0]
    probability = pipeline.predict_proba(new_patient)[0][1]

    print("\nNew Patient Prediction")
    print("----------------------")
    print("Readmitted:", "YES" if prediction == 1 else "NO")
    print("Risk Probability:", round(probability, 2))


# --------------------------------------------------
# 5. Main Runner
# --------------------------------------------------
if __name__ == "__main__":
    print("Loading data...")
    df = load_data()

    print("Engineering features...")
    X, y = engineer_features(df)

    print("Training model...")
    pipeline = train_model(X, y)

    # Save model
    model_out = os.path.join(os.path.dirname(__file__), "readmission_model.pkl")
    joblib.dump(pipeline, model_out)
    print(f"\nModel saved as {model_out}")

    # Predict example patient
    predict_new_patient(pipeline)
