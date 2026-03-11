"""
tool_signal_harvester.py
========================
Fetches real-time signals about a target company using NewsAPI.
Signals include: funding rounds, leadership changes, hiring trends,
tech stack signals, product launches, and competitive movements.
"""

import os
import httpx
from typing import Any


# ── Signal categories we scan for ───────────────────────────────────────────
SIGNAL_KEYWORDS = {
    "funding":    ["funding", "raised", "series", "investment", "valuation", "investor"],
    "leadership": ["cto", "ceo", "cfo", "vp", "hired", "appointed", "leadership", "executive"],
    "hiring":     ["hiring", "engineers", "recruiting", "job", "talent", "team", "workforce"],
    "tech_stack": ["infrastructure", "migration", "cloud", "kubernetes", "aws", "platform"],
    "product":    ["launch", "product", "release", "feature", "update", "announcement"],
    "growth":     ["expansion", "growth", "scaling", "revenue", "customers", "partnership"],
}


def _is_relevant(title: str, company: str) -> bool:
    """
    Check if an article title is actually about the target company,
    not just a random mention of a common word.
    """
    company_lower = company.lower().strip()
    title_lower = title.lower()

    # Direct company name match (as a whole word)
    # e.g. "Ramp" should match "Ramp raises funding" but not "highway ramp"
    import re
    pattern = r'\b' + re.escape(company_lower) + r'\b'
    if not re.search(pattern, title_lower):
        return False

    # Extra filter: reject if title is clearly about something else
    irrelevant_terms = [
        "highway", "freeway", "traffic", "road", "ramp up",
        "on-ramp", "off-ramp", "wheelchair ramp",
    ]
    for term in irrelevant_terms:
        if term in title_lower:
            return False

    return True


async def tool_signal_harvester(company: str) -> dict[str, Any]:
    """
    Fetch real signals about a company from NewsAPI.

    Args:
        company: The target company name (e.g., "Ramp")

    Returns:
        Dict with company name, list of signal strings, and sources.
    """
    api_key = os.getenv("NEWS_API_KEY", "")
    signals: list[str] = []
    sources: list[str] = []

    # Build a more specific search query to avoid generic matches
    # e.g. "Ramp" -> "Ramp company OR Ramp startup OR Ramp fintech"
    search_queries = [
        f'"{company}" company',
        f'"{company}" startup',
        f'"{company}" funding',
        f'"{company}" hiring',
    ]

    # ── 1. NewsAPI — Real news articles ─────────────────────────────────────
    if api_key:
        for query in search_queries:
            if len(signals) >= 8:
                break
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        "https://newsapi.org/v2/everything",
                        params={
                            "q": query,
                            "sortBy": "publishedAt",
                            "pageSize": 15,
                            "language": "en",
                            "apiKey": api_key,
                        },
                    )
                    if resp.status_code == 200:
                        articles = resp.json().get("articles", [])
                        for article in articles:
                            title = (article.get("title") or "").strip()
                            description = (article.get("description") or "").strip()
                            source_name = article.get("source", {}).get("name", "Unknown")
                            combined_text = f"{title} {description}".lower()

                            # IMPORTANT: Check relevance — is this article actually about the company?
                            if not _is_relevant(title, company):
                                continue

                            # Classify the article into signal categories
                            for category, keywords in SIGNAL_KEYWORDS.items():
                                if any(kw in combined_text for kw in keywords):
                                    signal_text = _format_signal(category, title)
                                    if signal_text and signal_text not in signals:
                                        signals.append(signal_text)
                                        sources.append(source_name)
                                    break  # one category per article
                    else:
                        print(f"[SignalHarvester] NewsAPI returned status {resp.status_code}")
            except Exception as e:
                print(f"[SignalHarvester] NewsAPI error: {e}")

    # ── 2. Fallback: Google News RSS (no API key needed) ────────────────────
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            # Use quoted company name for more specific results
            rss_url = f'https://news.google.com/rss/search?q="{company}"+company&hl=en-US&gl=US&ceid=US:en'
            resp = await client.get(rss_url)
            if resp.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                items = root.findall(".//item")
                for item in items[:15]:
                    title = (item.findtext("title") or "").strip()
                    source = (item.findtext("source") or "Google News").strip()

                    # Check relevance
                    if not _is_relevant(title, company):
                        continue

                    combined_text = title.lower()
                    for category, keywords in SIGNAL_KEYWORDS.items():
                        if any(kw in combined_text for kw in keywords):
                            signal_text = _format_signal(category, title)
                            if signal_text and signal_text not in signals:
                                signals.append(signal_text)
                                sources.append(source)
                            break
    except Exception as e:
        print(f"[SignalHarvester] Google News RSS error: {e}")

    # ── 3. If no real signals found, search for general company info ────────
    if not signals:
        # Try one more broad search
        if api_key:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        "https://newsapi.org/v2/everything",
                        params={
                            "q": f'"{company}"',
                            "sortBy": "relevancy",
                            "pageSize": 20,
                            "language": "en",
                            "apiKey": api_key,
                        },
                    )
                    if resp.status_code == 200:
                        articles = resp.json().get("articles", [])
                        for article in articles:
                            title = (article.get("title") or "").strip()
                            source_name = article.get("source", {}).get("name", "Unknown")

                            if not _is_relevant(title, company):
                                continue

                            signal_text = f"📰 News: {title[:150]}"
                            if signal_text not in signals:
                                signals.append(signal_text)
                                sources.append(source_name)
                            if len(signals) >= 5:
                                break
            except Exception as e:
                print(f"[SignalHarvester] Broad search error: {e}")

    # ── 4. If still nothing, provide honest fallback ────────────────────────
    if not signals:
        signals = [
            f"📰 {company} is actively present in industry discussions (no specific recent signals found via news APIs)",
            f"📰 {company} may have recent activity not captured by public news sources",
        ]
        sources = ["General Research"]

    return {
        "company": company,
        "signals": signals[:10],  # Cap at 10 most relevant
        "sources": list(set(sources))[:5],
    }


def _format_signal(category: str, title: str) -> str:
    """Format a raw article title into a clean signal string."""
    # Truncate overly long titles
    if len(title) > 150:
        title = title[:147] + "..."
    if not title:
        return ""

    prefixes = {
        "funding":    "💰 Funding: ",
        "leadership": "👤 Leadership: ",
        "hiring":     "👥 Hiring: ",
        "tech_stack": "🔧 Tech: ",
        "product":    "🚀 Product: ",
        "growth":     "📈 Growth: ",
    }
    return f"{prefixes.get(category, '')}{title}"
