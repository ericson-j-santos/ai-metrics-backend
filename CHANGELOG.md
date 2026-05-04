# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-05-01

### Added

- FastAPI backend with SQLite database (SQLAlchemy ORM)
- AI metrics endpoints: `/api/metrics` (list, create, detail)
- Incidents integration: endpoints `/api/incidents` and `/api/incidents/{id}`
- Correlation between AI metrics and related incidents
- `GET /health` health check endpoint
- JWT authentication support structure
- Pytest test suite (`tests/test_api.py`) covering metrics and incidents endpoints
- CI pipeline via GitHub Actions (`.github/workflows/ci.yml`): Python 3.12, pytest, SQLite in-memory
- `.env.example` with all required environment variables documented
- `BUNDLE_SUMMARY.md` describing project architecture

[Unreleased]: https://github.com/ericson-j-santos/ai-metrics-backend/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ericson-j-santos/ai-metrics-backend/releases/tag/v1.0.0
