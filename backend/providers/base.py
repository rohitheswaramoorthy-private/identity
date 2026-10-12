"""
Abstract base class for AI Provider Adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from backend.models import EvidenceItem

class BaseProviderAdapter(ABC):
    def __init__(self, api_key: str = "", model: str = "", base_url: str = ""):
        self.api_key = api_key or ""
        self.model = model or ""
        self.base_url = base_url or ""

    @abstractmethod
    async def test_connection(self) -> Tuple[bool, str]:
        """Verify provider authentication and model accessibility."""
        pass

    @abstractmethod
    async def analyze_brand(
        self,
        brand_name: str,
        website: str,
        description: str,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        """
        Analyze retrieved candidate evidence against legitimate brand profile.
        Returns synthesis summary and updated item judgments.
        """
        pass
