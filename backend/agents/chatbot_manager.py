import re
from typing import Literal

class ChatbotManager:
    """Simple intent router enforcing supply chain risk-only policy."""

    def classify_intent(self, text: str) -> Literal[
        "political", "schedule", "combined", "assistant", "disruption", "reject"]:
        t = (text or "").lower()
        allowed = any(x in t for x in [
            "supply", "chain", "risk", "political", "geopolit", "tariff", "sanction",
            "schedule", "delivery", "delay", "logistics", "shipping", "transport",
            "report", "equipment", "supplier", "country", "trade", "from", "to", "route",
            "disruption", "congestion", "strike", "blockade", "port congestion", "supply chain disruption",
            "customs", "documents", "bill of lading", "invoice", "packing list",
            "air freight", "sea freight", "weather", "typhoon", "hurricane", "cyclone",
            "canal", "suez", "panama", "hormuz", "malacca", "chokepoint", "fuel", "cost", "optimiz", "ai",
        ])
        if not allowed:
            return "reject"
        
        # Route analysis queries go to assistant (use bounded patterns, avoid false match on words like "today").
        route_patterns = [
            r"\broute\b",
            r"\bfrom\b.+\bto\b",
            r"\bshipping route\b",
            r"\btransit\b",
            r"\bvoyage\b",
            r"\bport\b",
            r"\bocean\b",
            r"\bmaritime\b",
        ]
        if any(re.search(p, t) for p in route_patterns):
            return "assistant"

        # Logistics knowledge / strategy queries should be handled by assistant knowledge base.
        if any(
            x in t for x in [
                "documents required",
                "shipping documents",
                "bill of lading",
                "customs clearance",
                "air vs sea",
                "air freight vs sea freight",
                "what affects shipping costs",
                "fuel prices",
                "how can ai",
                "ai predict",
                "optimization advice",
                "route alternatives",
                "reduce supply chain risk",
                "mitigate supply chain risk",
            ]
        ):
            return "assistant"

        if any(
            x in t for x in [
                "disruption",
                "delay",
                "congestion",
                "strike",
                "blockade",
                "port congestion",
                "supply chain disruption",
            ]
        ):
            return "disruption"
            
        if "combined" in t or ("report" in t and ("both" in t or "all" in t)):
            return "combined"
        if "political" in t or "geopolit" in t or "tariff" in t or "sanction" in t:
            return "political"
        if any(x in t for x in ["schedule", "delivery delay", "cargo delay", "shipping delay", "late delivery", "eta", "equipment"]):
            return "schedule"
        if "report" in t:
            return "combined"
        return "assistant"



