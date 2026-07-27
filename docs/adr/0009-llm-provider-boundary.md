# ADR 0009 — LLM Provider Boundary

> **Status:** Accepted  
> **Date:** 2026-07-26

## Decision

The deterministic engine calculates all numbers. An optional provider adapter
may explain validated results but cannot calculate, mutate or replace them.
DeepSeek V4 Pro is the first adapter and remains disabled by configuration
until the privacy and international-transfer launch gate is satisfied.

The provider receives no clear name or complete birthdate. It receives only
validated calculation facts, versioned knowledge excerpts and the user's
explicit follow-up text. Outputs are accepted only after schema, claim and
safety validation.

## Consequences

- Provider model, prompt, knowledge pack, parameters and fingerprint are
  returned as provenance.
- The platform remains usable without an LLM.
- Provider requests and responses are never written to application logs.
- Replacing the provider does not change domain or API calculation contracts.
