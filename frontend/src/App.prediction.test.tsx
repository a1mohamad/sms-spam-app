import { delay, http, HttpResponse } from "msw";
import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderApp } from "./test/renderApp";
import { server } from "./test/server";

describe("prediction workflow", () => {
  it("renders a spam prediction and stores only response metadata in session history", async () => {
    server.use(
      http.post("*/api/predict", () =>
        HttpResponse.json(
          { label: "spam", spam_probability: 0.9123 },
          { headers: { "x-request-id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" } },
        ),
      ),
    );

    const { user } = renderApp();
    await user.type(
      screen.getByRole("textbox", { name: "SMS message" }),
      "Claim your free prize now",
    );
    await user.click(screen.getByRole("button", { name: /Analyze message/i }));

    const result = await screen.findByRole("region", { name: "Prediction result" });
    expect(within(result).getByRole("heading", { name: "Spam detected" })).toBeVisible();
    expect(within(result).getByText("91.2%")).toBeVisible();
    expect(within(result).getByText("Encrypted record saved")).toBeVisible();
    expect(screen.getByText("91.2%", { selector: ".session-list strong" })).toBeVisible();
  });

  it("renders a ham prediction", async () => {
    const { user } = renderApp();
    await user.type(
      screen.getByRole("textbox", { name: "SMS message" }),
      "Are we still meeting at six?",
    );
    await user.click(screen.getByRole("button", { name: /Analyze message/i }));

    const result = await screen.findByRole("region", { name: "Prediction result" });
    expect(within(result).getByRole("heading", { name: "Looks like ham" })).toBeVisible();
    expect(within(result).getByText("8.0%")).toBeVisible();
  });

  it("shows the pending state while inference is running", async () => {
    server.use(
      http.post("*/api/predict", async () => {
        await delay(120);
        return HttpResponse.json({ label: "ham", spam_probability: 0.12 });
      }),
    );

    const { user } = renderApp();
    await user.type(screen.getByRole("textbox", { name: "SMS message" }), "Hello there");
    await user.click(screen.getByRole("button", { name: /Analyze message/i }));

    expect(screen.getByRole("button", { name: /Analyzing signal/i })).toBeDisabled();
    const result = screen.getByRole("region", { name: "Prediction result" });
    expect(await within(result).findByRole("heading", { name: "Looks like ham" })).toBeVisible();
  });

  it("shows an API error without losing the message", async () => {
    server.use(
      http.post("*/api/predict", () =>
        HttpResponse.json({ detail: "Classifier temporarily unavailable." }, { status: 503 }),
      ),
    );

    const { user } = renderApp();
    const input = screen.getByRole("textbox", { name: "SMS message" });
    await user.type(input, "Please analyze this message");
    await user.click(screen.getByRole("button", { name: /Analyze message/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Classifier temporarily unavailable.");
    expect(input).toHaveValue("Please analyze this message");
  });

  it("rejects an invalid API response", async () => {
    server.use(
      http.post("*/api/predict", () =>
        HttpResponse.json({ label: "maybe", spam_probability: 4.2 }),
      ),
    );

    const { user } = renderApp();
    await user.type(screen.getByRole("textbox", { name: "SMS message" }), "Unknown response");
    await user.click(screen.getByRole("button", { name: /Analyze message/i }));

    expect(await screen.findByRole("alert")).not.toBeEmptyDOMElement();
    expect(screen.queryByRole("heading", { name: /Spam detected|Looks like ham/ })).not.toBeInTheDocument();
  });

  it("explains when the free API is unavailable or sleeping", async () => {
    server.use(
      http.get("*/api/health", () => HttpResponse.json({ detail: "Unavailable" }, { status: 503 })),
    );

    renderApp();

    expect((await screen.findAllByText("API sleeping")).length).toBeGreaterThan(0);
    expect(screen.getByText("The free API may be waking up.")).toBeVisible();
  });
});
