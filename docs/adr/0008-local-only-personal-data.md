# ADR 0008 — Local-only Personal Data

> **Status:** Accepted  
> **Date:** 2026-07-26

## Decision

Numra has no user accounts and no server-side profile database. Names,
birthdates, reports, follow-up conversations and notes may be stored only in
the browser after explicit opt-in. The calculation API processes requests
transiently and must not log request bodies.

Redis is permitted only for expiring anonymous rate-limit counters. It must
not contain profile or conversation data.

## Consequences

- Browser storage includes export and complete deletion.
- Device loss means profile loss unless the user exported it.
- Server backups contain deployment configuration, never user profiles.
- Logs and telemetry use correlation IDs and aggregate timings only.
