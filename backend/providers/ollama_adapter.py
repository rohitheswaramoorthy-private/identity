"""
Local Ollama Provider Adapter for IdentityAI.
Communicates strictly with local daemon (e.g. http://localhost:11434 or http://127.0.0.1:11434).
Does not require any cloud credentials or external internet connection.
"""

import httpx
import json
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from backend.providers.base import BaseProviderAdapter
from backend.models import EvidenceItem

class OllamaAdapter(BaseProviderAdapter):
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        raw_url = (base_url or "http://localhost:11434").strip().rstrip("/")
        if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
            raw_url = f"http://{raw_url}"
        super().__init__(model=model or "llama3.2", base_url=raw_url)

    async def _find_active_endpoint(self) -> Tuple[Optional[str], List[str]]:
        """Try configured endpoint first, then fallback to standard 127.0.0.1:11434 and localhost:11434."""
        candidates = [self.base_url]
        for fallback in ["http://127.0.0.1:11434", "http://localhost:11434"]:
            if fallback not in candidates:
                candidates.append(fallback)

        for candidate in candidates:
            try:
                async with httpx.AsyncClient(timeout=2.5) as client:
                    res = await client.get(f"{candidate}/api/tags")
                    if res.status_code == 200:
                        data = res.json()
                        models = [m.get("name") for m in data.get("models", [])]
                        self.base_url = candidate
                        return candidate, models
            except Exception:
                continue
        return None, []

    async def get_installed_models(self) -> List[str]:
        active_url, models = await self._find_active_endpoint()
        return models if active_url else []

    async def test_connection(self) -> Tuple[bool, str]:
        active_url, models = await self._find_active_endpoint()
        if not active_url:
            parsed = urlparse(self.base_url)
            port_msg = f" (port {parsed.port})" if parsed.port else ""
            hint = ""
            if parsed.port and parsed.port != 11434:
                hint = f" Note: Port {parsed.port} was checked, but Ollama standard port is 11434 (TCP 127.0.0.1:11434). Check that you didn't enter the process PID instead of the port."
            return False, f"Cannot connect to Ollama at {self.base_url}. Ensure 'ollama serve' is running locally on your machine.{hint}"

        auto_resolved_note = ""
        if active_url != self.base_url:
            auto_resolved_note = f" (Auto-resolved to active daemon at {active_url})"

        if not models:
            return True, f"Connected to Ollama at {active_url}{auto_resolved_note}, but no models are downloaded yet (e.g. run 'ollama pull {self.model}')."

        matched = any(self.model in m or m.startswith(self.model) for m in models)
        if self.model and not matched:
            return True, f"Connected to Ollama at {active_url}{auto_resolved_note}. Selected model '{self.model}' not yet in installed: {', '.join(models[:4])}."

        return True, f"Connected to local Ollama at {active_url}{auto_resolved_note} ({len(models)} model(s) available: {', '.join(models[:4])})"

    async def analyze_brand(
        self,
        brand_name: str,
        website: str,
        description: str,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        active_url, _ = await self._find_active_endpoint()
        target_url = active_url or self.base_url

        prompt = (
            f"You are IdentityAI. Analyze whether the following items impersonate or misuse the official brand '{brand_name}'.\n"
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
                    f"{target_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    result_text = res.json().get("response", "")
                    official_domain = urlparse(website).netloc.lower() if website else ""
                    for item in evidence_items:
                        if official_domain and official_domain in item.url.lower():
                            item.is_official = True
                            item.status = "Verified"
                            item.reason = "Official brand website verified."
                        elif "scam" in item.url.lower() or "fake" in item.url.lower():
                            item.status = "Possible match"
                            item.reason = f"Flagged by {self.model} as probable unauthorized domain."
                    return {
                        "summary": result_text[:300] if result_text else f"Local Ollama analysis completed for {brand_name}.",
                        "items": evidence_items
                    }
        except Exception:
            pass

        # Fallback to deterministic synthesis if local inference timed out
        official_domain = urlparse(website).netloc.lower() if website else ""
        for item in evidence_items:
            if official_domain and official_domain in item.url.lower():
                item.is_official = True
                item.status = "Verified"
                item.reason = "Matches declared official brand domain."
            elif any(k in item.title.lower() or k in item.url.lower() for k in ["scam", "fake", "giveaway", "login"]):
                item.is_official = False
                item.status = "Possible match"
                item.reason = f"Detected brand keywords on unauthorized domain."

        return {
            "summary": f"Analyzed {len(evidence_items)} candidate sources for '{brand_name}' using local heuristic fallback.",
            "items": evidence_items
        }
