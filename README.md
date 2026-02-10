# Log Classification System (NLP)

A production-style, multi-stage log classification system that uses **Natural Language Processing** to automatically categorize system logs from multiple sources. The pipeline combines regex pattern matching, BERT-based embeddings, and an LLM for edge cases.

---

## 📹 Demo Video

Watch a walkthrough of the project: setup, classification pipeline, API, and frontend.

<!-- Embed: replace with your hosted URL if you prefer; local path works when viewing in browser or VS Code -->
[**▶ Watch: Log Classification Demo**](docs/Log_classification_video.mp4)

<video src="docs/Log_classification_video.mp4" controls width="720" title="Log Classification Demo"></video>

*If the video does not render above, open [docs/Log_classification_video.mp4](docs/Log_classification_video.mp4) directly.*

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Retraining the Model](#-retraining-the-model)
- [Documentation](#-documentation)
- [License & Author](#-license--author)

---

## ✨ Features

- **Multi-stage classification**: Regex → BERT (embeddings) → LLM (Groq), with routing by log source.
- **REST API**: Upload CSV or send JSON; get classified results and metrics.
- **Web UI**: Paste logs or upload CSV in the browser and view results in a table.
- **Metrics**: Per-label counts and request latency via `/metrics`.
- **Retraining**: Add new labeled examples and retrain the BERT classifier via API or CLI.
- **Sample data**: Ready-to-use sample logs for testing (see `resources/sample_logs.csv`).

---

## 🏗 Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Log Classification API                 │
                    │                     (FastAPI + Frontend)                   │
                    └───────────────────────────────┬───────────────────────────┘
                                                    │
                    ┌───────────────────────────────▼───────────────────────────┐
                    │                  Multi-Stage Pipeline (classify.py)        │
                    └───────────────────────────────┬───────────────────────────┘
                                                    │
         ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
         │                                          │                                           │
         ▼                                          ▼                                           ▼
┌─────────────────┐                    ┌─────────────────────┐                    ┌─────────────────────┐
│  source ==       │                    │  Regex patterns      │                    │  BERT classifier     │
│  "LegacyCRM"?   │── Yes ────────────►│  (processor_regex)   │── No match ───────►│  (processor_bert)   │
│                 │                    │  User Action,        │                    │  SentenceTransformer│
│                 │── No ─────────────►│  System Notif., etc. │                    │  + LogisticRegression│
└─────────────────┘                    └─────────────────────┘                    └─────────────────────┘
         │                                          │
         │ Yes                                      │ Match
         ▼                                          ▼
┌─────────────────┐                    ┌─────────────────────┐
│  LLM (Groq)     │                    │  Return label         │
│  processor_llm  │                    └─────────────────────┘
│  Workflow Error,│
│  Deprecation   │
└─────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a more detailed breakdown.

---

## 📁 Project Structure

```
Log_classification_system_NLP_Personal_project/
├── server.py                 # FastAPI app: /classify, /classify-json, /metrics, /retrain
├── main.py                   # Optional entry point
├── requirements.txt         # Python dependencies
├── synthetic_logs.csv       # Original training dataset
├── docs/
│   ├── Log_classification_video.mp4   # Demo video
│   └── ARCHITECTURE.md                # Architecture and design notes
├── static/
│   └── index.html           # Web UI: paste logs or upload CSV
├── resources/
│   ├── test.csv             # Minimal test CSV
│   ├── sample_logs.csv      # Sample logs for testing
│   └── output.csv           # Last classification output (written by API)
├── models/
│   └── log_classification_model.pkl  # Trained BERT-era classifier (joblib)
└── training/
    ├── training.ipynb       # Notebook: data load, clustering, regex, BERT training
    ├── classify.py           # Multi-stage pipeline + classify_batch / classify_csv
    ├── processor_regex.py    # Regex-based classifier
    ├── processor_bert.py     # BERT embeddings + Logistic Regression
    ├── processor_llm.py      # Groq LLM for LegacyCRM / edge cases
    ├── retrain.py            # Script to retrain from CSV (source, log_message, target_label)
    └── .env                  # GROQ_API_KEY (not committed)
```

---

## 🔧 Prerequisites & Installation

- **Python**: 3.9+ recommended.
- **Install dependencies**:

```bash
git clone <repository-url>
cd Log_classification_system_NLP_Personal_project
pip install -r requirements.txt
```

---

## ⚙ Configuration

- **Groq API (LLM)**  
  Create `training/.env` with:

  ```
  GROQ_API_KEY=your_groq_api_key_here
  ```

  Get a key at [console.groq.com](https://console.groq.com).

- **Paths**  
  The server and training scripts assume they are run from the project root. Model path: `models/log_classification_model.pkl`.

---

## 🚀 Usage

### 1. Run the API and open the UI

```bash
uvicorn server:app --reload
```

- **Web UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) — paste logs or upload CSV, then view the results table.
- **API docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Classify from the command line (no server)

```bash
# Classify resources/test.csv and write resources/output.csv
cd training
python classify.py
```

### 3. Test with sample logs

- **Upload**: Use `resources/sample_logs.csv` in the web UI or via Postman (POST `/classify` with form-data key `file`).
- **Paste**: Copy the sample lines from the README or from `resources/sample_logs.csv` into the “Paste logs” tab.

---

## 📡 API Reference

| Method | Endpoint         | Description |
|--------|------------------|-------------|
| `GET`  | `/`              | Serve web UI (paste/upload, results table). |
| `POST` | `/classify`      | Upload CSV (`source`, `log_message`). Returns classified CSV. |
| `GET`  | `/classify`      | Download last classified CSV. |
| `POST` | `/classify-json` | JSON body `{ "logs": [ { "source", "log_message" } ] }`. Returns `{ "results": [ { "source", "log_message", "target_label" } ] }`. |
| `GET`  | `/metrics`       | Counts per label, total requests, average latency (ms). |
| `POST` | `/retrain`       | Upload CSV with `source`, `log_message`, `target_label` to merge into dataset and retrain BERT model. |

All responses use standard HTTP status codes. Errors return JSON with a `detail` field when applicable.

---

## 🔄 Retraining the Model

- **Via API**: POST a CSV (columns `source`, `log_message`, `target_label`) to `/retrain` (form-data, key `file`). The server merges with `dataset/labeled_logs.csv` (or seeds from `synthetic_logs.csv` if needed) and retrains the BERT classifier.
- **Via CLI**:

  ```bash
  python -m training.retrain
  ```

  This uses `dataset/labeled_logs.csv` by default. To use another file:

  ```bash
  python -m training.retrain path/to/labeled.csv
  ```

---

## 📚 Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Pipeline design, components, and data flow.
- **Inline comments** — Key logic in `server.py`, `training/classify.py`, `training/processor_*.py`, `training/retrain.py`, and `static/index.html` is commented for maintainability.

---

## 📄 License & Author

This project is for **educational and portfolio use**.  
**Author**: Your Name  
**Last updated**: February 2026
