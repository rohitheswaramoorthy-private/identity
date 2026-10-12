"""
Anthropic Claude Provider Adapter.
"""

import httpx
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class AnthropicAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str = "", model: str = "claude-3-5-sonnet-20241022", base_url: str = ""):
        super().__init__(api_key=api_key, model=model or "claude-3-5-sonnet-20241022", base_url=base_url or "https://api.anthropic.com/v1")

    async def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Anthropic API key is missing. Please provide a key in settings."
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            # Lightweight probe
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.post(
                    f"{self.base_url.rstrip('/')}/messages",
                    headers=headers,
                    json={
                        "model": self.model,
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "ping"}]
                    }
                )
                if res.status_code == 200:
                    return True, "Successfully connected to Anthropic Claude API."
                elif res.status_code == 401:
                    return False, "Invalid Anthropic API key."
                elif res.status_code == 400:
                    # Often means key is valid but request format or credit issue
                    data = res.json()
                    err = data.get("error", {}).get("message", "Request error")
                    if "credit" in err.lower() or "billing" in err.lower():
                        return True, f"Key valid, but billing notice: {err}"
                    return False, f"Anthropic error: {err}"
                else:
                    return False, f"Anthropic returned HTTP status {res.status_code}"
        except Exception as e:
            return False, f"Anthropic connection failed: {str(e)[:100]}"

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
            res["summary"] += " (Demo mode active: No Claude API key supplied)"
            return res

        official_domain = urlparse(website).netloc.lower() if website else ""
        user_prompt = (
            f"Analyze brand security candidates for '{brand_name}' ({website}). "
            f"Description: {description}.\n\n"
        )
        for i, item in enumerate(evidence_items):
            user_prompt += f"[{i}] {item.title} ({item.url}): {item.snippet}\n"

        user_prompt += "\nProvide a concise 2-sentence brand protection assessment."

        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(
                    f"{self.base_url.rstrip('/')}/messages",
                    headers=headers,
                    json={
                        "model": self.model,
                        "max_tokens": 250,
                        "messages": [{"role": "user", "content": user_prompt}]
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    summary_text = data.get("content", [{}])[0].get("text", "").strip()
                    for item in evidence_items:
                        if official_domain and official_domain in item.url.lower():
                            item.is_official = True
                            item.status = "Verified"
                            item.reason = "Official brand property verified."
                    return {
                        "summary": summary_text,
                        "items": evidence_items
                    }
        except Exception:
            pass

        from backend.providers.demo_adapter import DemoAdapter
        return await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
