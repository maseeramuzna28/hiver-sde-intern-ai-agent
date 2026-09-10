# 🐝 AI Customer Support Agent - Hiver SDE Intern Take-Home Submission

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-purple.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![Claude API](https://img.shields.io/badge/Claude%20API-Anthropic-orange.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Reproducible Setup](https://img.shields.io/badge/Reproducible-Under%2015%20Mins-brightgreen.svg)]()

An end-to-end, production-grade **Full-Stack AI Customer Support Agent** for Twitter customer support classification (`@AmazonHelp`), context-aware reply generation, human escalation routing, decoupled **React/Vite Web Frontend** (`npm run dev`), **FastAPI REST Backend**, and LLM-as-judge evaluation, built for the **Hiver SDE Intern Take-Home Assignment**.

---

## 📄 Submission Package Quick Links

- 📋 **Full Assignment Report**: [`REPORT.md`](file:///c:/Users/Admin/Desktop/hiver%20intern/REPORT.md) *(Problem Framing, Baselines, Failure Analysis, Mandatory Headline Number Analysis, Decision Log)*
- 🎯 **Golden Evaluation Set**: [`data/golden_evaluation_set_200.json`](file:///c:/Users/Admin/Desktop/hiver%20intern/data/golden_evaluation_set_200.json) *(200 hand-labeled examples)*
- 📝 **Sampling & Labeling Note**: [`data/SAMPLING_AND_LABELING_NOTE.md`](file:///c:/Users/Admin/Desktop/hiver%20intern/data/SAMPLING_AND_LABELING_NOTE.md)
- 📊 **Evaluation Results Export**: [`evaluation_results.json`](file:///c:/Users/Admin/Desktop/hiver%20intern/evaluation_results.json)

---

## 🏗️ Decoupled Full-Stack Architecture

```
hiver intern/
│── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI server entrypoint (port 8000)
│   │   ├── config.py            # Intent taxonomy & escalation rules
│   │   ├── classifier.py        # Claude API classifier & heuristic engine
│   │   ├── reply_generator.py   # Grounded response drafting
│   │   ├── escalation.py        # Priority escalation decision logic
│   │   └── agent.py             # SupportAgent pipeline orchestrator
│   └── requirements.txt
│
│── frontend/                    # Decoupled React + Vite Web Dashboard
│   ├── src/
│   │   ├── App.jsx              # Interactive Web Dashboard UI
│   │   └── main.jsx
│   ├── package.json             # npm dependencies & `npm run dev` script
│   └── vite.config.js           # Vite dev server configuration (port 5173)
│
│── evaluate.py                  # Evaluation runner across 3 model baselines
│── REPORT.md                    # Hiver Assignment Submission Report
└── README.md                    # Root Documentation
```

---

## 🚀 How to Run Frontend & Backend

### 🎨 1. Start the React Frontend (`npm run dev`)
Open Terminal 1 in VS Code:
```bash
cd frontend
npm install
npm run dev
```
> 🌐 Opens interactive Web Dashboard in browser at: **`http://localhost:5173`**

---

### 🔌 2. Start the FastAPI REST Backend
Open Terminal 2 in VS Code:
```bash
cd backend
python -m pip install -r requirements.txt
python app/main.py
```
> 🌐 API runs at **`http://localhost:8000`**  
> 📖 Interactive Swagger API Docs at: **`http://localhost:8000/docs`**

---

### 💻 3. Run Benchmark Evaluation Suite (CLI)
```bash
python evaluate.py
```

---

## 📊 Benchmark Results Summary

| Model Architecture | Accuracy | Macro F1 | Escalation F1 | Reply Quality (1-5) |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline 1: Trivial (Majority Class)** | 16.50% | 4.72% | 0.00% | 4.00 / 5.0 |
| **Baseline 2: Simple (TF-IDF + Rules)** | 64.00% | 64.25% | 21.05% | 4.75 / 5.0 |
| **Main Model: Claude AI Support Agent** | **94.50%** *(API)* / 61.5% *(Fallback)* | **94.10%** | **88.50%** | **4.86 / 5.0** |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
