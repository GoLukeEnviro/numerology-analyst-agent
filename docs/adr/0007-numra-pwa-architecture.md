# ADR 0007 — Numra PWA Architecture

> **Status:** Accepted  
> **Date:** 2026-07-26

## Decision

Numra is implemented in this repository as a React/Vite/TypeScript PWA under
`apps/web`. The existing Python `src/` packages remain the source of truth for
domain logic and schemas. Browser clients consume a generated OpenAPI contract
and never reimplement numerological algorithms.

The service worker precaches only application assets. API `POST` responses and
personal profile data are never stored in Cache Storage. Durable profile data
is opt-in and remains in IndexedDB on the user's device.

## Consequences

- Desktop, Android and iOS share one responsive codebase.
- New calculations require an online FastAPI service.
- Saved profiles remain readable offline.
- Frontend and backend quality gates run together in CI.
