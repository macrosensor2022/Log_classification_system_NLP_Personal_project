"""
FastAPI server for the log classification system.

Endpoints:
- GET  /              : Frontend (paste logs or upload CSV, see results table).
- POST /classify      : Upload CSV → returns classified CSV.
- GET  /classify      : Download last classified CSV.
- POST /classify-json : JSON body { "logs": [{ "source", "log_message" }] } → { "results": [...] }.
- GET  /metrics       : Label counts and request latency stats.
- POST /retrain       : Upload CSV (source, log_message, target_label) to add data and retrain BERT model.
"""

from pathlib import Path
import sys
import time
from collections import defaultdict

import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException, Body
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Allow importing from the training module without a Python package
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "training"))
from classify import classify_batch  # type: ignore

app = FastAPI(title="Log Classification API")

# ---------- Metrics (in-memory) ----------
_metrics = {
    "by_label": defaultdict(int),
    "total_requests": 0,
    "total_latency_ms": 0.0,
}


def _record_metrics(labels: list, latency_ms: float):
    _metrics["total_requests"] += 1
    _metrics["total_latency_ms"] += latency_ms
    for label in labels:
        _metrics["by_label"][label] += 1


@app.post("/classify")
async def classify_logs(file: UploadFile):
    """
    Accept a CSV file, classify logs, and return the resulting CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        df = pd.read_csv(file.file)

        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'source' and 'log_message' columns",
            )

        logs = list(zip(df["source"], df["log_message"]))
        t0 = time.perf_counter()
        results = classify_batch(logs)
        latency_ms = (time.perf_counter() - t0) * 1000
        labels = [label for _, _, label in results]
        _record_metrics(labels, latency_ms)  # Update in-memory metrics for /metrics endpoint

        df["target_label"] = labels

        output_path = BASE_DIR / "resources" / "output.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)  # Persist so GET /classify can serve this file

        return FileResponse(
            path=str(output_path),
            media_type="text/csv",
            filename="classified_logs.csv",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()


@app.get("/classify")
async def get_classifications():
    """
    Return the last classified CSV from resources/output.csv.
    """
    output_path = BASE_DIR / "resources" / "output.csv"

    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No classified output found. POST a CSV to /classify first.",
        )

    return FileResponse(
        path=str(output_path),
        media_type="text/csv",
        filename="classified_logs.csv",
    )


@app.post("/classify-json")
async def classify_json(body: dict = Body(...)):
    """
    Accept JSON: { "logs": [ { "source": "...", "log_message": "..." }, ... ] }.
    Returns { "results": [ { "source", "log_message", "target_label" }, ... ] }.
    """
    logs_in = body.get("logs")
    if not isinstance(logs_in, list) or len(logs_in) == 0:
        raise HTTPException(status_code=400, detail="Body must contain a non-empty 'logs' array")
    try:
        logs = []
        for i, row in enumerate(logs_in):
            if not isinstance(row, dict):
                raise HTTPException(status_code=400, detail=f"logs[{i}] must be an object")
            s = row.get("source", "")
            m = row.get("log_message", "")
            logs.append((str(s), str(m)))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    t0 = time.perf_counter()
    results = classify_batch(logs)
    latency_ms = (time.perf_counter() - t0) * 1000
    labels = [label for _, _, label in results]
    _record_metrics(labels, latency_ms)

    out = [
        {"source": s, "log_message": m, "target_label": label}
        for (s, m), (_, _, label) in zip(logs, results)
    ]
    return {"results": out}


@app.get("/metrics")
async def get_metrics():
    """
    Return classification metrics: counts per label and average latency.
    """
    by_label = dict(_metrics["by_label"])
    total = _metrics["total_requests"]
    total_ms = _metrics["total_latency_ms"]
    return {
        "by_label": by_label,
        "total_requests": total,
        "avg_latency_ms": round(total_ms / total, 2) if total else 0,
    }


@app.post("/retrain")
async def retrain_model(file: UploadFile):
    """
    Upload a CSV with columns source, log_message, target_label.
    New rows are merged with existing dataset/labeled_logs.csv (or synthetic_logs.csv
    if labeled_logs does not exist), then the BERT classifier is retrained and saved.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    dataset_dir = BASE_DIR / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    labeled_path = dataset_dir / "labeled_logs.csv"
    synthetic_path = BASE_DIR / "synthetic_logs.csv"

    try:
        new_df = pd.read_csv(file.file)
        for col in ["source", "log_message", "target_label"]:
            if col not in new_df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"CSV must contain columns: source, log_message, target_label",
                )
    except HTTPException:
        raise
    finally:
        file.file.close()

    # Keep only needed columns
    new_df = new_df[["source", "log_message", "target_label"]].dropna(subset=["log_message", "target_label"])

    # Merge with existing data: prefer labeled_logs.csv, else seed from synthetic_logs.csv
    # so the first retrain has a base dataset if synthetic_logs.csv is present
    if labeled_path.exists():
        existing = pd.read_csv(labeled_path)
        for c in ["source", "log_message", "target_label"]:
            if c not in existing.columns:
                raise HTTPException(status_code=500, detail=f"Existing dataset missing column: {c}")
        combined = pd.concat([existing[["source", "log_message", "target_label"]], new_df], ignore_index=True)
    elif synthetic_path.exists():
        syn = pd.read_csv(synthetic_path)
        if "target_label" not in syn.columns:
            raise HTTPException(status_code=400, detail="synthetic_logs.csv must have target_label")
        cols = ["source", "log_message", "target_label"]
        for c in cols:
            if c not in syn.columns:
                raise HTTPException(status_code=500, detail=f"synthetic_logs.csv missing: {c}")
        combined = pd.concat([syn[cols], new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_csv(labeled_path, index=False)

    try:
        sys.path.insert(0, str(BASE_DIR / "training"))
        import retrain  # type: ignore
        msg = retrain.run_retrain(labeled_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrain failed: {e}")

    return {"status": "ok", "message": msg, "training_rows": len(combined)}


# ---------- Frontend: serve static and index at / ----------
# Mount static assets and serve the web UI at root so users can paste/upload logs in the browser
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return (static_dir / "index.html").read_text(encoding="utf-8")


if __name__ == "__main__":
    # Run with: uvicorn server:app --reload
    print("Start the server with: uvicorn server:app --reload")
