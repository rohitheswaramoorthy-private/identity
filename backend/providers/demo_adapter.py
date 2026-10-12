"""
Demo / Simulated Provider Adapter.
Provides deterministic, transparent heuristic analysis without external credentials.
"""

from typing import Dict, Any, List, Tuple
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class DemoAdapter(BaseProviderAdapter):
    def __init__(self, model: str = "demo-heuristic-v1"):
        super().__init__(model=model or "demo-heuristic-v1")

    async def test_connection(self) -> Tuple[bool, str]:
        return True, "Simulated demo provider active (Offline Heuristic Engine)"

    async def analyze_brand(
        self,
        brand_name: str,
        website: str,
        description: str,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        analyzed_items: List[EvidenceItem] = []
        official_domain = ""
        if website:
            from urllib.parse import urlparse
            official_domain = urlparse(website).netloc.lower()

        suspicious_count = 0
        for item in evidence_items:
            # Respect official property
            if official_domain and official_domain in item.url.lower():
                item.is_official = True
                item.status = "Verified"
                item.confidence = 0.98
                item.reason = "Matches declared official brand domain."
            elif any(k in item.title.lower() or k in item.url.lower() for k in ["scam", "fake", "giveaway", "login", "free", "support-desk"]):
                item.is_official = False
                item.status = "Possible match"
                item.confidence = 0.86
                item.reason = f"Uses '{brand_name}' branding on unauthorized domain with high-risk keyword patterns."
                suspicious_count += 1
            elif item.source_type == "app_store":
                item.is_official = False
                item.status = "Needs review"
                item.confidence = 0.65
                item.reason = "Third-party publisher distributing app resembling brand identity."
            else:
                item.is_official = False
                item.status = "Possible match"
                item.confidence = 0.55
                item.reason = "Contains brand keywords or similar visual cues."

            analyzed_items.append(item)

        summary = (
            f"Evaluated {len(analyzed_items)} candidate sources for '{brand_name}'. "
            f"Identified {suspicious_count} high-priority impersonation indicators and distinguished official assets."
        )

        return {
            "summary": summary,
            "items": analyzed_items
        }
