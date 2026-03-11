# 📘 FireReach – Technical Documentation

---

## 1. Agent Logic Flow

The FireReach agent follows a **strict sequential pipeline** — each tool's output feeds into the next.

```
┌──────────────────────────────────────────────────┐
│              USER INPUT                           │
│  { icp, company, email, recipient_name }          │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────┐
│  STEP 1: tool_signal_harvester                    │
│                                                   │
│  Input:  company name                             │
│  Action: Query NewsAPI + Google News RSS          │
│  Output: { company, signals[], sources[] }        │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────┐
│  STEP 2: tool_research_analyst                    │
│                                                   │
│  Input:  company, signals[], icp                  │
│  Action: LLM generates strategic Account Brief    │
│  Output: { account_brief }                        │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────┐
│  STEP 3: tool_outreach_automated_sender           │
│                                                   │
│  Input:  company, signals[], account_brief,       │
│          email, recipient_name, icp               │
│  Action: LLM generates email → sends via API      │
│  Output: { email_sent, subject, body }            │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────┐
│  FINAL RESPONSE                                   │
│  { signals, account_brief, email_sent,            │
│    email_subject, email_body }                    │
└──────────────────────────────────────────────────┘
```

---

## 2. Tool Schemas

### Tool 1: tool_signal_harvester

**Purpose:** Fetch real-time signals about a target company.

```json
{
  "name": "tool_signal_harvester",
  "parameters": {
    "properties": {
      "company": { "type": "string", "description": "Target company name" }
    },
    "required": ["company"]
  }
}
```

**Returns:**
```json
{
  "company": "Ramp",
  "signals": ["💰 Funding: Ramp raises $200M Series E..."],
  "sources": ["TechCrunch", "Forbes"]
}
```

---

### Tool 2: tool_research_analyst

**Purpose:** Generate a strategic Account Brief from signals + ICP.

```json
{
  "name": "tool_research_analyst",
  "parameters": {
    "properties": {
      "company": { "type": "string" },
      "signals": { "type": "array", "items": { "type": "string" } },
      "icp": { "type": "string" }
    },
    "required": ["company", "signals", "icp"]
  }
}
```

**Returns:**
```json
{
  "account_brief": "Two paragraphs: growth signals + ICP alignment"
}
```

---

### Tool 3: tool_outreach_automated_sender

**Purpose:** Generate and send a hyper-personalized outreach email.

```json
{
  "name": "tool_outreach_automated_sender",
  "parameters": {
    "properties": {
      "company": { "type": "string" },
      "signals": { "type": "array", "items": { "type": "string" } },
      "account_brief": { "type": "string" },
      "recipient_email": { "type": "string" },
      "recipient_name": { "type": "string" },
      "icp": { "type": "string" }
    },
    "required": ["company", "signals", "account_brief", "recipient_email", "recipient_name", "icp"]
  }
}
```

**Returns:**
```json
{
  "email_sent": true,
  "subject": "Congrats on Ramp's recent growth 🚀",
  "body": "Hi Alex, I noticed Ramp recently..."
}
```

---

## 3. System Prompt

```
You are FireReach, an autonomous outreach intelligence agent.

Your mission:
1. Capture real-time signals about target companies
2. Analyze signals to build strategic account briefs
3. Compose and send compelling outreach emails

THREE tools, called SEQUENTIALLY:
  STEP 1 → tool_signal_harvester
  STEP 2 → tool_research_analyst
  STEP 3 → tool_outreach_automated_sender

RULES:
- NEVER fabricate or hallucinate signals
- Every email MUST reference specific signals
- Keep emails concise, warm, and professional
```

---

## 4. Example Run

### Request

```bash
curl -X POST http://localhost:8000/run-agent \
  -H "Content-Type: application/json" \
  -d '{
    "icp": "We sell high-end cybersecurity training to Series B+ startups",
    "company": "Ramp",
    "email": "alex@ramp.com",
    "recipient_name": "Alex"
  }'
```

### Response

```json
{
  "signals": [
    "💰 Funding: Ramp Raises $200M Series E at $16B Valuation",
    "👥 Hiring: Ramp Acquires Jolt AI to Help Engineers Build Faster",
    "👤 Leadership: Ramp's CEO on building zero-touch finance",
    "📈 Growth: Ramp expands enterprise customer base"
  ],
  "sources": ["PR Newswire", "Crunchbase News", "McKinsey"],
  "account_brief": "Ramp recently raised a $200M Series E and is scaling rapidly with the acquisition of Jolt AI. This growth introduces cybersecurity risks...\n\nOur cybersecurity training for Series B+ startups aligns perfectly with Ramp's current needs...",
  "email_sent": true,
  "email_subject": "Congrats on Ramp's recent growth 🚀",
  "email_body": "Hi Alex,\n\nI noticed Ramp recently raised $200M in Series E funding. Teams scaling this quickly often face new security challenges...\n\nWould it make sense to chat for 15 minutes this week?\n\nBest,\nFireReach"
}
```

---

## 5. API Endpoints

### POST /run-agent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `icp` | string | ✅ | Ideal Customer Profile |
| `company` | string | ✅ | Target company name |
| `email` | string | ✅ | Recipient email address |
| `recipient_name` | string | ❌ | Name for greeting (e.g. "Alex") |

### GET /health

Returns service health and API configuration status.

---

## 6. Email Delivery

### How it works

The system tries email delivery in this priority order:

| Priority | Method | Type | Works On |
|----------|--------|------|----------|
| 1️⃣ | **Resend API** | HTTPS | ✅ Local + ✅ Render + ✅ Vercel |
| 2️⃣ | **Gmail SMTP** | Port 587 | ✅ Local + ❌ Render (blocked) |
| 3️⃣ | **SendGrid API** | HTTPS | ✅ Local + ✅ Render |
| 4️⃣ | **Console Log** | — | Preview only (no send) |

### ⚠️ Important: Render Deployment

> **Render's free tier blocks SMTP port 587.** When deployed on Render, Gmail SMTP will fail with:
> ```
> OSError: [Errno 101] Network is unreachable
> ```
> **Solution:** Use **Resend API** (HTTP-based, free at [resend.com](https://resend.com)).
> Add `RESEND_API_KEY` to Render environment variables.

### Local Development

Gmail SMTP works perfectly on local. Set `SMTP_EMAIL` and `SMTP_APP_PASSWORD` in `.env`.
