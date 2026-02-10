# Architecture: Log Classification System

This document describes the design and flow of the log classification pipeline and API.

---

## 1. Overview

The system classifies free-text log messages into a fixed set of labels (e.g. User Action, System Notification, HTTP Status, Critical Error, Security Alert, etc.). It uses a **multi-stage pipeline** so that:

- **Regex** handles high-confidence, well-defined patterns (fast, no model load).
- **BERT** (sentence embeddings + Logistic Regression) handles the bulk of non-legacy logs that don’t match regex.
- **LLM** (Groq) handles **LegacyCRM** logs and edge cases (e.g. Workflow Error, Deprecation Warning).

---

## 2. Pipeline Flow

1. **Input**: `(source, log_message)` — e.g. `("ModernCRM", "User User123 logged in.")`.
2. **Routing**:
   - If `source == "LegacyCRM"` → call **LLM** only; return its label.
   - Else → try **Regex**; if no match → call **BERT**; return the chosen label.
3. **Output**: A single string label per log (e.g. `"User Action"`, `"System Notification"`).

Batch classification is implemented by running this flow for each log in sequence (see `classify_batch` in `classify.py`).

---

## 3. Components

### 3.1 Regex stage (`training/processor_regex.py`)

- **Role**: Fast pattern matching for known formats.
- **Input**: Raw `log_message` string.
- **Output**: Label or `None` (no match).
- **Patterns**: E.g. user login/logout, backup start/end, system update, file upload, disk cleanup, reboot, account creation. All defined in a single dict mapping regex → label.

### 3.2 BERT stage (`training/processor_bert.py`)

- **Role**: Classify messages that don’t match regex, using semantic embeddings.
- **Model**: SentenceTransformer `all-MiniLM-L6-v2` (384-dim embeddings).
- **Classifier**: Logistic Regression loaded from `models/log_classification_model.pkl`.
- **Input**: `log_message` string.
- **Output**: Label; or `"Unclassified"` if max probability &lt; 0.5.
- **Training**: See `training/training.ipynb` — encode messages, train Logistic Regression, save with joblib.

### 3.3 LLM stage (`training/processor_llm.py`)

- **Role**: Handle LegacyCRM and ambiguous/edge-case logs.
- **API**: Groq (e.g. `llama-3.1-8b-instant`).
- **Input**: `log_message` string.
- **Output**: One of the instructed categories (e.g. Workflow Error, Deprecation Warning, Unclassified).
- **Config**: `GROQ_API_KEY` in `training/.env`.

### 3.4 Orchestrator (`training/classify.py`)

- **Role**: Implement the routing and fallback logic above.
- **Functions**:
  - `classify_logs(source, log_msg)` — single log.
  - `classify_batch(logs)` — list of `(source, log_message)` → list of `(source, log_message, label)`.
  - `classify_csv(input_file)` — read CSV, run `classify_batch`, write `resources/output.csv`.

---

## 4. API and Frontend

### 4.1 Server (`server.py`)

- **Framework**: FastAPI.
- **Endpoints**:
  - `GET /` — Serves `static/index.html` (web UI).
  - `POST /classify` — CSV upload (form-data `file`); returns classified CSV.
  - `GET /classify` — Download last written `resources/output.csv`.
  - `POST /classify-json` — JSON `{ "logs": [ { "source", "log_message" } ] }`; returns `{ "results": [ { "source", "log_message", "target_label" } ] }`.
  - `GET /metrics` — Aggregated counts per label and average request latency (in-memory).
  - `POST /retrain` — CSV upload (source, log_message, target_label); merge into dataset and run BERT retrain.

- **Metrics**: Updated on each `/classify` and `/classify-json` call (label counts, total requests, total latency). Served as JSON from `/metrics`.

### 4.2 Frontend (`static/index.html`)

- **Tabs**: “Paste logs” (lines of `source,log_message`) and “Upload CSV”.
- **Paste**: Parses lines, sends JSON to `/classify-json`, renders results in a table.
- **Upload**: Sends file to `/classify`, parses returned CSV, renders same table.
- **Metrics**: Optional block that fetches and displays `/metrics` when available.

---

## 5. Retraining

- **Data**: CSV with `source`, `log_message`, `target_label`. Optional columns (e.g. timestamp) are dropped.
- **Merge**: New rows are appended to `dataset/labeled_logs.csv`. If that file doesn’t exist, it can be seeded from `synthetic_logs.csv` (see `server.py` `/retrain` and `training/retrain.py`).
- **Process**: Load merged CSV → encode `log_message` with the same SentenceTransformer → train Logistic Regression → save to `models/log_classification_model.pkl`.
- **Invocation**: Via `POST /retrain` (file upload) or CLI `python -m training.retrain [path_to_csv]`.

---

## 6. File and Path Conventions

- **Project root**: Where `server.py` and `training/` live; recommended working directory for `uvicorn server:app` and `python -m training.retrain`.
- **Model**: `models/log_classification_model.pkl` (used by `processor_bert.py` and written by `retrain.py`).
- **Output**: Last classification CSV written to `resources/output.csv` by the server and by `classify_csv`.
- **Secrets**: `training/.env` for `GROQ_API_KEY`; not committed.

This architecture keeps the pipeline modular and makes it straightforward to add new regex patterns, change the LLM prompt, or retrain the BERT classifier on new data.
