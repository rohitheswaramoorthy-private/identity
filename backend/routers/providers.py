"""
AI Provider Settings API routes for IdentityAI.
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from backend.models import ProviderConfigRequest, ProviderStatusResponse
from backend.config import (
    get_or_create_session,
    set_session_provider_config,
    get_session_provider_config,
    clear_session_provider_config,
    OLLAMA_BASE_URL
)
from backend.providers import get_provider_adapter, SUPPORTED_MODELS
from backend.providers.ollama_adapter import OllamaAdapter

router = APIRouter(prefix="/api/providers", tags=["providers"])

class OllamaScanRequest(BaseModel):
    permission_granted: bool
    base_url: Optional[str] = OLLAMA_BASE_URL

@router.get("/status", response_model=ProviderStatusResponse)
async def get_status(x_session_id: Optional[str] = Header(None)):
    session_id = get_or_create_session(x_session_id)
    cfg = get_session_provider_config(session_id)
    provider_name = cfg.get("provider", "ollama")
    model_name = cfg.get("model", "llama3.2")
    is_local = (provider_name == "ollama")
    
    return ProviderStatusResponse(
        provider=provider_name,
        model=model_name or "llama3.2",
        is_local=is_local,
        connected=cfg.get("connected", False),
        message="Connected" if cfg.get("connected") else "Not configured"
    )

@router.get("/models")
async def get_models(provider: str = "ollama", base_url: Optional[str] = None):
    provider_lower = provider.lower()
    models = SUPPORTED_MODELS.get(provider_lower, ["custom"])
    return {"models": models, "installed": False}

@router.post("/ollama/scan")
async def scan_ollama_local(req: OllamaScanRequest):
    """
    Explicitly requires user consent before querying the local machine's localhost network.
    Automatically resolves to standard 11434 if an invalid port / PID was provided.
    """
    if not req.permission_granted:
        raise HTTPException(
            status_code=403,
            detail="Scanning aborted: user permission is required to probe local host."
        )

    endpoint = req.base_url or OLLAMA_BASE_URL
    adapter = OllamaAdapter(base_url=endpoint)
    is_connected, msg = await adapter.test_connection()
    installed_models = await adapter.get_installed_models() if is_connected else []

    return {
        "running": is_connected,
        "endpoint": adapter.base_url,
        "message": msg,
        "installed_models": installed_models
    }

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
        "is_local": (req.provider.lower() == "ollama"),
        "resolved_endpoint": getattr(adapter, "base_url", req.base_url)
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
    if not success:
        raise HTTPException(status_code=400, detail=message)
        
    resolved_url = getattr(adapter, "base_url", req.base_url)
    set_session_provider_config(
        session_id=session_id,
        provider=req.provider.lower(),
        api_key=req.api_key,
        model=req.model,
        base_url=resolved_url,
        connected=True
    )
    
    return {
        "session_id": session_id,
        "provider": req.provider.lower(),
        "model": req.model,
        "base_url": resolved_url,
        "connected": True,
        "message": message
    }

@router.post("/disconnect")
async def disconnect_provider(x_session_id: Optional[str] = Header(None)):
    session_id = get_or_create_session(x_session_id)
    clear_session_provider_config(session_id)
    return {"success": True, "message": "Provider disconnected and key purged from memory."}
