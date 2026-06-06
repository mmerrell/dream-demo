const { defineConfig } = require('@playwright/test');

/**
 * Minimal Playwright config for saucectl.
 * DOES NOT define projects — saucectl passes --browser via params.browserName.
 * For local runs use: npx playwright test --config playwright.local.config.js
 */
module.exports = defineConfig({
  testDir: './tests-playwright',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
