import { z } from "zod";

const predictionSchema = z.object({
  label: z.enum(["ham", "spam"]),
  spam_probability: z.number().min(0).max(1),
});

const healthSchema = z.object({ status: z.literal("ok") });

export type Prediction = z.infer<typeof predictionSchema> & {
  requestId: string | null;
};

function apiUrl(path: string): URL {
  return new URL(path, window.location.origin);
}

export async function getHealth(): Promise<"ok"> {
  const response = await fetch(apiUrl("/api/health"), {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error("The classifier is not ready.");
  }

  return healthSchema.parse(await response.json()).status;
}

export async function createPrediction(text: string): Promise<Prediction> {
  const response = await fetch(apiUrl("/api/predict"), {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    let message = "The message could not be analyzed.";
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Preserve the friendly fallback when the response is not JSON.
    }
    throw new Error(message);
  }

  const result = predictionSchema.parse(await response.json());
  return {
    ...result,
    requestId: response.headers.get("x-request-id"),
  };
}
