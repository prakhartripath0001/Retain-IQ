import { test, expect } from "@playwright/test";

test.describe("Platform Navigation & Page Views E2E", () => {
  test("dashboard page loads and displays executive headers and metrics", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText("RetainIQ Executive Dashboard")).toBeVisible();
    await expect(page.getByRole("main").getByText("Revenue", { exact: true })).toBeVisible();
    await expect(page.getByRole("main").getByText("Customers", { exact: true })).toBeVisible();
    await expect(page.getByRole("main").getByText("Orders", { exact: true })).toBeVisible();
    await expect(page.getByRole("main").getByText("Churn Rate", { exact: true })).toBeVisible();
  });

  test("customers directory loads", async ({ page }) => {
    await page.goto("/customers");
    await expect(page.getByRole("heading", { name: "Customers" })).toBeVisible();
    await expect(page.getByPlaceholder("Search by name or email...")).toBeVisible();
  });

  test("products page loads", async ({ page }) => {
    await page.goto("/products");
    await expect(page.getByText("Products Catalog")).toBeVisible();
    await expect(page.getByRole("button", { name: "Add Product" })).toBeVisible();
  });

  test("orders page loads", async ({ page }) => {
    await page.goto("/orders");
    await expect(page.getByText("Orders & Transactions")).toBeVisible();
  });

  test("segments page loads", async ({ page }) => {
    await page.goto("/segments");
    await expect(page.getByRole("heading", { name: "Customer Segmentation" })).toBeVisible();
  });

  test("churn risk page loads", async ({ page }) => {
    await page.goto("/churn");
    await expect(page.getByText("Churn Risk & Prediction")).toBeVisible();
    await expect(page.getByRole("button", { name: "Predict" })).toBeVisible();
  });

  test("analytics page loads", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page.getByText("Business & Revenue Analytics")).toBeVisible();
  });
});
