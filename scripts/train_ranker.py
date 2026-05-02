import json
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "data", "training_pairs.jsonl")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "goal_topic_ranker.pkl")


def load_pairs(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_features(rows):
    X = []
    y = []
    for r in rows:
        feat = f"goal: {r.get('goal', '')} [SEP] topic: {r.get('topic_text', '')}"
        X.append(feat)
        y.append(int(r.get("label", 0)))
    return X, y


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Training data not found: {DATA_PATH}. Run scripts/build_training_data.py first."
        )

    rows = load_pairs(DATA_PATH)
    X_text, y = build_features(rows)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        min_df=2,
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=100000,
    )
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)

    candidates = [
        {"C": 0.5, "solver": "liblinear"},
        {"C": 1.0, "solver": "liblinear"},
        {"C": 2.0, "solver": "liblinear"},
    ]
    best = None
    best_f1 = -1.0
    best_acc = 0.0

    for cfg in candidates:
        model = LogisticRegression(
            max_iter=1500,
            class_weight="balanced",
            solver=cfg["solver"],
            C=cfg["C"],
            random_state=42,
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        cur_f1 = f1_score(y_test, pred)
        cur_acc = accuracy_score(y_test, pred)
        if cur_f1 > best_f1:
            best = model
            best_f1 = cur_f1
            best_acc = cur_acc

    if best is None:
        raise RuntimeError("No model candidate was trained. Check training data and candidates.")

    model = best
    pred = model.predict(X_test)
    acc = best_acc
    f1 = best_f1
    print(f"Validation accuracy: {acc:.4f}")
    print(f"Validation F1: {f1:.4f}")
    print(classification_report(y_test, pred, digits=4))

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(
            {
                "vectorizer": vectorizer,
                "model": model,
                "meta": {
                    "val_accuracy": acc,
                    "val_f1": f1,
                    "num_samples": len(rows),
                },
            },
            f,
        )
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
