export function noteErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Notiz konnte nicht gespeichert werden.";
}
