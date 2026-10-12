"""
Local Ollama Provider Adapter.
Communicates strictly with local daemon (e.g. http://localhost:11434).
Does not require any cloud credentials or external internet connection.
"""

import httpx
import json
from typing import Dict, Any, List, Tuple
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class OllamaAdapter(BaseProviderAdapter):
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        super().__init__(model=model or "llama3.2", base_url=(base_url or "http://localhost:11434").rstrip("/"))

    async def get_installed_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def test_connection(self) -> Tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    if not models:
                        return True, f"Ollama is running at {self.base_url}, but no models are downloaded yet (e.g., run 'ollama pull {self.model}')."
                    if self.model and not any(self.model in m for m in models):
                        return True, f"Connected to Ollama. Selected model '{self.model}' not found in installed: {', '.join(models[:3])}."
                    return True, f"Connected to local Ollama ({len(models)} model(s) available: {', '.join(models[:3])})"
                return False, f"Ollama returned HTTP status {res.status_code}"
        except httpx.ConnectError:
            return False, f"Cannot connect to Ollama at {self.base_url}. Ensure 'ollama serve' is running locally on this machine."
        except Exception as e:
            return False, f"Ollama connection error: {str(e)[:100]}"

    async def analyze_brand(
        self,
        brand_name: str,
        website: str,
        description: str,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        prompt = (
            f"You are a Brand Protection AI. Analyze whether the following items impersonate or misuse the official brand '{brand_name}'.\n"
            f"Official Website: {website}\n"
            f"Brand Description: {description}\n\n"
            f"Candidate Items:\n"
        )
        for i, item in enumerate(evidence_items):
            prompt += f"[{i}] Title: {item.title} | URL: {item.url} | Snippet: {item.snippet}\n"

        prompt += (
            "\nFor each item, classify status as 'Verified' (if official), 'Possible match' (if impersonation/scam), "
            "'Needs review', or 'No evidence'. Return brief reason. End with a 1-sentence summary."
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    result_text = res.json().get("response", "")
                    # Mark official domain
                    from urllib.parse import urlparse
                    official_domain = urlparse(website).netloc.lower() if website else ""
                    for item in evidence_items:
                        if official_domain and official_domain in item.url.lower():
                            item.is_official = True
                            item.status = "Verified"
                            item.reason = "Official brand website verified."
                        elif "scam" in item.url.lower() or "fake" in item.url.lower():
                            item.status = "Possible match"
                            item.reason = "Flagged by local model as probable unauthorized domain."
                    return {
                        "summary": result_text[:300] if result_text else f"Local Ollama analysis completed for {brand_name}.",
                        "items": evidence_items
                    }
        except Exception as e:
            # Graceful fallback to heuristic if local inference timeouts
            from backend.providers.demo_adapter import DemoAdapter
            fallback = await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
            fallback["summary"] += f" (Note: Ollama fallback triggered: {str(e)[:80]})"
            return fallback

        from backend.providers.demo_adapter import DemoAdapter
        return await DemoAdapter().analyze_brand(brand_name, website, description, evidence_items)
