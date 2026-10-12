"""
Pydantic Schemas for Brand Protection AI.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator

class BrandProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Brand or organization name")
    logo: Optional[str] = Field(None, description="Data URL or path to logo preview")
    website: Optional[str] = Field(None, description="Official brand website URL")
    description: Optional[str] = Field(None, max_length=2000, description="Brand description and official markers")

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            v = f"https://{v}"
        return v

class ProviderConfigRequest(BaseModel):
    provider: str = Field(..., description="Provider name: openai, gemini, anthropic, ollama, custom, demo")
    api_key: Optional[str] = Field(None, description="Masked/submitted API key")
    model: Optional[str] = Field(None, description="Model identifier")
    base_url: Optional[str] = Field(None, description="Custom or Ollama base endpoint")

class ProviderStatusResponse(BaseModel):
    provider: str
    model: str
    is_local: bool
    connected: bool
    message: str

class EvidenceItem(BaseModel):
    id: str
    source_name: str
    source_type: str  # web, social, app_store, patent
    title: str
    url: str
    snippet: str
    timestamp: Optional[str] = None
    is_official: bool = False
    status: str = Field("Needs review", description="Verified, Possible match, Needs review, No evidence")
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reason: str

class AnalysisRequest(BaseModel):
    name: str
    logo: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class AnalysisResponse(BaseModel):
    brand_name: str
    provider_used: str
    model_used: str
    is_demo: bool
    summary: str
    total_checked: int
    sources_checked: List[str]
    items: List[EvidenceItem]

class PatentRecord(BaseModel):
    id: str
    title: str
    record_type: str  # Trademark, Patent, Copyright
    identifier: str
    owner: str
    registration_date: str
    source_url: str
    status: str
    relevance_explanation: str

class SourceItem(BaseModel):
    id: str
    name: str
    category: str
    description: str
    enabled: bool
    status: str
