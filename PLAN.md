# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

continue-implementation

## Roadmap

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature

Implementation: `backend/pyproject.toml`, `backend/app/api/v1/audits.py`, `backend/app/cli/validate.py`

Tests: `backend/tests/test_health.py`, `backend/tests/test_cli_validate.py`, `frontend/src/__tests__/App.test.tsx`

### add-audit-run-endpoint — POST /api/v1/audits/{id}/run endpoint

Status: planned

Acceptance:
- Start audit run transitions status to "running"
- Records started_at timestamp
- Returns updated audit run

### implement-multi-phase-audit — Multi-phase audit execution engine

Status: planned

Acceptance:
- Phase 1: Reconnaissance - discover attack surface
- Phase 2: Hunting - execute unit tests against findings
- Phase 3: Validation - verify findings independently
- Phase 4: Reporting - generate artifacts

### add-llm-adapter — LLM provider abstraction

Status: planned

Acceptance:
- OpenAI-compatible adapter
- Anthropic adapter
- Ollama adapter
- Configurable via env vars

### add-keycloak-auth — OIDC authentication with Keycloak

Status: planned

Acceptance:
- JWT validation middleware
- Role-based access (viewer, operator, admin)
- Protected API endpoints (except /health)

