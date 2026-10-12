"""
Analysis Orchestration API Route.
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from backend.models import AnalysisRequest, AnalysisResponse
from backend.config import get_or_create_session, get_session_provider_config
from backend.providers import get_provider_adapter
from backend.search.engine import SearchEngine
from backend.routers.sources import SOURCES_DB

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
search_engine = SearchEngine()

@router.post("", response_model=AnalysisResponse)
async def analyze_brand(req: AnalysisRequest, x_session_id: Optional[str] = Header(None)):
    if not req.name or not req.name.strip():
        raise HTTPException(status_code=422, detail="Brand name is required.")

    session_id = get_or_create_session(x_session_id)
    cfg = get_session_provider_config(session_id)
    
    provider_name = cfg.get("provider", "demo")
    api_key = cfg.get("api_key", "")
    model_name = cfg.get("model", "")
    base_url = cfg.get("base_url", "")
    
    adapter = get_provider_adapter(
        provider=provider_name,
        api_key=api_key,
        model=model_name,
        base_url=base_url
    )

    # Filter enabled sources
    enabled_sources = [s.id for s in SOURCES_DB if s.enabled]
    active_source_names = [s.name for s in SOURCES_DB if s.enabled]

    # Step 1: Real retrieval layer separate from AI
    candidates = await search_engine.retrieve_candidates(
        brand_name=req.name.strip(),
        official_website=req.website,
        enabled_sources=enabled_sources
    )

    # Step 2: AI provider evaluation
    analysis_result = await adapter.analyze_brand(
        brand_name=req.name.strip(),
        website=req.website or "",
        description=req.description or "",
        evidence_items=candidates
    )

    return AnalysisResponse(
        brand_name=req.name.strip(),
        provider_used=provider_name.capitalize(),
        model_used=model_name or "Standard",
        is_demo=(provider_name.lower() == "demo"),
        summary=analysis_result.get("summary", "Analysis completed."),
        total_checked=len(analysis_result.get("items", [])),
        sources_checked=active_source_names,
        items=analysis_result.get("items", [])
    )
