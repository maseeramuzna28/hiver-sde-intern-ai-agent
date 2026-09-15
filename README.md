# 🐝 AI Customer Support Agent - Hiver SDE Intern Take-Home Submission

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-purple.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![LLM API](https://img.shields.io/badge/LLM%20API-Groq%20%7C%20Anthropic-orange.svg)](https://console.groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Reproducible Setup](https://img.shields.io/badge/Reproducible-Under%2015%20Mins-brightgreen.svg)]()

An end-to-end **AI Customer Support Agent** for classifying `@AmazonHelp` messages, drafting grounded replies, and routing risky cases for human escalation. The production path is a decoupled React/Vite frontend and FastAPI backend, with a deterministic heuristic fallback when no LLM is configured or an API call fails.

---

## 📄 Submission Package Quick Links

- 📋 **Full Assignment Report**: [REPORT.md](REPORT.md) *(Problem Framing, Baselines, Failure Analysis, and Decision Log)*
- 🎯 **Golden Evaluation Set**: [data/golden_evaluation_set_200.json](data/golden_evaluation_set_200.json) *(200 hand-labeled examples)*
- 📝 **Sampling & Labeling Note**: [data/SAMPLING_AND_LABELING_NOTE.md](data/SAMPLING_AND_LABELING_NOTE.md)
- 📊 **Evaluation Results Export**: [evaluation_results.json](evaluation_results.json)

---

## 🏗️ Decoupled Full-Stack Architecture

```
hiver intern/
│── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI server entrypoint (port 8000)
│   │   ├── config.py            # Intent taxonomy & escalation rules
│   │   ├── classifier.py        # Groq/Anthropic classifier & heuristic engine
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

The deployed production entry points are `frontend/src/main.jsx` and `backend/app/main.py`. The root `server.py`, `app.py`, and `src/` modules are retained for the original CLI, Streamlit demo, and evaluation harness; they are not used by the Vercel/Render deployment.

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
python -m uvicorn app.main:app --reload
```
> 🌐 API runs at **`http://localhost:8000`**  
> 📖 Interactive Swagger API Docs at: **`http://localhost:8000/docs`**

### ☁️ Deploying

The repository includes a Render Blueprint in [`render.yaml`](render.yaml) for the backend. Deploy the frontend separately to Vercel.

**Backend (Render/Railway/Fly.io):**
- Root directory: `backend`
- Build command: `python -m pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `GROQ_API_KEY` (or `ANTHROPIC_API_KEY`), the matching model variable, `CORS_ORIGINS`, and `ENVIRONMENT=production`
- Health check path: `/health`

**Frontend (Vercel):**
- Root directory: `frontend`
- Build command: `npm run build`
- Environment variable: `VITE_API_URL=https://your-backend-domain.example.com`

Set `CORS_ORIGINS` on Render to the exact Vercel origin, such as `https://your-app.vercel.app` (comma-separated origins are supported). Do not commit API keys; use the variables in `.env.example` as a template.

### AI pipeline and fallback

`SupportAgent` classifies the message, applies deterministic escalation rules, and generates a DM-safe reply. Groq structured JSON output is requested when available; Anthropic uses the same strict prompt and both responses are validated before use. Invalid responses, unavailable SDKs, and API failures are logged without exposing credentials and fall back to the offline keyword classifier.

### Benchmark note

The published 200-example results are offline heuristic-fallback measurements: 61.50% intent accuracy, 60.10% macro F1, 49.21% escalation F1, and 4.35/5 reply quality. They are not LLM-run accuracy claims. The LLM-as-judge alignment figures are separate evidence from 30 annotated replies.

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
| **Main Model: Heuristic Fallback** | **61.50%** | **60.10%** | **49.21%** | **4.35 / 5.0** |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
