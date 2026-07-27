import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function mockApi(page: Page) {
  await page.route("**/api/health", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" }),
    }),
  );
  await page.route("**/api/predict", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "x-request-id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" },
      body: JSON.stringify({ label: "spam", spam_probability: 0.96 }),
    }),
  );
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("adapts primary navigation to the viewport", async ({ page, isMobile }) => {
  await page.goto("/app");

  const desktopRail = page.locator(".icon-rail");
  const mobileNavigation = page.getByRole("navigation", { name: "Mobile primary navigation" });

  if (isMobile) {
    await expect(desktopRail).toBeHidden();
    await expect(mobileNavigation).toBeVisible();
    await mobileNavigation.getByRole("link", { name: "Datasets" }).click();
  } else {
    await expect(desktopRail).toBeVisible();
    await expect(mobileNavigation).toBeHidden();
    await page.getByRole("navigation", { name: "Primary navigation" })
      .getByRole("link", { name: "Datasets" })
      .click();
  }

  await expect(page.getByRole("heading", { name: "Know the signal before the model" })).toBeVisible();
});

test("completes a prediction from message to result", async ({ page }) => {
  await page.goto("/app");
  await page.getByRole("textbox", { name: "SMS message" }).fill("Win a free prize now");
  await page.getByRole("button", { name: /Analyze message/i }).click();

  const result = page.getByRole("region", { name: "Prediction result" });
  await expect(result.getByRole("heading", { name: "Spam detected" })).toBeVisible();
  await expect(result.getByText("96.0%")).toBeVisible();
  await expect(result.getByText("Encrypted record saved")).toBeVisible();
});

test("opens selected details as a mobile sheet", async ({ page, isMobile }) => {
  test.skip(!isMobile, "Mobile-only interaction");
  await page.goto("/datasets");

  await page.locator(".metric-card").first().click();
  const detailPanel = page.getByRole("complementary", { name: "Selected item details" });
  await expect(detailPanel).toHaveClass(/open/);
  await expect(detailPanel.getByRole("heading", { name: "Messages" })).toBeVisible();
});

test("has no automatically detectable WCAG A or AA violations in any theme", async ({ page }) => {
  await page.goto("/app");
  await expect(page.getByRole("heading", { name: "Read the signal in any message" })).toBeVisible();

  for (const theme of ["dark", "light", "contrast"]) {
    await expect(page.locator(".app")).toHaveAttribute("data-theme", theme);

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    expect(results.violations, `${theme} theme accessibility violations`).toEqual([]);

    if (theme !== "contrast") {
      await page.getByRole("button", { name: `Current theme: ${theme}. Change theme.` }).click();
    }
  }
});
