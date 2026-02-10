"""
Retrain the BERT-based log classifier from a CSV of labeled examples.

CSV must have columns: source, log_message, target_label
(optional: timestamp, complexity — will be dropped if present)

Usage:
  python -m training.retrain [path_to_csv]
  Default path: dataset/labeled_logs.csv (relative to project root)
"""

import sys
from pathlib import Path

import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "log_classification_model.pkl"
DEFAULT_DATA_PATH = PROJECT_ROOT / "dataset" / "labeled_logs.csv"


def run_retrain(csv_path: Path) -> str:
    """
    Load CSV, encode log_message with SentenceTransformer, train LogisticRegression, save model.
    Returns a short status message.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    for col in ["source", "log_message", "target_label"]:
        if col not in df.columns:
            raise ValueError(f"CSV must contain column: {col}")

    # Drop optional columns if present
    for drop in ["timestamp", "complexity", "regex_labels", "cluster"]:
        if drop in df.columns:
            df = df.drop(columns=[drop])

    df = df.dropna(subset=["log_message", "target_label"])
    if len(df) == 0:
        raise ValueError("No rows with valid log_message and target_label")

    # Same encoder as processor_bert so the saved classifier is compatible
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(df["log_message"].tolist())
    X = embeddings
    y = df["target_label"]

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)  # Overwrites the model used by processor_bert

    return f"Model saved to {MODEL_PATH} (trained on {len(df)} rows)"


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_PATH
    path = Path(path)
    try:
        msg = run_retrain(path)
        print(msg)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
