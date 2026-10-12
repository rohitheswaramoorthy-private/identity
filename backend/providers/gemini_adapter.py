"""
Google Gemini Provider Adapter.
"""

import httpx
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class GeminiAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str = "", model: str = "gemini-2.0-flash", base_url: str = ""):
        super().__init__(api_key=api_key, model=model or "gemini-2.0-flash", base_url=base_url)

    async def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Google Gemini API key is missing. Please provide a key in settings."
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return True, "Successfully connected to Google Gemini API."
                elif res.status_code == 400 or res.status_code == 403:
                    return False, "Invalid Gemini API key or insufficient permissions."
                else:
                    return False, f"Gemini returned HTTP status {res.status_code}"
        except Exception as e:
            return False, f"Gemini connection failed: {str(e)[:100]}"

    async def analyze_brand(
        self,
        brand_name: str,
        website: str,
        description: str,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        if not self.api_key:
            from backend.providers.demo_adapter import DemoAdapter
            res = await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
            res["summary"] += " (Demo mode active: No Gemini API key supplied)"
            return res

        official_domain = urlparse(website).netloc.lower() if website else ""
        prompt_text = (
            f"You are Brand Protection AI. Analyze potential brand impersonation for: '{brand_name}'.\n"
            f"Official website: {website}\nDescription: {description}\n\n"
            "Candidates:\n"
        )
        for i, item in enumerate(evidence_items):
            prompt_text += f"- [{i}] {item.title} ({item.url}): {item.snippet}\n"

        prompt_text += "\nProvide a brief, objective 2-sentence summary of the brand risk profile."

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt_text}]
                        }]
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    summary_text = (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                        .strip()
                    )
                    for item in evidence_items:
                        if official_domain and official_domain in item.url.lower():
                            item.is_official = True
                            item.status = "Verified"
                            item.reason = "Official brand property verified."
                    return {
                        "summary": summary_text or f"Gemini evaluated {len(evidence_items)} sources for {brand_name}.",
                        "items": evidence_items
                    }
        except Exception:
            pass

        from backend.providers.demo_adapter import DemoAdapter
        return await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
