# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-23

### Added
- Initial FastAPI/React scaffold with SQLite database
- Health check endpoint at `/health`
- Audit run CRUD API (`/api/v1/audits`)
- Finding CRUD API (`/api/v1/audits/{id}/findings`) with CWE, CVSS, references, preserved_uses
- Coverage ledger API (`/api/v1/audits/{id}/coverage`) with units, attempts, promoted artifacts
- Audit logs API (`/api/v1/audits/{id}/logs`)
- React + TypeScript + Vite frontend with:
  - Audit list page with create/delete
  - Audit detail page with findings, coverage, logs tabs
  - Finding management (create, update status/severity)
  - Responsive professional UI with loading/error/empty states
- Docker Compose with backend, frontend, and Keycloak
- Backend tests (9 passing) using FastAPI TestClient
- Frontend tests (3 passing) using Vitest + React Testing Library
- CI pipeline with backend/frontend tests, type checking, Docker builds
- README with architecture diagram, API reference, AI/ML evaluation section
- Portfolio.json with project metadata
- MIT License