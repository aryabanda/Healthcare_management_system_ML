import os
import math
import joblib
import pandas as pd


MODEL_PATH = os.path.join(os.path.dirname(__file__), "readmission_model.pkl")
HIGH_RISK_THRESHOLD = 0.65
MEDIUM_RISK_THRESHOLD = 0.4

# Keep the same feature schema expected by the training pipeline.
MODEL_FEATURES = [
    "age",
    "gender",
    "time_in_hospital",
    "num_medications",
    "num_lab_procedures",
    "number_inpatient",
    "active_med_count",
    "comorbidity_score",
    "a1c_abnormal",
]

AGE_BUCKETS = [
    "[0-10]",
    "[10-20]",
    "[20-30]",
    "[30-40]",
    "[40-50]",
    "[50-60]",
    "[60-70]",
    "[70-80]",
    "[80-90]",
    "[90-100]",
]


def age_to_bucket(age_value):
    if age_value is None:
        return "[50-60]"
    try:
        age_int = int(age_value)
    except (TypeError, ValueError):
        return "[50-60]"

    lower = max(0, min(90, int(math.floor(age_int / 10) * 10)))
    upper = lower + 10
    return f"[{lower}-{upper}]"


def get_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def risk_label_from_probability(probability):
    if probability >= HIGH_RISK_THRESHOLD:
        return "High"
    if probability >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


def normalize_features(raw_features):
    normalized = {}
    for key in MODEL_FEATURES:
        normalized[key] = raw_features.get(key)

    normalized["age"] = normalized["age"] or "[50-60]"
    if normalized["age"] not in AGE_BUCKETS:
        normalized["age"] = "[50-60]"

    normalized["gender"] = (normalized["gender"] or "Unknown").strip().capitalize()
    if normalized["gender"] not in ("Male", "Female", "Unknown"):
        normalized["gender"] = "Unknown"

    int_fields = [
        "time_in_hospital",
        "num_medications",
        "num_lab_procedures",
        "number_inpatient",
        "active_med_count",
        "comorbidity_score",
        "a1c_abnormal",
    ]
    for field in int_fields:
        try:
            normalized[field] = int(normalized.get(field, 0))
        except (TypeError, ValueError):
            normalized[field] = 0

    normalized["a1c_abnormal"] = 1 if normalized["a1c_abnormal"] else 0
    return normalized


def predict_readmission(raw_features):
    features = normalize_features(raw_features)
    model = get_model()
    if model is None:
        # Fallback heuristic so HMS still works when model file is absent.
        score = 0.0
        comorbidity_norm = min(features["comorbidity_score"] / 6.0, 1.0)
        score += min(features["time_in_hospital"] / 14.0, 1.0) * 0.18
        score += min(features["num_medications"] / 20.0, 1.0) * 0.12
        score += min(features["num_lab_procedures"] / 120.0, 1.0) * 0.1
        score += min(features["number_inpatient"] / 5.0, 1.0) * 0.2
        score += min(features["active_med_count"] / 10.0, 1.0) * 0.1
        # Make comorbidity impact stronger and non-linear at higher burden.
        score += comorbidity_norm * 0.22
        score += (comorbidity_norm ** 2) * 0.12
        score += 0.03 if features["a1c_abnormal"] == 1 else 0.0
        score += 0.03 if features["age"] in ("[70-80]", "[80-90]", "[90-100]") else 0.0
        probability = max(0.05, min(0.95, round(score, 4)))
        return {
            "ok": True,
            "prediction": 1 if probability >= 0.5 else 0,
            "risk_probability": probability,
            "risk_label": risk_label_from_probability(probability),
            "features_used": features,
            "source": "heuristic_fallback",
        }

    payload = pd.DataFrame([features], columns=MODEL_FEATURES)
    prediction = int(model.predict(payload)[0])
    probability = float(model.predict_proba(payload)[0][1])

    return {
        "ok": True,
        "prediction": prediction,
        "risk_probability": round(probability, 4),
        "risk_label": risk_label_from_probability(probability),
        "features_used": features,
        "source": "ml_model",
    }


def build_features_from_hms(patient_profile, appointment, treatment_count, appointment_count=0):
    age_bucket = age_to_bucket(getattr(patient_profile, "age", None))
    gender_value = getattr(patient_profile, "gender", None)

    return normalize_features(
        {
            "age": age_bucket,
            "gender": gender_value or "Unknown",
            "time_in_hospital": 3,
            "num_medications": max(1, treatment_count),
            "num_lab_procedures": 20 + (treatment_count * 5),
            # Use appointment history from DB as a proxy for prior inpatient burden.
            "number_inpatient": max(0, appointment_count - 1),
            "active_med_count": min(10, max(1, treatment_count)),
            "comorbidity_score": min(6, max(1, treatment_count // 2)),
            "a1c_abnormal": 0,
        }
    )
