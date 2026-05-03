import os
import json
import joblib
import pandas as pd
from datetime import datetime, date


MODEL_PATH = os.path.join(os.path.dirname(__file__), "noshow_model.pkl")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "noshow_features.json")

HIGH_RISK_THRESHOLD = 0.65
MEDIUM_RISK_THRESHOLD = 0.4


def risk_label_from_probability(probability):
    if probability >= HIGH_RISK_THRESHOLD:
        return "High"
    if probability >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


def get_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def get_feature_list():
    if not os.path.exists(FEATURES_PATH):
        return None
    with open(FEATURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else None


def normalize_features(raw_features):
    out = {
        "age": int(raw_features.get("age", 30) or 30),
        "lead_time_days": int(raw_features.get("lead_time_days", 0) or 0),
        "scheduled_weekday": int(raw_features.get("scheduled_weekday", 0) or 0),
        "appointment_weekday": int(raw_features.get("appointment_weekday", 0) or 0),
        "appointment_hour": int(raw_features.get("appointment_hour", 10) or 10),
        "prev_appt_count": int(raw_features.get("prev_appt_count", 0) or 0),
        "prev_noshow_count": int(raw_features.get("prev_noshow_count", 0) or 0),
        "prev_noshow_rate": float(raw_features.get("prev_noshow_rate", 0.0) or 0.0),
        "sms_received": int(raw_features.get("sms_received", 0) or 0),
    }

    out["age"] = max(0, min(120, out["age"]))
    out["lead_time_days"] = max(0, min(365, out["lead_time_days"]))
    out["appointment_hour"] = max(0, min(23, out["appointment_hour"]))
    out["prev_appt_count"] = max(0, out["prev_appt_count"])
    out["prev_noshow_count"] = max(0, out["prev_noshow_count"])
    out["prev_noshow_rate"] = max(0.0, min(1.0, out["prev_noshow_rate"]))
    out["sms_received"] = 1 if out["sms_received"] else 0
    return out


def predict_noshow(raw_features):
    features = normalize_features(raw_features)
    model = get_model()
    feature_list = get_feature_list()

    if model is not None:
        if not feature_list:
            feature_list = list(features.keys())
        row = {f: features.get(f, 0) for f in feature_list}
        input_df = pd.DataFrame([row], columns=feature_list)
        probability = float(model.predict_proba(input_df)[0][1])
        return {
            "ok": True,
            "risk_probability": round(probability, 4),
            "risk_label": risk_label_from_probability(probability),
            "source": "ml_model",
            "features_used": features,
        }

    # Fallback heuristic when trained model is not present.
    score = 0.0
    score += min(features["lead_time_days"] / 30.0, 1.0) * 0.25
    score += min(features["prev_noshow_rate"], 1.0) * 0.35
    score += min(features["prev_noshow_count"] / 5.0, 1.0) * 0.2
    score += (0.08 if features["age"] < 20 else 0.0)
    score += (0.05 if features["appointment_hour"] < 9 else 0.0)
    score -= (0.08 if features["sms_received"] == 1 else 0.0)

    probability = max(0.05, min(0.95, round(score, 4)))
    return {
        "ok": True,
        "risk_probability": probability,
        "risk_label": risk_label_from_probability(probability),
        "source": "heuristic_fallback",
        "features_used": features,
    }


def build_noshow_features_from_hms(patient_profile, appointment_date, appointment_time, prev_appt_count, prev_noshow_count):
    age = getattr(patient_profile, "age", 30) if patient_profile else 30
    prev_noshow_rate = (
        (float(prev_noshow_count) / float(prev_appt_count))
        if prev_appt_count > 0
        else 0.0
    )

    today = date.today()
    if isinstance(appointment_date, date):
        lead_time_days = max(0, (appointment_date - today).days)
        appt_weekday = appointment_date.weekday()
    else:
        lead_time_days = 0
        appt_weekday = datetime.today().weekday()

    appt_hour = getattr(appointment_time, "hour", 10) if appointment_time else 10

    return normalize_features(
        {
            "age": age,
            "lead_time_days": lead_time_days,
            "scheduled_weekday": today.weekday(),
            "appointment_weekday": appt_weekday,
            "appointment_hour": appt_hour,
            "prev_appt_count": prev_appt_count,
            "prev_noshow_count": prev_noshow_count,
            "prev_noshow_rate": prev_noshow_rate,
            "sms_received": 0,
        }
    )
