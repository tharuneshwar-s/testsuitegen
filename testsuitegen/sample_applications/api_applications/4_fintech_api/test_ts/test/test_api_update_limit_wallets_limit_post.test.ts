import { describe, it, expect } from '@jest/globals';

// Uses native fetch (Node.js 18+)

describe("POST /wallets/limit (update_limit_wallets_limit_post)", () => {
  const BASE_URL = "http://localhost:8004";
  const ENDPOINT = "/wallets/limit";
  const METHOD = "POST";

  // Operation: update_limit_wallets_limit_post
  // Error Codes Expected: 422

  const testCases = [
    {
      intent: "HAPPY_PATH",
      payload: { daily_limit: 5000, risk_score: 0.0 },
      pathParams: {},
      expectedStatus: 200,
    },
    {
      intent: "REQUIRED_FIELD_MISSING",
      payload: { risk_score: 0.0 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "REQUIRED_FIELD_MISSING",
      payload: { daily_limit: 5000 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "TYPE_VIOLATION",
      payload: { daily_limit: '__INVALID_TYPE__', risk_score: 0.0 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "BOUNDARY_MIN_MINUS_ONE",
      payload: { daily_limit: -1.0, risk_score: 0.0 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "BOUNDARY_MAX_PLUS_ONE",
      payload: { daily_limit: 5001.0, risk_score: 0.0 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "TYPE_VIOLATION",
      payload: { daily_limit: 5000, risk_score: '__INVALID_TYPE__' },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "BOUNDARY_MIN_MINUS_ONE",
      payload: { daily_limit: 5000, risk_score: -0.01 },
      pathParams: {},
      expectedStatus: 422,
    },
    {
      intent: "BOUNDARY_MAX_PLUS_ONE",
      payload: { daily_limit: 5000, risk_score: 1.01 },
      pathParams: {},
      expectedStatus: 422,
    },
  ];

  beforeAll(async () => {
    // Implement dynamic data setup here if needed
  });

  it.each(testCases)("intent: %s", async (testCase) => {
    const { intent, payload, pathParams, expectedStatus } = testCase;

    let url = `${BASE_URL}${ENDPOINT}`;

    if (pathParams) {
      for (const [name, value] of Object.entries(pathParams)) {
        const paramValue =
          value === "__INVALID_TYPE__" ? "invalid_string_value" : value ?? 1;
        url = url.replace(`:${name}`, String(paramValue)).replace(
          `{${name}}`,
          String(paramValue),
        );
      }
    }

    const init: any = {
      method: METHOD,
      headers: { "Content-Type": "application/json" },
    };

    if (payload && (METHOD === "POST" || METHOD === "PUT" || METHOD === "PATCH")) {
      init.body = JSON.stringify(payload);
    }

    const response = await fetch(url, init);

    expect(response.status).toBe(
      expectedStatus,
    );

    if (expectedStatus >= 400) {
      try {
        const body = await response.json();
        expect(body).toBeDefined();
      } catch {
        // Some error responses might not have JSON body
      }
    }
  });
});