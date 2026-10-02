import { test, expect } from "@playwright/test";

test.describe("Authentication Page E2E", () => {
  test("login page renders form and toggles between Sign In and Sign Up", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByText("RetainIQ Platform")).toBeVisible();

    // Toggle to Sign Up mode
    await page.getByRole("button", { name: "Sign Up" }).first().click();
    await expect(page.getByPlaceholder("Rahul Sharma")).toBeVisible();

    // Toggle back to Sign In mode
    await page.getByRole("button", { name: "Sign In" }).first().click();
    await expect(page.getByPlaceholder("admin@retainiq.com")).toBeVisible();
  });
});
