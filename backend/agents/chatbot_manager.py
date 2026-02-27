from typing import Literal

class ChatbotManager:
    """Simple intent router enforcing supply chain risk-only policy."""

    def classify_intent(self, text: str) -> Literal[
        "political", "schedule", "combined", "assistant", "reject"]:
        t = (text or "").lower()
        allowed = any(x in t for x in [
            "supply", "chain", "risk", "political", "geopolit", "tariff", "sanction",
            "schedule", "delivery", "delay", "logistics", "shipping", "transport",
            "report", "equipment", "supplier", "country", "trade", "from", "to", "route"
        ])
        if not allowed:
            return "reject"
        
        # Route analysis queries go to assistant
        if any(x in t for x in ["from", "to", "route", "transit", "voyage", "port", "ocean", "maritime"]):
            return "assistant"
            
        if "combined" in t or ("report" in t and ("both" in t or "all" in t)):
            return "combined"
        if "political" in t or "geopolit" in t or "tariff" in t or "sanction" in t:
            return "political"
        if "schedule" in t or "delivery" in t or "delay" in t or "logistics" in t or "shipping" in t:
            return "schedule"
        if "report" in t:
            return "combined"
        return "assistant"



