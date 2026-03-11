# 🔥 FireReach – Autonomous Outreach Engine

An **Agentic AI system** that autonomously captures company signals, generates strategic insights, and sends hyper-personalized outreach emails.

Built with **FastAPI + Groq (Llama 3) + React** and a strict **tool-calling architecture**.

---

## 🏗️ Architecture

```
User Input → Agent Pipeline
                ├── 📡 tool_signal_harvester    (NewsAPI + Google News)
                ├── 🔬 tool_research_analyst     (Groq/Llama 3 analysis)
                └── 📧 tool_outreach_sender      (Gmail SMTP / SendGrid)
```

---

## 🔑 API Keys Required

| Key | Source | Purpose |
|-----|--------|---------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | LLM calls (Llama 3) |
| `NEWS_API_KEY` | [newsapi.org](https://newsapi.org) | Real company signals |
| `SMTP_EMAIL` | Your Gmail address | Email sending |
| `SMTP_APP_PASSWORD` | Gmail App Password | Email authentication |

> **Gmail App Password Setup:** Gmail Settings → 2-Step Verification → App Passwords → Generate

---

## 🚀 Quick Start

### 1. Clone & Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Backend

```bash
cd backend
uvicorn main:app --reload
# API runs at http://localhost:8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
# UI runs at http://localhost:5173
```

### 4. Use the Dashboard

1. Enter your **ICP** (what you sell)
2. Enter the **target company** name
3. Enter the **candidate email**
4. Click **"Run FireReach Agent"**

---

## 📁 Project Structure

```
fire-reach/
├── backend/
│   ├── main.py                 # FastAPI app + /run-agent endpoint
│   ├── agent.py                # Agentic pipeline + tool schemas
│   ├── tools/
│   │   ├── signal_harvester.py # Tool 1: Fetch real signals
│   │   ├── research_analyst.py # Tool 2: Generate Account Brief
│   │   └── outreach_sender.py  # Tool 3: Compose + send email
│   ├── prompts/
│   │   └── system_prompt.txt   # Agent system prompt
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── App.jsx             # React dashboard
│       ├── App.css             # Component styles
│       └── index.css           # Design tokens
├── README.md
└── DOCS.md
```

---

## 🌐 Deployment

### Backend (Render)
- Runtime: Python 3.11+
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set env vars in Render dashboard

### Frontend (Vercel)
- Framework: Vite
- Build: `npm run build`
- Output: `dist/`
- Set `VITE_API_URL` env var to your Render backend URL
