# Frontend Tests

This directory contains Playwright end-to-end tests for the Loan Application frontend.

## Test Coverage

The test suite covers:

- **Form Display**: Verifies all sections and buttons are visible
- **Form Validation**: Tests required field validation, SSN format, email format
- **Random Data Generation**: Tests the "Generate Random Data" button functionality
- **Form Reset**: Tests the "Reset Form" button
- **Conditional Fields**: Tests fields that show/hide based on selections (employment status, loan purpose, bankruptcy, foreclosure)
- **Form Submission (Mocked)**: Tests successful submission with mocked API responses
- **Form Submission (Real API)**: Tests actual loan application submissions to the backend
- **API Response Handling**: Tests approved, disapproved, and additional info needed responses
- **Error Handling**: Tests API error scenarios
- **Button States**: Tests button enabling/disabling during submission

## Test Categories

### Unit/Integration Tests (Mocked API)
Most tests use mocked API responses and can run without the backend server. These tests verify:
- Form validation and UI interactions
- Random data generation
- Form reset functionality
- Conditional field display
- Mock API response handling

### End-to-End Tests (Real API)
Two tests submit actual loan applications to the backend API:
- **"should submit loan application to real API and verify outcome"** - Tests a complete application with good credit profile
- **"should submit application with poor credit and get appropriate decision"** - Tests application with poor credit indicators

**Important:** These tests require the backend API to be running on `http://localhost:8000` and will fail with a clear error message if it's not available.

## Running Tests

### Prerequisites

```bash
# Install dependencies (includes Playwright)
make frontend-install

# Install Playwright browsers (first time only)
cd frontend
npx playwright install
```

### Start the Dev Server and Backend API

**For Mocked Tests (no backend required)**:
```bash
# Terminal 1: Start the dev server
cd frontend
make dev
```

**For Real API Tests (backend required)**:
```bash
# Terminal 1: Start the backend API
cd agents/loan_approval
make run-local

# Terminal 2: Start the frontend dev server
cd frontend
make dev
```

### Run Tests

```bash
# Terminal 3 (or 2 if only mocked tests): Run all tests
make frontend-test

# Or from frontend directory
cd frontend
make test

# Run tests in UI mode (interactive)
make frontend-test-ui

# Or from frontend directory
make test-ui

# Run tests in debug mode
cd frontend
make test-debug

# Run specific test file
cd frontend
SKIP_WEBSERVER=1 npx playwright test tests/loan-application.spec.js

# Run tests in headed mode (see browser)
cd frontend
SKIP_WEBSERVER=1 npx playwright test --headed

# Run tests in specific browser
cd frontend
SKIP_WEBSERVER=1 npx playwright test --project=chromium
SKIP_WEBSERVER=1 npx playwright test --project=firefox
SKIP_WEBSERVER=1 npx playwright test --project=webkit

# Run only mocked tests (no backend required)
cd frontend
SKIP_WEBSERVER=1 npx playwright test --grep-invert "real API|poor credit"

# Run only real API tests (backend required)
cd frontend
SKIP_WEBSERVER=1 npx playwright test --grep "real API|poor credit"
```

### View Test Reports

```bash
cd frontend
npx playwright show-report
```

## Test Configuration

Tests are configured in `playwright.config.js`:

- **Browsers**: Tests run on Chromium, Firefox, and WebKit
- **Base URL**: http://localhost:3000
- **Auto-start dev server**: The dev server starts automatically when running tests
- **Screenshots**: Taken only on failure
- **Traces**: Captured on first retry
- **Retries**: 2 retries in CI, 0 locally

## Writing New Tests

Add new test files in the `tests/` directory with the `.spec.js` extension.

Example:

```javascript
import { test, expect } from '@playwright/test';

test('my new test', async ({ page }) => {
  await page.goto('/');
  // Your test code here
});
```

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```bash
# CI mode (with retries)
CI=true pnpm run test
```

## Debugging Tests

1. **UI Mode** (recommended): `pnpm run test:ui`
2. **Debug Mode**: `pnpm run test:debug`
3. **Headed Mode**: `npx playwright test --headed`
4. **Step through**: Use `await page.pause()` in your test code

## Mock API Responses

The tests use Playwright's route mocking to simulate API responses:

```javascript
await page.route('**/api/v1/loan/evaluate', async route => {
  await route.fulfill({
    status: 200,
    body: JSON.stringify({ /* mock response */ })
  });
});
```

This allows testing without a running backend API.
