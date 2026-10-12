"""
AI Provider Settings API routes.
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional, Dict, Any, List
from backend.models import ProviderConfigRequest, ProviderStatusResponse
from backend.config import (
    get_or_create_session,
    set_session_provider_config,
    get_session_provider_config,
    clear_session_provider_config
)
from backend.providers import get_provider_adapter, SUPPORTED_MODELS
from backend.providers.ollama_adapter import OllamaAdapter

router = APIRouter(prefix="/api/providers", tags=["providers"])

@router.get("/status", response_model=ProviderStatusResponse)
async def get_status(x_session_id: Optional[str] = Header(None)):
    session_id = get_or_create_session(x_session_id)
    cfg = get_session_provider_config(session_id)
    provider_name = cfg.get("provider", "demo")
    model_name = cfg.get("model", "")
    is_local = provider_name in ["demo", "ollama"]
    
    return ProviderStatusResponse(
        provider=provider_name,
        model=model_name or ("local" if is_local else "default"),
        is_local=is_local,
        connected=cfg.get("connected", False),
        message="Connected" if cfg.get("connected") else "Not configured"
    )

@router.get("/models")
async def get_models(provider: str = "demo", base_url: Optional[str] = None):
    provider_lower = provider.lower()
    models = SUPPORTED_MODELS.get(provider_lower, ["default"])
    if provider_lower == "ollama":
        adapter = OllamaAdapter(base_url=base_url or "http://localhost:11434")
        installed = await adapter.get_installed_models()
        if installed:
            return {"models": installed, "installed": True}
    return {"models": models, "installed": False}

@router.post("/test")
async def test_provider(req: ProviderConfigRequest):
    adapter = get_provider_adapter(
        provider=req.provider,
        api_key=req.api_key or "",
        model=req.model or "",
        base_url=req.base_url or ""
    )
    success, message = await adapter.test_connection()
    return {
        "success": success,
        "message": message,
        "is_local": req.provider.lower() in ["demo", "ollama"]
    }

@router.post("/configure")
async def configure_provider(req: ProviderConfigRequest, x_session_id: Optional[str] = Header(None)):
    session_id = get_or_create_session(x_session_id)
    adapter = get_provider_adapter(
        provider=req.provider,
        api_key=req.api_key or "",
        model=req.model or "",
        base_url=req.base_url or ""
    )
    success, message = await adapter.test_connection()
    if not success and req.provider.lower() not in ["demo"]:
        raise HTTPException(status_code=400, detail=message)
        
    set_session_provider_config(
        session_id=session_id,
        provider=req.provider.lower(),
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url,
        connected=True
    )
    
    return {
        "session_id": session_id,
        "provider": req.provider.lower(),
        "model": req.model,
        "connected": True,
        "message": message
    }

@router.post("/disconnect")
async def disconnect_provider(x_session_id: Optional[str] = Header(None)):
    session_id = get_or_create_session(x_session_id)
    clear_session_provider_config(session_id)
    return {"success": True, "message": "Provider disconnected and key purged from memory."}
