# 🧠 NLP-Based Log Classification System

## 📌 Overview

This project implements a **hybrid NLP-driven log classification pipeline** that efficiently categorizes system and application logs by combining **rule-based methods** with **machine learning and NLP techniques**.

The system is designed to **minimize cost and latency** by applying simple techniques first (regex-based classification) and escalating to more advanced models only for unknown or complex log messages. This approach closely mirrors **real-world log analysis architectures** used in cloud platforms and enterprise monitoring systems.

---

## 🎯 Problem Statement

Modern distributed systems generate **large volumes of logs** that are:

- Highly repetitive for known issues
- Semi-structured with minor variations
- Continuously evolving with new error patterns

Using heavyweight AI models on every log message is:
- Computationally expensive
- Slower at scale
- Often unnecessary for known patterns

This project addresses the problem by building a **layered log classification framework** that balances **accuracy, scalability, and cost efficiency**.

---

## 🏗️ High-Level Architecture



Log Message
↓
Regex-Based Classification
├── Known Pattern → Assigned Label
└── Unknown
↓
Sentence Embeddings
↓
DBSCAN Clustering
↓
Cluster Analysis
↓
(Future) BERT / LLM-Based Classification




---

## ⚙️ Current Features

- ✅ Regex-based log pattern matching
- ✅ Identification of unmatched (unknown) log messages
- ✅ Semantic embeddings using transformer models
- ✅ DBSCAN clustering to group similar unknown logs
- ✅ Cluster-size analysis to evaluate training data sufficiency
- ✅ Support for synthetic datasets for experimentation

---

## 🚧 Features Under Development

- 🔄 Automatic regex pattern inference from log clusters
- 🔄 Threshold-based decision for “enough training samples”
- 🔄 Supervised classification using BERT for stable log classes
- 🔄 LLM-based classification for rare or unseen logs
- 🔄 Feedback loop to convert ML/LLM outputs into new regex rules

---

## 📁 Project Structure




classification_logs/
│
├── training/
│ ├── dataset/
│ │ └── synthetic_logs.csv
│ └── training.ipynb
│
├── main.py
├── README.md
└── .gitignore




---

## 🛠️ Tech Stack

- **Python**
- **Regular Expressions (Regex)**
- **Pandas**
- **SentenceTransformers**
- **DBSCAN (scikit-learn)**
- **Jupyter Notebook**
- *(Planned)* BERT, LLM APIs

---

## 🧩 Why DBSCAN?

DBSCAN is used for clustering unknown logs because:

- It does not require a predefined number of clusters
- It groups logs based on semantic similarity
- It naturally handles noise and rare events
- It works well for evolving and unknown log patterns

---

## 🧪 Example Use Case

Sample logs:


"ERROR: Database connection timeout"
"DB timeout while connecting to read replica"



These logs are:
- Embedded into vector space
- Clustered together using DBSCAN
- Treated as a single semantic log pattern

Such clusters can later be used to:
- Create regex rules
- Train supervised models
- Improve automated alerting

---

## 📈 Real-World Relevance

The design principles in this project align with systems used in:

- Cloud monitoring platforms
- SIEM and security analytics tools
- Observability and DevOps pipelines
- Enterprise-scale log intelligence systems

---

## 🚀 Project Goal

To build a **self-improving log classification system** that:
- Starts with simple rule-based logic
- Learns from data over time
- Adapts automatically to new log patterns

---

## 🧑‍💻 Author

**Vinay Varshigan SJ**  
MS in Computer Science  
Northeastern University  
Interests: NLP, Machine Learning, Log Intelligence, AI Systems

---

## 📌 Project Status

🚧 **Active Development**  
The project is under continuous improvement, and features may change as development progresses.


