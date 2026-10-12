"""
Provider registry and factory for IdentityAI.
"""

from typing import Dict, Any, Type
from backend.providers.base import BaseProviderAdapter
from backend.providers.openai_adapter import OpenAIAdapter
from backend.providers.gemini_adapter import GeminiAdapter
from backend.providers.anthropic_adapter import AnthropicAdapter
from backend.providers.ollama_adapter import OllamaAdapter

PROVIDERS_REGISTRY: Dict[str, Type[BaseProviderAdapter]] = {
    "ollama": OllamaAdapter,
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "anthropic": AnthropicAdapter,
}

SUPPORTED_MODELS = {
    "ollama": ["llama3.2", "mistral", "qwen2.5", "llama3.1", "deepseek-r1", "phi3"],
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o3-mini"],
    "gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
}

def get_provider_adapter(
    provider: str,
    api_key: str = "",
    model: str = "",
    base_url: str = ""
) -> BaseProviderAdapter:
    provider_clean = (provider or "ollama").lower()
    if provider_clean == "openai":
        return OpenAIAdapter(api_key=api_key, model=model or "gpt-4o-mini", base_url=base_url)
    elif provider_clean == "gemini":
        return GeminiAdapter(api_key=api_key, model=model or "gemini-2.0-flash", base_url=base_url)
    elif provider_clean == "anthropic":
        return AnthropicAdapter(api_key=api_key, model=model or "claude-3-5-sonnet-20241022", base_url=base_url)
    elif provider_clean == "ollama":
        return OllamaAdapter(model=model or "llama3.2", base_url=base_url or "http://localhost:11434")
    else:
        # Default to local Ollama adapter
        return OllamaAdapter(model=model or "llama3.2", base_url=base_url or "http://localhost:11434")
