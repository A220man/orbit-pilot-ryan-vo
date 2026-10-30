"""Tests for the validator CLI."""
import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from app.cli.validate import app


def test_validate_finding_valid():
    """Test validating a valid finding."""
    runner = CliRunner()
    
    finding_data = {
        "unit_id": "auth-bypass-001",
        "title": "Authentication bypass via JWT algorithm confusion",
        "description": "The API accepts JWT tokens with 'none' algorithm, allowing authentication bypass.",
        "attack_class": "authentication_bypass",
        "status": "confirmed",
        "severity": "critical",
        "cwe": ["CWE-347", "CWE-287"],
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
        "cvss_version": "3.1",
        "references": [
            {"url": "https://cwe.mitre.org/data/definitions/347.html", "description": "CWE-347"}
        ],
        "evidence": {"request": "POST /api/verify-token"},
        "remediation": {"summary": "Enforce RS256 algorithm"},
        "preserved_uses": [],
        "method_backed": True,
        "source_trace": {"tool": "manual"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(finding_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["finding", temp_path])
        assert result.exit_code == 0
        assert "Valid as FindingCreate" in result.output
        assert "Validation passed" in result.output
    finally:
        Path(temp_path).unlink()


def test_validate_finding_invalid():
    """Test validating an invalid finding (missing required fields)."""
    runner = CliRunner()
    
    finding_data = {
        "title": "Missing unit_id",
        "description": "This finding is missing required fields",
        "attack_class": "test",
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(finding_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["finding", temp_path])
        assert result.exit_code != 0
        assert "Error" in result.output or "validation failed" in result.output.lower()
    finally:
        Path(temp_path).unlink()


def test_validate_coverage_valid():
    """Test validating a valid coverage ledger."""
    runner = CliRunner()
    
    coverage_data = {
        "units": [
            {
                "unit_id": "auth-001",
                "title": "Authentication module",
                "attack_class": "authentication",
                "status": "planned",
                "files": ["auth/login.py", "auth/jwt.py"],
                "assigned_to": "analyst-1"
            }
        ],
        "attempts": [
            {
                "attempt_id": 1,
                "phase": "recon",
                "units_targeted": ["auth-001"],
                "units_completed": ["auth-001"],
                "artifacts": [{"type": "swagger", "path": "/tmp/swagger.json"}]
            }
        ],
        "promoted_artifacts": {
            "swagger": "/tmp/swagger.json"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coverage_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["coverage", temp_path])
        assert result.exit_code == 0
        assert "Valid as CoverageLedgerBase" in result.output
        assert "Validation passed" in result.output
    finally:
        Path(temp_path).unlink()


def test_validate_coverage_invalid():
    """Test validating an invalid coverage ledger."""
    runner = CliRunner()
    
    coverage_data = {
        "units": [
            {
                "unit_id": "auth-001",
                "title": "Missing attack_class and status",
            }
        ],
        "attempts": [],
        "promoted_artifacts": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coverage_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["coverage", temp_path])
        assert result.exit_code != 0
    finally:
        Path(temp_path).unlink()


def test_validate_finding_warnings():
    """Test that warnings are shown for non-standard CVSS vector."""
    runner = CliRunner()
    
    finding_data = {
        "unit_id": "test-001",
        "title": "Test finding",
        "description": "Test",
        "attack_class": "test",
        "cvss_vector": "INVALID_VECTOR",
        "cwe": ["INVALID-CWE"],
        "references": [{}],
        "evidence": {},
        "remediation": {},
        "preserved_uses": [],
        "method_backed": False,
        "source_trace": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(finding_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["finding", temp_path])
        # Should pass validation but show warnings
        assert result.exit_code == 0
        assert "Warnings:" in result.output
        assert "CVSS vector should start with" in result.output
        assert "CWE ID should start with" in result.output
        assert "Reference missing 'url' field" in result.output
    finally:
        Path(temp_path).unlink()


def test_validate_finding_strict_mode():
    """Test strict mode treats warnings as errors."""
    runner = CliRunner()
    
    finding_data = {
        "unit_id": "test-001",
        "title": "Test finding",
        "description": "Test",
        "attack_class": "test",
        "cvss_vector": "INVALID_VECTOR",
        "cwe": ["INVALID-CWE"],
        "references": [{}],
        "evidence": {},
        "remediation": {},
        "preserved_uses": [],
        "method_backed": False,
        "source_trace": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(finding_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["finding", temp_path, "--strict"])
        assert result.exit_code != 0
        assert "Strict mode: warnings treated as errors" in result.output
    finally:
        Path(temp_path).unlink()


def test_validate_coverage_duplicate_unit_ids():
    """Test warning for duplicate unit IDs."""
    runner = CliRunner()
    
    coverage_data = {
        "units": [
            {
                "unit_id": "auth-001",
                "title": "Auth module 1",
                "attack_class": "authentication",
                "status": "planned",
                "files": [],
            },
            {
                "unit_id": "auth-001",  # Duplicate
                "title": "Auth module 2",
                "attack_class": "authentication",
                "status": "planned",
                "files": [],
            }
        ],
        "attempts": [],
        "promoted_artifacts": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coverage_data, f)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["coverage", temp_path])
        assert result.exit_code == 0
        assert "Duplicate unit IDs found" in result.output
    finally:
        Path(temp_path).unlink()
