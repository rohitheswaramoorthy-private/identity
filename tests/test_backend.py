"""
Comprehensive test suite for Brand Protection AI backend.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_provider_status_default():
    res = client.get("/api/providers/status")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "demo"
    assert data["is_local"] is True
    assert data["connected"] is True

def test_provider_models():
    res = client.get("/api/providers/models?provider=openai")
    assert res.status_code == 200
    assert "gpt-4o-mini" in res.json()["models"]

def test_provider_test_demo():
    res = client.post("/api/providers/test", json={"provider": "demo"})
    assert res.status_code == 200
    assert res.json()["success"] is True

def test_provider_test_missing_key():
    res = client.post("/api/providers/test", json={"provider": "openai", "api_key": ""})
    assert res.status_code == 200
    assert res.json()["success"] is False
    assert "API key is missing" in res.json()["message"]

def test_analysis_validation_failure():
    res = client.post("/api/analysis", json={"name": ""})
    assert res.status_code == 422

def test_analysis_demo_flow():
    payload = {
        "name": "AcmeCorp",
        "website": "https://acmecorp.com",
        "description": "Enterprise cloud security provider."
    }
    res = client.post("/api/analysis", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["brand_name"] == "AcmeCorp"
    assert data["is_demo"] is True
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

def test_sources_toggle():
    res = client.get("/api/sources")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 3

    # Toggle one
    toggle_res = client.post("/api/sources/toggle", json={"source_id": "app_store", "enabled": False})
    assert toggle_res.status_code == 200
    assert toggle_res.json()["source"]["enabled"] is False

    # Restore
    client.post("/api/sources/toggle", json={"source_id": "app_store", "enabled": True})

def test_frontend_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Brand Protection AI" in res.text
    assert "card-name" in res.text
    assert "card-logo" in res.text
    assert "card-web" in res.text
    assert "card-desc" in res.text

