import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "environment" in data


def test_create_audit_run(client: TestClient):
    payload = {
        "name": "Test Audit",
        "target_path": "/path/to/target",
        "profile": "standard",
        "config": {"key": "value"}
    }
    response = client.post("/api/v1/audits", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Audit"
    assert data["target_path"] == "/path/to/target"
    assert data["profile"] == "standard"
    assert data["status"] == "draft"
    assert "id" in data


def test_list_audit_runs(client: TestClient):
    # Create one first
    client.post("/api/v1/audits", json={
        "name": "Test Audit 2",
        "target_path": "/path/to/target2",
        "profile": "quick"
    })
    
    response = client.get("/api/v1/audits")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_audit_run(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 3",
        "target_path": "/path/to/target3",
        "profile": "deep"
    })
    audit_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/audits/{audit_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == audit_id
    assert data["name"] == "Test Audit 3"


def test_update_audit_run(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 4",
        "target_path": "/path/to/target4",
        "profile": "standard"
    })
    audit_id = create_resp.json()["id"]
    
    response = client.patch(f"/api/v1/audits/{audit_id}", json={
        "name": "Updated Name",
        "status": "running"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "running"
    assert data["started_at"] is not None


def test_create_finding(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 5",
        "target_path": "/path/to/target5",
        "profile": "standard"
    })
    audit_id = create_resp.json()["id"]
    
    finding_payload = {
        "unit_id": "auth-bypass-001",
        "title": "Authentication Bypass",
        "description": "Possible auth bypass in login flow",
        "attack_class": "authentication",
        "severity": "high",
        "cwe": ["CWE-287"],
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
        "cvss_version": "3.1",
        "references": [{"url": "https://cwe.mitre.org/data/definitions/287.html"}],
        "evidence": {"file": "auth.py", "line": 42},
        "remediation": {"strategy": "add_rate_limiting", "details": "Add rate limiting to login"},
        "preserved_uses": [{"who": "legitimate_users", "path": "login", "how_it_keeps_working": "rate limit allows normal use"}],
        "method_backed": True,
        "source_trace": {"agent": "hunter-1", "model": "gpt-4o-mini"}
    }
    response = client.post(f"/api/v1/audits/{audit_id}/findings", json=finding_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["unit_id"] == "auth-bypass-001"
    assert data["title"] == "Authentication Bypass"
    assert data["status"] == "planned"
    assert data["cwe"] == ["CWE-287"]
    assert data["cvss_vector"] == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N"


def test_list_findings(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 6",
        "target_path": "/path/to/target6",
        "profile": "standard"
    })
    audit_id = create_resp.json()["id"]
    
    client.post(f"/api/v1/audits/{audit_id}/findings", json={
        "unit_id": "finding-1",
        "title": "Finding 1",
        "description": "Description 1",
        "attack_class": "injection",
        "severity": "critical"
    })
    
    response = client.get(f"/api/v1/audits/{audit_id}/findings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_coverage_ledger(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 7",
        "target_path": "/path/to/target7",
        "profile": "standard"
    })
    audit_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/audits/{audit_id}/coverage")
    assert response.status_code == 200
    data = response.json()
    assert data["audit_run_id"] == audit_id
    assert "units" in data
    assert "attempts" in data
    assert "promoted_artifacts" in data


def test_get_audit_logs(client: TestClient):
    create_resp = client.post("/api/v1/audits", json={
        "name": "Test Audit 8",
        "target_path": "/path/to/target8",
        "profile": "standard"
    })
    audit_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/audits/{audit_id}/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the creation log
    assert data[0]["action"] == "created"