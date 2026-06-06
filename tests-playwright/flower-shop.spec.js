const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

/**
 * Flower Shop E2E Tests — Playwright
 *
 * These tests cover the core web flows of the Flower Shop app:
 * - Page load & product display
 * - User registration & login
 * - Add to cart & place order
 *
 * Run locally:
 *   npx playwright test
 *
 * Run via saucectl on Sauce Labs:
 *   saucectl run
 */

test.describe('Flower Shop - Auth Flow', () => {
  test('page loads with Flower Shop branding', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.getByRole('heading', { name: /Flower Shop/i })).toBeVisible();
    await expect(page.getByText('Our Products')).toBeVisible();
  });

  test('user can register and then log in', async ({ page }) => {
    await page.goto(BASE_URL);

    const uniqueEmail = `demo-${Date.now()}@example.com`;

    // Register
    const registerForm = page.getByRole('form', { name: /Registration form/i });
    await registerForm.getByRole('textbox', { name: /Email address for registration/i }).fill(uniqueEmail);
    await registerForm.getByRole('textbox', { name: /Password for registration/i }).fill('DemoPass123!');
    await registerForm.getByRole('button', { name: /Submit registration/i }).click();

    // Accept alert
    page.on('dialog', async dialog => await dialog.accept());

    // Login
    const loginForm = page.getByRole('form', { name: /Login form/i });
    await loginForm.getByRole('textbox', { name: /Email address for login/i }).fill(uniqueEmail);
    await loginForm.getByRole('textbox', { name: /Password for login/i }).fill('DemoPass123!');
    await loginForm.getByRole('button', { name: /Submit login/i }).click();

    await expect(page.getByText(/Welcome,/i)).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Flower Shop - Shopping Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);

    // Re-use a known test account (assumes it exists in seeded DB)
    const loginForm = page.getByRole('form', { name: /Login form/i });
    await loginForm.getByRole('textbox', { name: /Email address for login/i }).fill('test@example.com');
    await loginForm.getByRole('textbox', { name: /Password for login/i }).fill('testpassword123');
    await loginForm.getByRole('button', { name: /Submit login/i }).click();

    await expect(page.getByText(/Welcome,/i)).toBeVisible({ timeout: 10000 });
  });

  test('add product to cart and place order', async ({ page }) => {
    // Add first product to cart
    const addButton = page.getByRole('button', { name: /^Add .* to cart/i }).first();
    await addButton.click();

    // Verify cart shows the item
    await expect(page.getByText(/Your cart is empty/)).not.toBeVisible();
    await expect(page.locator('.cart-total')).toContainText('$');

    // Place order
    await page.getByRole('button', { name: /Place order/i }).click();

    // Accept alert
    page.on('dialog', async dialog => await dialog.accept());

    // Verify orders section appears
    await expect(page.getByRole('heading', { name: /Your Orders/i })).toBeVisible();
  });

  test('logout returns to auth screen', async ({ page }) => {
    await page.getByRole('button', { name: /Logout/i }).click();
    await expect(page.getByRole('form', { name: /Login form/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Submit login/i })).toBeVisible();
  });
});
