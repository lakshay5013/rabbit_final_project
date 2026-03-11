# 📘 FireReach – Technical Documentation

## 1. Agent Logic Flow

The FireReach agent follows a **strict sequential pipeline** — each tool's output feeds into the next.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│  { icp, company, email }                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: tool_signal_harvester                               │
│  ─────────────────────────────                               │
│  Input:  company name                                        │
│  Action: Query NewsAPI + Google News RSS                     │
│  Output: { company, signals[], sources[] }                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: tool_research_analyst                               │
│  ─────────────────────────────                               │
│  Input:  company, signals[], icp                             │
│  Action: LLM generates strategic Account Brief               │
│  Output: { account_brief }                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: tool_outreach_automated_sender                      │
│  ──────────────────────────────────────                      │
│  Input:  company, signals[], account_brief, email, icp       │
│  Action: LLM generates email → sends via SMTP/SendGrid      │
│  Output: { email_sent, subject, body }                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  FINAL RESPONSE                                              │
│  { signals, account_brief, email_sent, email_subject,        │
│    email_body }                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tool Schemas

### tool_signal_harvester

```json
{
  "name": "tool_signal_harvester",
  "description": "Fetch real-time signals about a target company including funding rounds, leadership changes, hiring trends, tech stack signals, product launches, and competitive movements.",
  "parameters": {
    "type": "object",
    "properties": {
      "company": {
        "type": "string",
        "description": "The target company name to research"
      }
    },
    "required": ["company"]
  }
}
```

**Response Schema:**
```json
{
  "company": "string",
  "signals": ["string"],
  "sources": ["string"]
}
```

---

### tool_research_analyst

```json
{
  "name": "tool_research_analyst",
  "description": "Analyze captured signals against the ICP to generate a two-paragraph Account Brief.",
  "parameters": {
    "type": "object",
    "properties": {
      "company": { "type": "string" },
      "signals": { "type": "array", "items": { "type": "string" } },
      "icp": { "type": "string" }
    },
    "required": ["company", "signals", "icp"]
  }
}
```

**Response Schema:**
```json
{
  "account_brief": "string (two paragraphs)"
}
```

---

### tool_outreach_automated_sender

```json
{
  "name": "tool_outreach_automated_sender",
  "description": "Generate and send a hyper-personalized outreach email referencing captured signals.",
  "parameters": {
    "type": "object",
    "properties": {
      "company": { "type": "string" },
      "signals": { "type": "array", "items": { "type": "string" } },
      "account_brief": { "type": "string" },
      "recipient_email": { "type": "string" },
      "icp": { "type": "string" }
    },
    "required": ["company", "signals", "account_brief", "recipient_email", "icp"]
  }
}
```

**Response Schema:**
```json
{
  "email_sent": true,
  "subject": "string",
  "body": "string"
}
```

---

## 3. System Prompt

```
You are FireReach, an autonomous outreach intelligence agent.

Your mission is to help sales teams send hyper-personalized outreach emails by:
1. Capturing real-time signals about target companies
2. Analyzing those signals to build strategic account briefs
3. Composing and sending compelling outreach emails

You have access to exactly THREE tools that you MUST call sequentially:

STEP 1 — tool_signal_harvester
STEP 2 — tool_research_analyst
STEP 3 — tool_outreach_automated_sender

RULES:
- Call tools in order: signal_harvester → research_analyst → outreach_sender
- NEVER fabricate or hallucinate signals
- Every email MUST reference specific signals from Step 1
- Keep the email concise, warm, and professional
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
    "email": "alex@ramp.com"
  }'
```

### Response

```json
{
  "signals": [
    "💰 Funding: Ramp raises $150M Series D at $7.65B valuation",
    "👥 Hiring: Ramp hiring 12 new backend engineers",
    "👤 Leadership: Ramp appoints new CTO from Stripe",
    "📈 Growth: Ramp expands enterprise customer base by 40%"
  ],
  "sources": ["TechCrunch", "Forbes", "LinkedIn"],
  "account_brief": "Ramp recently raised a $150M Series D round and is aggressively expanding their engineering team with 12 new backend hires. The appointment of a new CTO from Stripe signals a shift towards more sophisticated infrastructure and enterprise readiness.\n\nFor Series B+ startups scaling at this pace, structured cybersecurity training becomes critical. Rapid engineering team growth introduces security risks in internal tooling and developer workflows, creating an ideal alignment with our cybersecurity training platform.",
  "email_sent": true,
  "email_subject": "Congrats on Ramp's recent growth 🚀",
  "email_body": "Hi Alex,\n\nI noticed Ramp recently closed a significant funding round and is bringing on several new backend engineers. Teams scaling this quickly often face new security challenges in their developer workflows.\n\nWe help fast-growing engineering teams like yours build security-first habits without slowing down velocity. Would it make sense to chat for 15 minutes this week?\n\nBest,\nFireReach"
}
```

---

## 5. API Endpoint

### POST /run-agent

| Field | Type | Description |
|-------|------|-------------|
| `icp` | string | Ideal Customer Profile |
| `company` | string | Target company name |
| `email` | string | Recipient email address |

### GET /health

Returns service health and configuration status.
