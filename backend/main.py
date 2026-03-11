"""
main.py
=======
FastAPI application for FireReach – Autonomous Outreach Engine.

Endpoints:
  POST /run-agent  — Execute the full agent pipeline
  GET  /health     — Health check
"""

import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing agent
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from agent import FireReachAgent


# ── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="FireReach – Autonomous Outreach Engine",
    description="Agentic AI workflow with tool calling for automated sales outreach",
    version="1.0.0",
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ───────────────────────────────────────────────
class AgentRequest(BaseModel):
    icp: str             # Ideal Customer Profile description
    company: str         # Target company name
    email: str           # Candidate email address
    recipient_name: str = ""  # Recipient name for personalization


class AgentResponse(BaseModel):
    signals: list[str]
    sources: list[str]
    account_brief: str
    email_sent: bool
    email_subject: str
    email_body: str
    email_error: str = ""


# ── Routes ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "service": "FireReach Agent",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "news_api_configured": bool(os.getenv("NEWS_API_KEY")),
        "smtp_configured": bool(os.getenv("SMTP_EMAIL") and os.getenv("SMTP_APP_PASSWORD")),
    }


@app.post("/run-agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    Execute the FireReach agent pipeline.

    The agent will:
    1. Harvest signals about the target company
    2. Generate an Account Brief
    3. Compose and send a personalized outreach email
    """
    # Validate that required API keys are present
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Add it to backend/.env"
        )

    try:
        agent = FireReachAgent()
        result = await agent.run(
            icp=request.icp,
            company=request.company,
            email=request.email,
            recipient_name=request.recipient_name,
        )
        return AgentResponse(
            signals=result["signals"],
            sources=result.get("sources", []),
            account_brief=result["account_brief"],
            email_sent=result["email_sent"],
            email_subject=result["email_subject"],
            email_body=result["email_body"],
            email_error=result.get("email_error", ""),
        )
    except Exception as e:
        print(f"[FireReach] Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Run with: uvicorn main:app --reload ─────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
