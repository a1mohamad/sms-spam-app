import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderApp } from "./test/renderApp";

describe("workspace navigation and controls", () => {
  it("orders the primary navigation around the App workspace", () => {
    renderApp();

    const navigation = screen.getByRole("navigation", { name: "Primary navigation" });
    const links = within(navigation).getAllByRole("link");

    expect(links.map((link) => link.getAttribute("aria-label"))).toEqual([
      "App",
      "Datasets",
      "Training",
    ]);
    expect(screen.getByRole("heading", { name: "Read the signal in any message" })).toBeVisible();
  });

  it("switches between App, Datasets, and Training", async () => {
    const { user } = renderApp();
    const navigation = screen.getByRole("navigation", { name: "Primary navigation" });

    await user.click(within(navigation).getByRole("link", { name: "Datasets" }));
    expect(screen.getByRole("heading", { name: "Know the signal before the model" })).toBeVisible();
    expect(window.location.pathname).toBe("/datasets");

    await user.click(within(navigation).getByRole("link", { name: "Training" }));
    expect(screen.getByRole("heading", { name: "A small model with a sharp signal" })).toBeVisible();
    expect(window.location.pathname).toBe("/training");
  });

  it("focuses search with K and opens a matching result", async () => {
    const { user } = renderApp();
    const search = screen.getByRole("searchbox", {
      name: "Search datasets, metrics, and model details",
    });

    await user.keyboard("k");
    expect(search).toHaveFocus();

    await user.type(search, "Vocabulary");
    const result = screen.getByRole("button", { name: "Vocabulary, Datasets" });
    expect(result).toBeVisible();

    await user.click(result);
    expect(window.location.pathname).toBe("/datasets");
    expect(screen.getByRole("heading", { name: "Know the signal before the model" })).toBeVisible();
  });

  it("cycles through dark, light, and high-contrast themes", async () => {
    const { container, user } = renderApp();
    const app = container.querySelector(".app");

    expect(app).toHaveAttribute("data-theme", "dark");
    await user.click(screen.getByRole("button", { name: /Current theme: dark/i }));
    expect(app).toHaveAttribute("data-theme", "light");
    await user.click(screen.getByRole("button", { name: /Current theme: light/i }));
    expect(app).toHaveAttribute("data-theme", "contrast");
  });

  it("hides and restores the desktop sidebar", async () => {
    const { container, user } = renderApp();

    await user.click(screen.getByRole("button", { name: "Hide sidebar" }));
    expect(container.querySelector(".app")).toHaveClass("rail-collapsed");
    expect(screen.getByRole("button", { name: "Show sidebar" })).toBeVisible();
  });

  it("uses the correct source-of-truth repository for each section", async () => {
    const { user } = renderApp("/datasets");

    expect(screen.getByRole("link", { name: "Source of truth: Application repository" }))
      .toHaveAttribute("href", "https://github.com/a1mohamad/sms-spam-app");

    const navigation = screen.getByRole("navigation", { name: "Primary navigation" });
    await user.click(within(navigation).getByRole("link", { name: "Training" }));

    expect(screen.getByRole("link", { name: "Source of truth: Training notebooks" }))
      .toHaveAttribute(
        "href",
        "https://github.com/a1mohamad/machine-learning-portfolio/tree/main/SMS%20Spam",
      );
  });

  it("exposes the six icon-only contact links with accessible names", () => {
    renderApp();
    const footer = screen.getByRole("navigation", { name: "Contact links" });

    for (const name of ["Gmail", "iCloud", "Phone", "GitHub", "LinkedIn", "Kaggle"]) {
      const link = within(footer).getByRole("link", { name });
      expect(link).toBeVisible();
      expect(link.querySelector("svg")).toBeTruthy();
    }
  });
});
