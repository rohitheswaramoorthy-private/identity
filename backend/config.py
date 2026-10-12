"""
Configuration and Session-based Security for IdentityAI.
API keys are kept strictly in server memory per session and NEVER logged, persisted, or returned to clients.
"""

import os
import secrets
from typing import Dict, Optional, Any

DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# In-memory store for active session provider credentials
# Structure: { session_id: { "provider": str, "api_key": Optional[str], "model": str, "base_url": Optional[str], "connected": bool } }
_SESSION_STORE: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: Optional[str]) -> str:
    """Validate or generate a new cryptographically secure session ID."""
    if not session_id or session_id not in _SESSION_STORE:
        new_id = secrets.token_hex(16)
        _SESSION_STORE[new_id] = {
            "provider": "ollama",
            "api_key": None,
            "model": "llama3.2",
            "base_url": OLLAMA_BASE_URL,
            "connected": False
        }
        return new_id
    return session_id

def set_session_provider_config(
    session_id: str,
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    connected: bool = False
) -> None:
    """Store provider credentials strictly in server memory."""
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = {}
        
    _SESSION_STORE[session_id].update({
        "provider": provider,
        "api_key": api_key,
        "model": model or "",
        "base_url": base_url or (OLLAMA_BASE_URL if provider == "ollama" else None),
        "connected": connected
    })

def get_session_provider_config(session_id: str) -> Dict[str, Any]:
    """Retrieve session provider credentials (internal backend use only)."""
    return _SESSION_STORE.get(session_id, {
        "provider": "ollama",
        "api_key": None,
        "model": "llama3.2",
        "base_url": OLLAMA_BASE_URL,
        "connected": False
    })

def clear_session_provider_config(session_id: str) -> None:
    """Explicitly wipe provider credentials for the session."""
    if session_id in _SESSION_STORE:
        _SESSION_STORE[session_id] = {
            "provider": "ollama",
            "api_key": None,
            "model": "llama3.2",
            "base_url": OLLAMA_BASE_URL,
            "connected": False
        }
