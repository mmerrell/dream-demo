# Playwright Tests for Flower Shop

These tests run against the Flower Shop web application and are designed to be executed both locally and via `saucectl` on Sauce Labs.

## Local Run

```bash
# Ensure the app is running (docker-compose up)
npx playwright test
```

## Sauce Labs Run

```bash
# Uses .sauce/config.yml
saucectl run
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Flower Shop frontend URL | `http://localhost:3000` |
| `SAUCE_USERNAME` | Sauce Labs username | — |
| `SAUCE_ACCESS_KEY` | Sauce Labs access key | — |
