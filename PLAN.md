# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

initial-scaffold

## Roadmap

### initial-scaffold — Initial FastAPI/React scaffold with database and basic API

Status: done

Acceptance:
- FastAPI backend with SQLite database runs
- React + TypeScript + Vite frontend builds
- Backend and frontend can communicate
- Docker compose with Keycloak runs
- Basic tests pass

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/api/v1/audits.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`, `backend/requirements.txt`, `backend/tests/test_health.py`, `backend/tests/conftest.py`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/AppContext.tsx`, `frontend/src/api/client.ts`, `frontend/src/types/index.ts`, `frontend/src/pages/AuditList.tsx`, `frontend/src/pages/AuditDetail.tsx`, `frontend/src/index.css`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/src/__tests__/setup.ts`, `frontend/src/__tests__/App.test.tsx`, `docker-compose.yaml`, `Dockerfile.backend`, `Dockerfile.frontend`, `frontend/nginx.conf`

Tests: `backend/tests/test_health.py`, `backend/tests/conftest.py`, `frontend/src/__tests__/App.test.tsx`, `frontend/src/__tests__/setup.ts`

### audit-domain-engine — Security audit domain engine with findings, coverage ledger, and validation

Status: planned

Acceptance:
- Finding model with CWE, CVSS, references
- Coverage ledger with attempt tracking
- Validator CLI for findings and coverage
- Multi-phase audit workflow (recon, hunting, validation, reporting)

### oidc-auth — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Login/logout flow works
- Protected API endpoints
- Role-based access control

### llm-adapters — LLM provider adapters (OpenAI-compatible, Anthropic, Gemini, Ollama)

Status: planned

Acceptance:
- Unified LLM interface
- Configurable provider/model/endpoint
- Bounded timeouts, redacted errors

### ui-workflows — Three complete UI workflows: create audit, view findings, export report

Status: planned

Acceptance:
- Create/import audit target
- Search/filter findings
- Export machine-readable report

