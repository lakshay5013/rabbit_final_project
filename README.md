# 🔥 FireReach – Autonomous Outreach Engine

An **Agentic AI system** that autonomously captures company signals, generates strategic insights, and sends hyper-personalized outreach emails.

Built with **FastAPI + Groq (Llama 3) + React** and a strict **tool-calling architecture**.

---

## 🏗️ Architecture

```
User Input → Agent Pipeline
                ├── 📡 tool_signal_harvester    (NewsAPI + Google News)
                ├── 🔬 tool_research_analyst     (Groq/Llama 3 analysis)
                └── 📧 tool_outreach_sender      (Resend API / Gmail SMTP)
```

---

## 🔑 API Keys Required

| Key | Source | Purpose | Free? |
|-----|--------|---------|-------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | LLM (Llama 3) | ✅ |
| `NEWS_API_KEY` | [newsapi.org](https://newsapi.org) | Company signals | ✅ |
| `RESEND_API_KEY` | [resend.com](https://resend.com) | Email (deployed) | ✅ 100/day |
| `SMTP_EMAIL` | Your Gmail | Email (local dev) | ✅ |
| `SMTP_APP_PASSWORD` | Gmail App Password | Email auth (local) | ✅ |

### 📧 Email Setup

**Local Development:**
- Use **Gmail SMTP** — works perfectly via port 587
- Gmail Settings → 2-Step Verification ON → App Passwords → Generate 16-char code

**Deployed on Render:**
- ⚠️ **Gmail SMTP does NOT work** on Render (port 587 is blocked by Render's free tier)
- Use **Resend API** instead — sign up at [resend.com](https://resend.com), get free API key
- Resend sends emails via HTTPS (no port restrictions)

---

## 🚀 Quick Start

### 1. Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Backend

```bash
cd backend
python -m uvicorn main:app --reload
# API at http://localhost:8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
# UI at http://localhost:5173
```

### 4. Use the Dashboard

1. Enter your **ICP** (what you sell)
2. Enter the **Target Company** name
3. Enter the **Candidate Email**
4. Enter the **Recipient Name** (for personalized greeting)
5. Click **"🚀 Run FireReach Agent"**

---

## 📁 Project Structure

```
RabbitFinal/
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

### Backend → Render.com

| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Runtime | Python 3.11+ |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Environment Variables:** `GROQ_API_KEY`, `NEWS_API_KEY`, `RESEND_API_KEY`

> ⚠️ **Important:** Render blocks SMTP port 587 on free tier. Gmail SMTP will NOT work on Render. Use `RESEND_API_KEY` for email delivery on Render. Gmail SMTP works only for local development.

### Frontend → Vercel.com

| Setting | Value |
|---------|-------|
| Root Directory | `frontend` |
| Framework | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |

**Environment Variable:** `VITE_API_URL` = your Render backend URL
