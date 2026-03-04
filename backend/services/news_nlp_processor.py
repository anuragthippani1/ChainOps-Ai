"""
AI/NLP module for supply chain news:
- Summarize the article
- Extract risk signals (port closure, delay, strike, etc.)
- Extract location: country, city, port
- Assign a risk score (1-5)
"""
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from models.schemas import SupplyChainNewsAlert
import uuid

# Port/city to country - derived from logistics_regions (single source of truth)
from data.logistics_regions import (
    PORT_TO_COUNTRY,
    ALL_WORLD_COUNTRIES,
    COUNTRY_ALIASES,
    get_canonical_country,
)

# Logistics-only risk signals
LOGISTICS_RISK_SIGNALS = {
    "port congestion": ["port congestion", "congestion", "port backlog"],
    "shipping delays": ["shipping delays", "shipping delay", "freight delay", "delayed shipment", "shipment delay"],
    "container shortage": ["container shortage", "container shortfall"],
    "cargo disruption": ["cargo disruption", "cargo backlog", "backlog", "container backlog"],
    "logistics strike": ["logistics strike", "port strike", "shipping strike", "dock strike", "dockworker strike"],
    "vessel rerouting": ["vessel rerouting", "rerouting", "diversion", "route change"],
    "customs hold": ["customs hold", "customs delay", "customs clearance", "held at customs"],
    "trade sanctions": ["trade sanctions", "sanctions", "economic sanctions"],
    "export ban": ["export ban", "export restriction"],
    "import restriction": ["import restriction", "import restrictions", "import ban"],
    "oil supply disruption": ["oil supply disruption", "oil supply shock", "oil supply risk"],
    "maritime attack": ["maritime attack", "ship attack", "vessel attack"],
    "canal blockage": ["canal blockage", "suez canal", "panama canal", "canal closure"],
    "transport disruption": ["transport disruption", "transport delays", "transit disruption"],
    "maritime accident": ["maritime accident", "ship accident", "vessel accident", "collision"],
}

DISRUPTION_TRIGGER_KEYWORDS = [
    "port congestion",
    "shipping delays",
    "container shortage",
    "cargo disruption",
    "trade sanctions",
    "export ban",
    "import restriction",
    "oil supply disruption",
    "maritime attack",
    "canal blockage",
    "logistics strike",
    "transport disruption",
]

# Maritime chokepoints that should boost disruption detection and map to countries.
CHOKEPOINT_LOCATION_COUNTRIES = {
    "suez canal": ["Egypt"],
    "red sea": ["Saudi Arabia", "Yemen"],
    "panama canal": ["Panama"],
    "strait of hormuz": ["Iran", "United Arab Emirates"],
    "hormuz strait": ["Iran", "United Arab Emirates"],
    "malacca strait": ["Singapore", "Malaysia"],
    "strait of malacca": ["Singapore", "Malaysia"],
}

# Countries to prioritize due to global trade/energy impact.
HIGH_IMPACT_COUNTRIES = {
    "Saudi Arabia",
    "United Arab Emirates",
    "China",
    "United States",
    "Germany",
    "Singapore",
    "India",
    "Panama",
    "Egypt",
    "Turkey",
}

# Use canonical country names and safe aliases (avoid very short aliases like "US").
COUNTRY_TEXT_CANDIDATES = sorted(
    set(ALL_WORLD_COUNTRIES + [a for a in COUNTRY_ALIASES.keys() if len(a) > 2]),
    key=len,
    reverse=True,
)


class NewsNLPProcessor:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    def _extract_risk_signals(self, text: str) -> List[str]:
        """Extract logistics risk signals only. Returns empty if none found."""
        t = (text or "").lower()
        signals = []
        for signal_name, keywords in LOGISTICS_RISK_SIGNALS.items():
            if any(kw in t for kw in keywords):
                signals.append(signal_name)
        return signals[:5]

    def _extract_chokepoint_mentions(self, text: str) -> List[str]:
        """Detect mentions of major maritime chokepoints."""
        t = (text or "").lower()
        hits = []
        for location in CHOKEPOINT_LOCATION_COUNTRIES:
            if location in t:
                hits.append(location)
        return hits

    def _compute_risk_score(self, text: str, signals: List[str]) -> int:
        """Assign risk score 1-5 based on content and signals."""
        score = 1
        t = (text or "").lower()

        # Critical logistics signals
        if any(s in ["canal blockage", "maritime attack", "maritime accident", "oil supply disruption", "maritime chokepoint"] for s in signals):
            score += 2
        if any(s in ["shipping delays", "port congestion", "cargo disruption", "container shortage", "transport disruption"] for s in signals):
            score += 1

        # Keywords that boost score
        high = ["blockage", "strike", "attack", "sanctions", "ban", "critical", "closure"]
        med = ["delay", "disruption", "backlog", "congestion", "restriction"]
        if any(k in t for k in high):
            score += 2
        elif any(k in t for k in med):
            score += 1

        return min(max(score, 1), 5)

    def _risk_severity(self, score: int) -> str:
        if score >= 4:
            return "critical"
        if score == 3:
            return "high"
        if score == 2:
            return "medium"
        return "low"

    def _simple_summary(self, title: str, description: str, content: str) -> str:
        """Fallback summary when LLM is not available."""
        if description and len(description) > 50:
            return description[:300] + ("..." if len(description) > 300 else "")
        text = (content or title or "").strip()
        if len(text) > 300:
            return text[:300] + "..."
        return text or title

    async def _llm_summarize_and_score(
        self, title: str, description: str, content: str, signals: List[str]
    ) -> tuple[str, int]:
        """Use OpenAI or Anthropic to summarize and refine risk score."""
        prompt = f"""Analyze this supply chain news and return ONLY a JSON object with two keys:
- "summary": A 1-2 sentence summary of the disruption impact (max 150 chars)
- "risk_score": Integer 1-5 (1=low, 5=critical)

Title: {title}
Description: {description}
Content: {(content or description or title)[:500]}

Detected risk signals: {', '.join(signals)}

Respond with valid JSON only, no markdown."""

        # Try OpenAI first
        if self.openai_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.openai_key)
                resp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                )
                import json
                text = resp.choices[0].message.content or "{}"
                text = text.strip().removeprefix("```json").removeprefix("```").strip()
                obj = json.loads(text)
                return (
                    obj.get("summary", self._simple_summary(title, description, content)),
                    min(max(int(obj.get("risk_score", 2)), 1), 5),
                )
            except Exception as e:
                print(f"OpenAI summarize error: {e}")

        # Try Anthropic
        if self.anthropic_key:
            try:
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic()
                resp = await client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                )
                import json
                text = (resp.content[0].text if resp.content else "{}").strip()
                text = text.strip().removeprefix("```json").removeprefix("```").strip()
                obj = json.loads(text)
                return (
                    obj.get("summary", self._simple_summary(title, description, content)),
                    min(max(int(obj.get("risk_score", 2)), 1), 5),
                )
            except Exception as e:
                print(f"Anthropic summarize error: {e}")

        return self._simple_summary(title, description, content), 2

    def _extract_location(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract country, city, port from article text using ports and direct country mentions."""
        t = text or ""
        country, city, port = None, None, None

        # 1) Prefer explicit port/city mappings first.
        for place_key, c in PORT_TO_COUNTRY.items():
            if re.search(rf"\b{re.escape(place_key)}\b", t, re.I):
                country = get_canonical_country(c)
                port = place_key.title()
                break

        # 2) Fallback to direct country detection in article text.
        if not country:
            for name in COUNTRY_TEXT_CANDIDATES:
                if re.search(rf"\b{re.escape(name)}\b", t, re.I):
                    country = get_canonical_country(name)
                    break

        # 3) Fallback to chokepoint region mapping.
        if not country:
            chokepoints = self._extract_chokepoint_mentions(t)
            if chokepoints:
                primary = chokepoints[0]
                mapped_countries = CHOKEPOINT_LOCATION_COUNTRIES.get(primary, [])
                if mapped_countries:
                    country = get_canonical_country(mapped_countries[0])
                    port = primary.title()

        return (country, city, port)

    def _extract_trigger_keywords(self, title: str, description: str) -> List[str]:
        """Detect disruption trigger keywords in title/description."""
        td = f"{title or ''} {description or ''}".lower()
        return [kw for kw in DISRUPTION_TRIGGER_KEYWORDS if kw in td]

    def _assign_category(self, text: str, signals: List[str]) -> str:
        """Assign category: maritime | freight | port disruption | customs delay"""
        t = (text or "").lower()
        if any(s in signals for s in ["canal blockage", "maritime attack", "maritime accident", "vessel rerouting"]):
            return "maritime"
        if any(k in t for k in ["freight", "cargo", "shipment", "transport"]) or "shipping delays" in signals or "cargo disruption" in signals:
            return "freight"
        if any(s in signals for s in ["port congestion", "logistics strike"]) or "port" in t:
            return "port disruption"
        if any(s in signals for s in ["customs hold", "trade sanctions", "export ban", "import restriction"]) or "customs" in t:
            return "customs delay"
        return "freight"  # default

    async def process_article(self, article: Dict[str, Any]) -> Optional[SupplyChainNewsAlert]:
        """Process raw article. Discard if no logistics risk signals."""
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "") or description
        url = article.get("url", "")
        source = article.get("source", "Unknown")
        published_at = article.get("published_at", "")

        if not title and not description:
            return None

        text = f"{title} {description} {content}"
        signals = self._extract_risk_signals(text)
        chokepoint_mentions = self._extract_chokepoint_mentions(text)
        if chokepoint_mentions and "maritime chokepoint" not in signals:
            signals.append("maritime chokepoint")
        trigger_signals = self._extract_trigger_keywords(title, description)
        for kw in trigger_signals:
            if kw not in signals:
                signals.append(kw)

        # Discard if no logistics risk signals
        if not signals:
            return None

        base_score = self._compute_risk_score(text, signals)
        # If trigger keywords appear in title/description, disruptions should be medium+.
        if trigger_signals:
            base_score = max(base_score, 3)

        # Chokepoint mentions indicate globally sensitive disruptions.
        if chokepoint_mentions:
            base_score = min(max(base_score, 3) + 1, 5)

        country, city, port = self._extract_location(text)

        # Boost impact around major trade hubs and energy exporters.
        if country and get_canonical_country(country) in HIGH_IMPACT_COUNTRIES:
            base_score = min(base_score + 1, 5)

        summary, risk_score = await self._llm_summarize_and_score(
            title, description, content, signals
        )
        risk_score = max(base_score, risk_score or 0)
        if trigger_signals:
            risk_score = max(risk_score, 3)
        category = self._assign_category(text, signals)

        return SupplyChainNewsAlert(
            alert_id=str(uuid.uuid4()),
            title=title[:200],
            summary=summary[:500],
            source_url=url,
            source_name=source if isinstance(source, str) else str(source),
            published_at=published_at,
            risk_score=risk_score,
            risk_severity=self._risk_severity(risk_score),
            risk_signals=signals,
            category=category,
            country=country,
            city=city,
            port=port,
        )
