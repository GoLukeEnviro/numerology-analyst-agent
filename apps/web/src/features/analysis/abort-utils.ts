import { ApiProblem } from "../../api/client";

const QUOTA_EXHAUSTED_CODES = new Set([
  "rate_limit_exceeded",
  "quota_exceeded",
  "daily_quota_exceeded",
]);

export function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}

export function isQuotaError(error: unknown): boolean {
  return error instanceof ApiProblem && QUOTA_EXHAUSTED_CODES.has(error.code);
}

export function quotaExhaustedMessage(error: unknown): string | null {
  if (isQuotaError(error)) {
    return "Das tägliche Kontingent ist ausgeschöpft. Bitte versuche es morgen wieder.";
  }
  return null;
}
