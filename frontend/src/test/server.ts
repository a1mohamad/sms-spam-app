import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const server = setupServer(
  http.get("*/api/health", () => HttpResponse.json({ status: "ok" })),
  http.post("*/api/predict", () =>
    HttpResponse.json(
      { label: "ham", spam_probability: 0.08 },
      { headers: { "x-request-id": "11111111-2222-3333-4444-555555555555" } },
    ),
  ),
);
