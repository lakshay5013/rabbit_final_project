"""
tool_research_analyst.py
========================
Generates a strategic Account Brief by analyzing captured signals
against the Ideal Customer Profile (ICP) using Groq/Llama 3.
"""

import os
from groq import Groq


async def tool_research_analyst(company: str, signals: list[str], icp: str) -> dict:
    """
    Generate an Account Brief from signals and ICP.

    Args:
        company:  Target company name
        signals:  List of signal strings from tool_signal_harvester
        icp:      Ideal Customer Profile description

    Returns:
        Dict with 'account_brief' — two paragraphs of strategic analysis.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    signals_text = "\n".join(f"- {s}" for s in signals)

    prompt = f"""You are a senior sales research analyst. Analyze the following signals about {company}
and generate a strategic Account Brief.

SIGNALS CAPTURED:
{signals_text}

IDEAL CUSTOMER PROFILE (ICP):
{icp}

Write EXACTLY two paragraphs:

PARAGRAPH 1 — Company Growth Signals:
Summarize the key growth signals. Mention specific data points from the signals above.
Explain what these signals indicate about the company's current trajectory.

PARAGRAPH 2 — Strategic Pain Points & ICP Alignment:
Based on the growth signals, identify the strategic pain points the company likely faces.
Explain exactly how our offering (as described in the ICP) aligns with their current needs.

RULES:
- Be specific. Reference actual signals, not generic statements.
- Write in a professional but conversational tone.
- Do NOT add any headings, bullet points, or extra formatting.
- Output ONLY the two paragraphs, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior B2B sales research analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    account_brief = response.choices[0].message.content.strip()

    return {"account_brief": account_brief}
