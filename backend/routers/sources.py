"""
Sources Management API routes.
"""

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from backend.models import SourceItem

router = APIRouter(prefix="/api/sources", tags=["sources"])

# In-memory source configuration
SOURCES_DB: List[SourceItem] = [
    SourceItem(
        id="web",
        name="Global Web & Typosquat Registries",
        category="Domain & Web",
        description="Scans newly observed domains, lookalike spellings, and phishing kits.",
        enabled=True,
        status="Active"
    ),
    SourceItem(
        id="app_store",
        name="Apple App Store & Play Services",
        category="App Ecosystem",
        description="Detects unauthorized apps utilizing resembling publisher branding.",
        enabled=True,
        status="Active"
    ),
    SourceItem(
        id="social",
        name="Social Media & Ad Libraries",
        category="Advertising",
        description="Inspects sponsored ad campaigns and imposter high-volume profiles.",
        enabled=True,
        status="Active"
    ),
    SourceItem(
        id="trademark",
        name="USPTO & WIPO IP Databases",
        category="Legal & IP",
        description="Cross-references published wordmarks and design classes.",
        enabled=True,
        status="Active"
    )
]

class ToggleSourceRequest(BaseModel):
    source_id: str
    enabled: bool

@router.get("", response_model=List[SourceItem])
async def list_sources():
    return SOURCES_DB

@router.post("/toggle")
async def toggle_source(req: ToggleSourceRequest):
    for s in SOURCES_DB:
        if s.id == req.source_id:
            s.enabled = req.enabled
            s.status = "Active" if req.enabled else "Disabled"
            return {"success": True, "source": s}
    return {"success": False, "message": "Source not found"}
