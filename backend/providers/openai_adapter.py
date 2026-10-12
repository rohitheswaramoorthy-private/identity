"""
OpenAI Provider Adapter.
"""

import httpx
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class OpenAIAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini", base_url: str = ""):
        super().__init__(api_key=api_key, model=model or "gpt-4o-mini", base_url=base_url or "https://api.openai.com/v1")

    async def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "OpenAI API key is missing. Please provide a key in settings."
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(f"{self.base_url.rstrip('/')}/models", headers=headers)
                if res.status_code == 200:
                    return True, "Successfully connected to OpenAI API."
                elif res.status_code == 401:
                    return False, "Invalid OpenAI API key. Check key format and permissions."
                else:
                    return False, f"OpenAI returned HTTP status {res.status_code}"
        except Exception as e:
            return False, f"Connection failed: {str(e)[:100]}"

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
            res["summary"] += " (Demo mode active: No OpenAI API key supplied)"
            return res

        official_domain = urlparse(website).netloc.lower() if website else ""

        system_msg = (
            "You are Brand Protection AI, an expert brand security investigator. "
            "Analyze candidates for brand impersonation, deceptive lookalikes, or trademark misuse. "
            "Never flag official brand properties as impersonation. Be objective, concise, and defensible."
        )

        user_content = f"Brand: {brand_name}\nOfficial Web: {website}\nDescription: {description}\nCandidates:\n"
        for i, item in enumerate(evidence_items):
            user_content += f"[{i}] {item.title} ({item.url}): {item.snippet}\n"

        user_content += "\nProvide a concise 2-sentence summary of potential risks found across the sources."

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": user_content}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.2
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    summary_text = data["choices"][0]["message"]["content"].strip()
                    
                    # Update status for items
                    for item in evidence_items:
                        if official_domain and official_domain in item.url.lower():
                            item.is_official = True
                            item.status = "Verified"
                            item.reason = "Official brand property verified."
                        elif "scam" in item.url.lower() or "fake" in item.title.lower():
                            item.status = "Possible match"
                            item.reason = f"High-risk domain identified by {self.model} analysis."

                    return {
                        "summary": summary_text,
                        "items": evidence_items
                    }
        except Exception:
            pass

        # Fallback to heuristic
        from backend.providers.demo_adapter import DemoAdapter
        return await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
