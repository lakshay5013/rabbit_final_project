"""
agent.py
========
FireReach Autonomous Agent — Implements the agentic tool-calling pipeline.

The agent follows a strict sequential chain:
  1. tool_signal_harvester   → Capture real company signals
  2. tool_research_analyst   → Generate Account Brief
  3. tool_outreach_automated_sender → Compose & send personalized email

Uses Groq API with Llama 3 for LLM reasoning and tool orchestration.
"""

import os
import json
from groq import Groq
from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.outreach_sender import tool_outreach_automated_sender


# ── Tool Schemas (OpenAI-compatible function calling format) ────────────────
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "tool_research_analyst",
            "description": "Analyze captured signals against the Ideal Customer Profile (ICP) to generate a two-paragraph Account Brief covering growth signals, strategic pain points, and ICP alignment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The target company name"
                    },
                    "signals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of captured signal strings from tool_signal_harvester"
                    },
                    "icp": {
                        "type": "string",
                        "description": "The Ideal Customer Profile description"
                    }
                },
                "required": ["company", "signals", "icp"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_outreach_automated_sender",
            "description": "Generate a hyper-personalized outreach email referencing the captured signals and send it to the target recipient via email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The target company name"
                    },
                    "signals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of captured signals"
                    },
                    "account_brief": {
                        "type": "string",
                        "description": "The account brief from tool_research_analyst"
                    },
                    "recipient_email": {
                        "type": "string",
                        "description": "Email address of the outreach target"
                    },
                    "icp": {
                        "type": "string",
                        "description": "The Ideal Customer Profile description"
                    }
                },
                "required": ["company", "signals", "account_brief", "recipient_email", "icp"]
            }
        }
    }
]


# ── Tool dispatcher ────────────────────────────────────────────────────────
TOOL_FUNCTIONS = {
    "tool_signal_harvester": tool_signal_harvester,
    "tool_research_analyst": tool_research_analyst,
    "tool_outreach_automated_sender": tool_outreach_automated_sender,
}


class FireReachAgent:
    """
    Autonomous outreach agent that orchestrates tool calls via LLM reasoning.
    """

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.system_prompt = self._load_system_prompt()
        self.trace: list[dict] = []   # Reasoning trace for debugging

    def _load_system_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "You are FireReach, an autonomous outreach agent."

    async def run(self, icp: str, company: str, email: str, recipient_name: str = "") -> dict:
        """
        Execute the full agentic pipeline:
          Step 1: Signal Capture
          Step 2: Research & Brief
          Step 3: Email Generation & Delivery

        Returns:
            Dict with signals, account_brief, email_sent, email_subject, email_body
        """
        print(f"\n{'='*60}")
        print(f"🚀 FireReach Agent — Starting pipeline for {company}")
        print(f"{'='*60}")

        # ── STEP 1: Signal Capture ──────────────────────────────────────────
        print("\n📡 Step 1: Calling tool_signal_harvester...")
        self._log_trace("step_1_start", {"tool": "tool_signal_harvester", "company": company})

        signal_result = await tool_signal_harvester(company)
        signals = signal_result.get("signals", [])
        sources = signal_result.get("sources", [])

        self._log_trace("step_1_complete", {
            "signals_count": len(signals),
            "signals": signals,
            "sources": sources,
        })
        print(f"   ✅ Captured {len(signals)} signals from {len(sources)} sources")
        for s in signals:
            print(f"      • {s}")

        # ── STEP 2: Research & Account Brief ────────────────────────────────
        print("\n🔬 Step 2: Calling tool_research_analyst...")
        self._log_trace("step_2_start", {
            "tool": "tool_research_analyst",
            "signals": signals,
            "icp": icp,
        })

        research_result = await tool_research_analyst(company, signals, icp)
        account_brief = research_result.get("account_brief", "")

        self._log_trace("step_2_complete", {"account_brief_length": len(account_brief)})
        print(f"   ✅ Account Brief generated ({len(account_brief)} chars)")

        # ── STEP 3: Email Composition & Delivery ────────────────────────────
        print("\n📧 Step 3: Calling tool_outreach_automated_sender...")
        self._log_trace("step_3_start", {
            "tool": "tool_outreach_automated_sender",
            "recipient": email,
        })

        email_result = await tool_outreach_automated_sender(
            company=company,
            signals=signals,
            account_brief=account_brief,
            recipient_email=email,
            recipient_name=recipient_name,
            icp=icp,
        )

        self._log_trace("step_3_complete", {
            "email_sent": email_result.get("email_sent"),
            "subject": email_result.get("subject"),
        })
        print(f"   ✅ Email {'sent' if email_result.get('email_sent') else 'failed'}")

        # ── Final Result ────────────────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"🎯 FireReach Agent — Pipeline complete for {company}")
        print(f"{'='*60}\n")

        return {
            "signals": signals,
            "sources": sources,
            "account_brief": account_brief,
            "email_sent": email_result.get("email_sent", False),
            "email_subject": email_result.get("subject", ""),
            "email_body": email_result.get("body", ""),
            "email_error": email_result.get("error_message", ""),
            "trace": self.trace,
        }

    def _log_trace(self, step: str, data: dict):
        """Add an entry to the reasoning trace."""
        self.trace.append({"step": step, **data})
