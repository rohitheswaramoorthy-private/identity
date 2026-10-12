"""
Comprehensive test suite for IdentityAI backend.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["service"] == "identity-ai"

def test_provider_status_default():
    res = client.get("/api/providers/status")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "ollama"
    assert data["is_local"] is True

def test_provider_models():
    res = client.get("/api/providers/models?provider=openai")
    assert res.status_code == 200
    assert "gpt-4o-mini" in res.json()["models"]

def test_provider_test_missing_key():
    res = client.post("/api/providers/test", json={"provider": "openai", "api_key": ""})
    assert res.status_code == 200
    assert res.json()["success"] is False
    assert "API key is missing" in res.json()["message"]

def test_ollama_scan_permission_required():
    # Attempting to scan without permission yields 403
    res = client.post("/api/providers/ollama/scan", json={"permission_granted": False})
    assert res.status_code == 403
    assert "permission is required" in res.json()["detail"]

def test_ollama_scan_with_permission():
    # Scanning with explicit user permission executes cleanly
    res = client.post("/api/providers/ollama/scan", json={"permission_granted": True, "base_url": "http://localhost:11434"})
    assert res.status_code == 200
    assert "running" in res.json()
    assert "installed_models" in res.json()

def test_add_custom_source():
    payload = {
        "name": "Acme Brand Registry",
        "category": "Corporate Registry",
        "url": "https://registry.acme.internal",
        "description": "Internal monitoring database of authorized distributor partners."
    }
    res = client.post("/api/sources/add", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Acme Brand Registry"
    assert data["id"].startswith("custom_")
    assert data["enabled"] is True

    # Verify it now appears in all sources list
    sources_res = client.get("/api/sources")
    assert any(s["id"] == data["id"] for s in sources_res.json())

def test_analysis_validation_failure():
    res = client.post("/api/analysis", json={"name": ""})
    assert res.status_code == 422

def test_analysis_flow():
    payload = {
        "name": "AcmeCorp",
        "website": "https://acmecorp.com",
        "description": "Enterprise cloud identity provider."
    }
    res = client.post("/api/analysis", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["brand_name"] == "AcmeCorp"
    assert len(data["items"]) > 0

    # Verify official website is never marked as scam
    official_items = [i for i in data["items"] if i["is_official"]]
    assert len(official_items) >= 1
    assert official_items[0]["status"] == "Verified"

def test_patents_records():
    res = client.get("/api/patents?brand=AcmeCorp")
    assert res.status_code == 200
    records = res.json()
    assert len(records) > 0
    assert any(r["record_type"] == "Trademark" for r in records)

def test_frontend_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "IdentityAI" in res.text
    assert "card-name" in res.text
    assert "card-logo" in res.text
    assert "card-web" in res.text
    assert "card-desc" in res.text
    assert "Demo Mode" not in res.text
