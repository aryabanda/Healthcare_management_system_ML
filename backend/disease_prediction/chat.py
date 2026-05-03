import os
import csv
import re
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
from rapidfuzz import process, fuzz

# -----------------------------
# LOAD DATASETS
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "Data")

TRAINING_CANDIDATES = [
    os.path.join(BASE_DIR, "Training.csv"),
    os.path.join(DATA_DIR, "Training.csv"),
]
TESTING_CANDIDATES = [
    os.path.join(BASE_DIR, "Testing.csv"),
    os.path.join(DATA_DIR, "Testing.csv"),
]
DOC_CONSULT_PATH = os.path.join(DATA_DIR, "doc_consult.csv")


def _first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"None of these files exist: {paths}")


training = pd.read_csv(_first_existing(TRAINING_CANDIDATES))
testing = pd.read_csv(_first_existing(TESTING_CANDIDATES))

# remove unwanted columns
training = training.loc[:, ~training.columns.str.contains('^Unnamed')]

# separate features and target
x = training.drop("prognosis", axis=1)
y = training["prognosis"]

cols = x.columns

# -----------------------------
# ENCODE LABELS
# -----------------------------
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

# -----------------------------
# TRAIN MODEL
# -----------------------------
clf = DecisionTreeClassifier()
clf.fit(x, y)

# -----------------------------
# REDUCED DATA
# -----------------------------
reduced_data = training.groupby(training['prognosis']).max()

# -----------------------------------------
# AUTO BASE MAP (FROM DATASET)
# -----------------------------------------
def generate_base_map(cols):
    base_map = {}
    generic_words = {
        "pain", "body", "skin", "history", "movement", "discomfort",
        "abnormality", "changes", "disturbances", "irregularities",
        "loss", "gain", "disease", "problem", "problems"
    }

    for col in cols:
        clean = col.replace("_", " ")
        base_map[clean] = col

        words = clean.split()
        # Last-word aliases are only safe for specific, non-generic words.
        last_word = words[-1]
        if len(last_word) >= 5 and last_word not in generic_words:
            base_map[last_word] = col

    return base_map


BASE_MAP = generate_base_map(cols)

# -----------------------------------------
# CUSTOM HUMAN-FRIENDLY MAP
# -----------------------------------------
CUSTOM_MAP = {
    "fever": "mild_fever",
    "temperature": "mild_fever",
    "cold": "continuous_sneezing",
    "runny nose": "continuous_sneezing",
    "blocked nose": "continuous_sneezing",
    "cough": "cough",
    "headache": "headache",
    "head pain": "headache",
    "body pain": "body_ache",
    "body pains": "body_ache",
    "body ache": "body_ache",
    "body aches": "body_ache",
    "stomach pain": "abdominal_pain",
    "vomit": "vomiting",
    "nausea": "nausea",
    "tired": "fatigue",
    "weakness": "fatigue",
    "breathing problem": "breathlessness",
    "heart pain": "chest_pain",
    "chest pain": "chest_pain",
    "sweating": "sweating"
}

# FINAL LOOKUP
SYMPTOM_LOOKUP = {**BASE_MAP, **CUSTOM_MAP}
LOOKUP_KEYS = list(SYMPTOM_LOOKUP.keys())

# -----------------------------------------
# NLP FUNCTIONS
# -----------------------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_negated_keys(text):
    """
    Identify keys that are negated in the sentence, e.g.:
    - no fever
    - not having cough
    - without chest pain
    """
    negated = set()
    patterns = [
        r"\bno\s+([a-z\s]{2,30})",
        r"\bwithout\s+([a-z\s]{2,30})",
        r"\bnot\s+(?:having|have|feeling)\s+([a-z\s]{2,30})",
    ]
    breakers = {"but", "and", "or"}
    for pat in patterns:
        for m in re.findall(pat, text):
            phrase = m.strip()
            tokens = []
            for tok in phrase.split():
                if tok in breakers:
                    break
                tokens.append(tok)
                if len(tokens) >= 4:
                    break
            if tokens:
                negated.add(" ".join(tokens))
    return negated


def fuzzy_extract_candidates(text):
    """
    Fuzzy-match 1-3 gram tokens against lookup keys to catch typos
    like 'hve cold' -> 'cold', 'fevr' -> 'fever'.
    """
    tokens = [t for t in text.split() if len(t) > 2]
    candidates = set()

    ngrams = []
    for n in (1, 2, 3):
        for i in range(0, max(0, len(tokens) - n + 1)):
            ngrams.append(" ".join(tokens[i:i+n]))

    for gram in ngrams:
        best = process.extractOne(
            gram,
            LOOKUP_KEYS,
            scorer=fuzz.WRatio,
            score_cutoff=90 if len(gram) > 4 else 95
        )
        if best:
            key = best[0]
            candidates.add(SYMPTOM_LOOKUP[key])
    return candidates


def extract_symptoms(text):
    text = normalize_text(text)
    found = set()
    negated_phrases = detect_negated_keys(text)
    negated_values = set()

    # Map negated phrases to symptom keys/values.
    for key, val in SYMPTOM_LOOKUP.items():
        if any(re.search(r"\b" + re.escape(key) + r"\b", phrase) for phrase in negated_phrases):
            negated_values.add(val)

    # Phrase matching with word boundaries to avoid accidental substrings.
    for key, val in SYMPTOM_LOOKUP.items():
        if len(key) <= 3:
            continue
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, text):
            # Skip if the exact key appears in a negated phrase.
            if val in negated_values:
                continue
            found.add(val)

    # Fuzzy extraction for typo tolerance.
    fuzzy_found = fuzzy_extract_candidates(text)
    for val in fuzzy_found:
        if val in negated_values:
            continue
        found.add(val)

    return list(found)


def extract_duration(text):
    match = re.search(r'(\d+)\s*(day|days|week|weeks)', text.lower())

    if match:
        num = int(match.group(1))
        if "week" in match.group(2):
            num *= 7
        return num

    return 1


def symptoms_to_vector(symptoms):
    vector = [0] * len(cols)

    for s in symptoms:
        if s in cols:
            vector[list(cols).index(s)] = 1

    return vector


def estimate_severity(symptoms, days):
    score = len(symptoms) * days

    if score <= 3:
        return "Mild"
    elif score <= 7:
        return "Moderate"
    else:
        return "Severe - Consult doctor"


def rank_diseases_by_symptoms(symptoms):
    """
    Rank diseases by symptom overlap against reduced_data.
    Returns list of dicts: [{disease, score, matched_count}, ...]
    """
    if not symptoms:
        return []

    symptom_set = set(symptoms)
    rankings = []

    for disease in reduced_data.index:
        row = reduced_data.loc[disease]
        disease_symptoms = set(row[row > 0].index.tolist())
        if not disease_symptoms:
            continue

        intersection = symptom_set.intersection(disease_symptoms)
        union = symptom_set.union(disease_symptoms)
        if not union:
            continue

        jaccard = len(intersection) / len(union)
        coverage = len(intersection) / max(1, len(symptom_set))
        score = 0.7 * coverage + 0.3 * jaccard

        rankings.append({
            "disease": disease,
            "score": round(float(score), 4),
            "matched_count": len(intersection),
        })

    rankings.sort(key=lambda d: (d["score"], d["matched_count"]), reverse=True)
    return rankings


# -----------------------------------------
# DIRECT TEXT PREDICTION
# -----------------------------------------
def predict_from_text(text):
    symptoms = extract_symptoms(text)
    days = extract_duration(text)

    severity = estimate_severity(symptoms, days)
    rankings = rank_diseases_by_symptoms(symptoms)
    top3 = rankings[:3]

    if len(symptoms) < 2:
        disease = "Insufficient symptoms"
        advice = "Please provide at least 2-3 symptoms for better prediction."
    elif not top3:
        disease = "Uncertain"
        advice = "Symptoms are not specific enough. Add more symptoms."
    elif top3[0]["score"] < 0.35:
        disease = "Uncertain"
        advice = "Confidence is low. Add more specific symptoms."
    elif len(top3) > 1 and (top3[0]["score"] - top3[1]["score"]) < 0.08:
        disease = "Uncertain"
        advice = "Top matches are too close. Add one or two more symptoms."
    else:
        disease = top3[0]["disease"]
        advice = "You can add more symptoms for a better estimate."

    return {
        "type": "text_result",
        "input": text,
        "symptoms_extracted": symptoms,
        "duration_days": days,
        "predicted_disease": disease,
        "severity": severity,
        "top_matches": top3,
        "advice": advice,
    }


# -----------------------------------------
# TREE-BASED CHAT SYSTEM (UNCHANGED)
# -----------------------------------------
tree_state = {
    "node": 0,
    "symptoms_present": []
}


def print_disease(node):
    node = node[0]
    val = node.nonzero()
    disease = le.inverse_transform(val[0])
    return disease


def start_chat():
    tree_state["node"] = 0
    tree_state["symptoms_present"] = []
    return ask_next_question()


def answer_question(user_answer):
    tree_ = clf.tree_
    node = tree_state["node"]

    feature = tree_.feature[node]
    threshold = tree_.threshold[node]

    if feature != _tree.TREE_UNDEFINED:
        val = 1 if user_answer.lower() == "yes" else 0

        if val <= threshold:
            tree_state["node"] = tree_.children_left[node]
        else:
            symptom_name = cols[feature]
            tree_state["symptoms_present"].append(symptom_name)
            tree_state["node"] = tree_.children_right[node]

        return ask_next_question()
    else:
        return get_result()


def ask_next_question():
    tree_ = clf.tree_
    node = tree_state["node"]

    if tree_.feature[node] != _tree.TREE_UNDEFINED:
        symptom = cols[tree_.feature[node]]
        return {
            "type": "question",
            "question": f"Do you have {symptom.replace('_',' ')} ?"
        }
    else:
        return get_result()


def get_result():
    tree_ = clf.tree_
    node = tree_state["node"]

    present_disease = print_disease(tree_.value[node])
    disease = present_disease[0]

    red_cols = reduced_data.columns
    symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]

    consult = {}
    if os.path.exists(DOC_CONSULT_PATH):
        with open(DOC_CONSULT_PATH, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    try:
                        consult[row[0]] = int(row[1])
                    except ValueError:
                        continue

    consult_msg = "You may consult a doctor"
    if disease in consult and consult[disease] > 50:
        consult_msg = "You should consult a doctor as soon as possible"

    return {
        "type": "result",
        "disease": disease,
        "symptoms_present": tree_state["symptoms_present"],
        "other_symptoms": list(symptoms_given),
        "advice": consult_msg
    }


if __name__ == "__main__":
    user_text = input("Describe your symptoms: ")
    print(predict_from_text(user_text))