import type {
  ProblemDetails,
  ProfileCalculationRequest,
  ProfileCalculationResult,
} from "./types";

export class ApiProblem extends Error {
  readonly code: string;
  readonly correlationId: string;

  constructor(problem: Pick<ProblemDetails, "title" | "detail" | "code" | "correlation_id">) {
    super(problem.detail || problem.title);
    this.name = "ApiProblem";
    this.code = problem.code;
    this.correlationId = problem.correlation_id;
  }
}

export async function calculateProfile(
  request: ProfileCalculationRequest,
  fetcher: typeof fetch = fetch,
): Promise<ProfileCalculationResult> {
  const response = await fetcher("/api/v1/profiles/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Correlation-ID": crypto.randomUUID(),
    },
    body: JSON.stringify(request),
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    const problem = payload as ProblemDetails;
    throw new ApiProblem(problem);
  }
  return payload as ProfileCalculationResult;
}
