import { test, expect } from '@playwright/test';

test.describe('Loan Application Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the loan application form', async ({ page }) => {
    // Check page title and header
    await expect(page.locator('h1')).toContainText('Loan Application Portal');
    await expect(page.locator('p')).toContainText('AI-Powered Instant Loan Evaluation');
    
    // Check all sections are present
    await expect(page.locator('h2').filter({ hasText: 'Personal Information' })).toBeVisible();
    await expect(page.locator('h2').filter({ hasText: 'Employment Information' })).toBeVisible();
    await expect(page.locator('h2').filter({ hasText: 'Financial Information' })).toBeVisible();
    await expect(page.locator('h2').filter({ hasText: 'Credit History' })).toBeVisible();
    await expect(page.locator('h2').filter({ hasText: 'Loan Details' })).toBeVisible();
  });

  test('should have all action buttons', async ({ page }) => {
    await expect(page.locator('button', { hasText: 'Submit Application' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Generate Random Data' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Generate Approved Request' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Reset Form' })).toBeVisible();
  });

  test('should validate required fields on submit', async ({ page }) => {
    // Click submit without filling the form
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Check for validation errors
    await expect(page.locator('.error-message').first()).toBeVisible();
  });

  test('should generate random data when clicking Generate Random Data button', async ({ page }) => {
    // Click the Generate Random Data button
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    
    // Wait a bit for the form to be populated
    await page.waitForTimeout(500);
    
    // Verify that key fields are now populated
    const firstName = await page.locator('input[name="first_name"]').inputValue();
    const lastName = await page.locator('input[name="last_name"]').inputValue();
    const email = await page.locator('input[name="email"]').inputValue();
    const ssn = await page.locator('input[name="ssn"]').inputValue();
    const creditScore = await page.locator('input[name="credit_score"]').inputValue();
    const loanAmount = await page.locator('input[name="loan_amount"]').inputValue();
    
    expect(firstName).not.toBe('');
    expect(lastName).not.toBe('');
    expect(email).toContain('@example.com');
    expect(ssn).toMatch(/^\d{3}-\d{2}-\d{4}$/);
    expect(parseInt(creditScore)).toBeGreaterThan(0);
    expect(parseInt(loanAmount)).toBeGreaterThan(0);
  });

  test('should generate approved request data when clicking Generate Approved Request button', async ({ page }) => {
    // Click the Generate Approved Request button
    await page.locator('button', { hasText: 'Generate Approved Request' }).click();
    
    // Wait a bit for the form to be populated
    await page.waitForTimeout(500);
    
    // Verify that all key fields are populated with approval-worthy data
    const firstName = await page.locator('input[name="first_name"]').inputValue();
    const lastName = await page.locator('input[name="last_name"]').inputValue();
    const email = await page.locator('input[name="email"]').inputValue();
    const ssn = await page.locator('input[name="ssn"]').inputValue();
    const creditScore = await page.locator('input[name="credit_score"]').inputValue();
    const loanAmount = await page.locator('input[name="loan_amount"]').inputValue();
    const monthlyIncome = await page.locator('input[name="monthly_income"]').inputValue();
    const savingsBalance = await page.locator('input[name="savings_balance"]').inputValue();
    const employmentStatus = await page.locator('select[name="employment_status"]').inputValue();
    
    // Verify fields are populated
    expect(firstName).not.toBe('');
    expect(lastName).not.toBe('');
    expect(email).toContain('@example.com');
    expect(ssn).toMatch(/^\d{3}-\d{2}-\d{4}$/);
    
    // Verify approval-worthy values
    expect(parseInt(creditScore)).toBeGreaterThan(700); // Good credit score
    expect(parseInt(loanAmount)).toBeGreaterThan(0);
    expect(parseInt(monthlyIncome)).toBeGreaterThan(5000); // Good income
    expect(parseInt(savingsBalance)).toBeGreaterThan(10000); // Good savings
    expect(employmentStatus).toBe('employed'); // Should be employed
  });

  test('should submit generated approved request with supporting documentation (mock API)', async ({ page }) => {
    let capturedPayload;

    await page.route('**/api/v1/loan/evaluate', async route => {
      capturedPayload = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'TEST-APPROVED',
          decision: {
            decision: 'approved',
            risk_score: 12,
            disapproval_reason: null,
            additional_info_description: null,
            recommended_amount: '400000',
            recommended_term_months: 360,
            interest_rate: '4.5',
            monthly_payment: '2026.74'
          },
          processing_time_ms: 850
        })
      });
    });

    await page.locator('button', { hasText: 'Generate Approved Request' }).click();
    await page.waitForTimeout(200);
    await page.locator('button', { hasText: 'Submit Application' }).click();

    await page.waitForSelector('.result', { timeout: 5000 });

    expect(capturedPayload).toBeDefined();
    expect(capturedPayload.financial.monthly_debt_breakdown).toBeTruthy();
    expect(capturedPayload.financial.monthly_debt_breakdown.auto_loan).toBe(500);
    expect(capturedPayload.property).toBeTruthy();
    expect(capturedPayload.property.address).toBe('789 Pine Street');
    expect(capturedPayload.documentation).toBeTruthy();
    expect(capturedPayload.documentation.application_signed).toBe(true);
    expect(capturedPayload.documentation.pay_stubs_months).toBe(2);
    expect(capturedPayload.documentation.tax_returns_verified).toBe(true);
  });

  test('should generate approved request and submit successfully to real API', async ({ page }) => {
    // Check if API is running
    const apiHealthCheck = await page.request.get('http://localhost:8000/health').catch(() => null);
    if (!apiHealthCheck || !apiHealthCheck.ok()) {
      throw new Error('Backend API is not running. Please start the API server on port 8000 before running this test.');
    }

    // Click the Generate Approved Request button
    await page.locator('button', { hasText: 'Generate Approved Request' }).click();
    
    // Wait for form to be populated
    await page.waitForTimeout(500);
    
    // Submit the form
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Wait for result to appear (real API might take longer)
    await page.waitForSelector('.result', { timeout: 30000 });
    
    // Verify result is displayed
    await expect(page.locator('.result')).toBeVisible();
    
    const resultElement = page.locator('.result');
    const resultText = await resultElement.textContent();
    const heading = await resultElement.locator('h3').textContent();
    
    // Verify we got a valid response
    expect(resultText).toContain('Request ID');
    expect(resultText).toContain('Decision');
    expect(resultText).toContain('Processing Time');
    
    // The request uses approval-optimized data, but actual decision is up to the AI agent
    // We verify we get one of the valid decision types
    const hasValidDecision = 
      heading.includes('Application Approved') || 
      heading.includes('Application Disapproved') || 
      heading.includes('Additional Information Needed');
    expect(hasValidDecision).toBeTruthy();
    
    // Note: This test generates high-quality loan application data designed to maximize
    // approval chances, but the final decision is made by the AI agent based on its
    // evaluation logic. The test verifies the form works correctly, not the approval rate.
  });

  test('should validate SSN format', async ({ page }) => {
    // Fill in an invalid SSN
    await page.locator('input[name="ssn"]').fill('123456789');
    await page.locator('input[name="first_name"]').fill('John');
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Wait a bit for validation
    await page.waitForTimeout(500);
    
    // Check for SSN validation error
    const errorMessages = await page.locator('.error-message').allTextContents();
    const hasSsnError = errorMessages.some(msg => 
      msg.includes('SSN') || msg.includes('format')
    );
    expect(hasSsnError).toBeTruthy();
  });

  test('should validate email format', async ({ page }) => {
    // Fill in an invalid email
    await page.locator('input[name="email"]').fill('invalid-email');
    await page.locator('input[name="first_name"]').fill('John');
    
    // Click submit and wait for validation to complete
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Wait for error messages to appear (or alert to show up)
    await page.waitForTimeout(1000);
    
    // Check for email validation error (check if any error message contains email-related text)
    const errorMessages = await page.locator('.error-message').allTextContents();
    const hasEmailError = errorMessages.some(msg => 
      msg.includes('email') || msg.includes('Email') || msg.includes('Invalid email')
    );
    expect(hasEmailError).toBeTruthy();
  });

  test('should reset form when clicking Reset Form button', async ({ page }) => {
    // Generate random data first
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    
    // Verify data is populated
    let firstName = await page.locator('input[name="first_name"]').inputValue();
    expect(firstName).not.toBe('');
    
    // Click reset
    await page.locator('button', { hasText: 'Reset Form' }).click();
    
    // Verify form is empty
    firstName = await page.locator('input[name="first_name"]').inputValue();
    const lastName = await page.locator('input[name="last_name"]').inputValue();
    const email = await page.locator('input[name="email"]').inputValue();
    
    expect(firstName).toBe('');
    expect(lastName).toBe('');
    expect(email).toBe('');
  });

  test('should show employment fields based on employment status', async ({ page }) => {
    // Select employed status
    await page.locator('select[name="employment_status"]').selectOption('employed');
    await expect(page.locator('input[name="employer_name"]')).toBeVisible();
    await expect(page.locator('input[name="job_title"]')).toBeVisible();
    
    // Select unemployed status
    await page.locator('select[name="employment_status"]').selectOption('unemployed');
    await expect(page.locator('input[name="employer_name"]')).toBeVisible();
  });

  test('should show property fields for home loans', async ({ page }) => {
    // Select home purchase
    await page.locator('select[name="loan_purpose"]').selectOption('home_purchase');
    await page.waitForTimeout(200);
    
    // Check property value and down payment fields are visible
    await expect(page.locator('input[name="property_value"]')).toBeVisible();
    await expect(page.locator('input[name="down_payment"]')).toBeVisible();
  });

  test('should show bankruptcy date field when has_bankruptcy is checked', async ({ page }) => {
    // Check bankruptcy checkbox
    await page.locator('input[name="has_bankruptcy"]').check();
    
    // Verify bankruptcy date field appears
    await expect(page.locator('input[name="bankruptcy_date"]')).toBeVisible();
    
    // Uncheck
    await page.locator('input[name="has_bankruptcy"]').uncheck();
    
    // Verify field is hidden
    await expect(page.locator('input[name="bankruptcy_date"]')).not.toBeVisible();
  });

  test('should show foreclosure date field when has_foreclosure is checked', async ({ page }) => {
    // Check foreclosure checkbox
    await page.locator('input[name="has_foreclosure"]').check();
    
    // Verify foreclosure date field appears
    await expect(page.locator('input[name="foreclosure_date"]')).toBeVisible();
  });

  test('should submit form with random data successfully (mock API)', async ({ page }) => {
    // Mock the API response
    await page.route('**/api/v1/loan/evaluate', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'TEST-001',
          decision: {
            decision: 'approved',
            risk_score: 15,
            disapproval_reason: null,
            additional_info_description: null,
            recommended_amount: '50000',
            recommended_term_months: 60,
            interest_rate: '5.5',
            monthly_payment: '1000.00'
          },
          processing_time_ms: 1234
        })
      });
    });
    
    // Generate random data
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    
    // Submit the form
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Wait for result to appear
    await page.waitForSelector('.result', { timeout: 5000 });
    
    // Verify result is displayed
    await expect(page.locator('.result')).toBeVisible();
    await expect(page.locator('.result h3')).toContainText('Application Approved');
    await expect(page.locator('.result')).toContainText('Risk Score');
  });

  test('should handle disapproved loan application', async ({ page }) => {
    // Mock disapproved response
    await page.route('**/api/v1/loan/evaluate', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'TEST-002',
          decision: {
            decision: 'disapproved',
            risk_score: 85,
            disapproval_reason: 'Credit score below threshold',
            additional_info_description: null,
            recommended_amount: null,
            recommended_term_months: null,
            interest_rate: null,
            monthly_payment: null
          },
          processing_time_ms: 1100
        })
      });
    });
    
    // Generate and submit
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Verify disapproved result
    await page.waitForSelector('.result', { timeout: 5000 });
    await expect(page.locator('.result h3')).toContainText('Application Disapproved');
    await expect(page.locator('.result')).toContainText('Credit score below threshold');
  });

  test('should handle additional info needed response', async ({ page }) => {
    // Mock additional info needed response
    await page.route('**/api/v1/loan/evaluate', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'TEST-003',
          decision: {
            decision: 'additional_info_needed',
            risk_score: 45,
            disapproval_reason: null,
            additional_info_description: 'Need to verify employment and income',
            recommended_amount: null,
            recommended_term_months: null,
            interest_rate: null,
            monthly_payment: null
          },
          processing_time_ms: 980
        })
      });
    });
    
    // Generate and submit
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Verify result
    await page.waitForSelector('.result', { timeout: 5000 });
    await expect(page.locator('.result h3')).toContainText('Additional Information Needed');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/loan/evaluate', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error'
        })
      });
    });
    
    // Listen for alerts
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('Error');
      await dialog.accept();
    });
    
    // Generate and submit
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Wait a bit for the error to be handled
    await page.waitForTimeout(1000);
  });

  test('should disable buttons while submitting', async ({ page }) => {
    // Mock a slow API response
    await page.route('**/api/v1/loan/evaluate', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'TEST-004',
          decision: {
            decision: 'approved',
            risk_score: 20,
            disapproval_reason: null,
            additional_info_description: null,
            recommended_amount: '50000',
            recommended_term_months: 60,
            interest_rate: '5.5',
            monthly_payment: '1000.00'
          },
          processing_time_ms: 2000
        })
      });
    });
    
    // Generate and submit
    await page.locator('button', { hasText: 'Generate Random Data' }).click();
    await page.waitForTimeout(500);
    await page.locator('button', { hasText: 'Submit Application' }).click();
    
    // Check that buttons are disabled
    await expect(page.locator('button', { hasText: 'Generate Random Data' })).toBeDisabled();
    await expect(page.locator('button', { hasText: 'Reset Form' })).toBeDisabled();
    
    // Wait for submission to complete
    await page.waitForSelector('.result', { timeout: 5000 });
    
    // Buttons should be enabled again
    await expect(page.locator('button', { hasText: 'Generate Random Data' })).toBeEnabled();
    await expect(page.locator('button', { hasText: 'Reset Form' })).toBeEnabled();
  });

  test('should submit loan application to real API and verify outcome', async ({ page }) => {
    // Check if API is running
    const apiHealthCheck = await page.request.get('http://localhost:8000/health').catch(() => null);
    if (!apiHealthCheck || !apiHealthCheck.ok()) {
      throw new Error('Backend API is not running. Please start the API server on port 8000 before running this test.');
    }

    // Fill in a complete loan application form with data likely to be approved
    await page.locator('input[name="first_name"]').fill('Sarah');
    await page.locator('input[name="last_name"]').fill('Johnson');
    await page.locator('input[name="date_of_birth"]').fill('1985-03-15');
    await page.locator('input[name="ssn"]').fill('123-45-6789');
    await page.locator('input[name="email"]').fill('sarah.johnson@example.com');
    await page.locator('input[name="phone"]').fill('+15551234567');
    await page.locator('input[name="address"]').fill('456 Oak Avenue');
    await page.locator('input[name="city"]').fill('Seattle');
    await page.locator('input[name="state"]').fill('WA');
    await page.locator('input[name="zip_code"]').fill('98101');

    // Employment information
    await page.locator('select[name="employment_status"]').selectOption('employed');
    await page.locator('input[name="employer_name"]').fill('Tech Solutions Inc');
    await page.locator('input[name="job_title"]').fill('Senior Software Engineer');
    await page.locator('input[name="years_employed"]').fill('5.5');
    await page.locator('input[name="monthly_income"]').fill('12000');
    await page.locator('input[name="additional_income"]').fill('1000');
    await page.locator('input[name="industry"]').fill('Technology');
    await page.locator('textarea[name="industry_outlook"]').fill('Stable with strong growth prospects');

    // Financial information
    await page.locator('input[name="monthly_debt_payments"]').fill('2000');
    await page.locator('input[name="checking_balance"]').fill('15000');
    await page.locator('input[name="savings_balance"]').fill('50000');
    await page.locator('input[name="investment_balance"]').fill('75000');
    await page.locator('input[name="retirement_balance"]').fill('120000');
    await page.locator('input[name="asset_reserves_months"]').fill('8.5');

    // Credit history
    await page.locator('input[name="credit_score"]').fill('780');
    await page.locator('input[name="number_of_credit_cards"]').fill('4');
    await page.locator('input[name="total_credit_limit"]').fill('60000');
    await page.locator('input[name="credit_utilization"]').fill('15.5');
    await page.locator('input[name="number_of_late_payments_12m"]').fill('0');
    await page.locator('input[name="number_of_late_payments_24m"]').fill('0');
    await page.locator('input[name="number_of_inquiries_6m"]').fill('1');
    await page.locator('input[name="oldest_credit_line_years"]').fill('12.5');

    // Loan details
    await page.locator('input[name="loan_amount"]').fill('50000');
    await page.locator('select[name="loan_purpose"]').selectOption('personal');
    await page.locator('input[name="term_months"]').fill('60');

    // Submit the form
    await page.locator('button', { hasText: 'Submit Application' }).click();

    // Wait for result to appear (real API might take longer)
    await page.waitForSelector('.result', { timeout: 30000 });

    // Verify result is displayed
    await expect(page.locator('.result')).toBeVisible();
    
    // Check that we have a decision
    const resultElement = page.locator('.result');
    await expect(resultElement.locator('h3')).toBeVisible();
    
    // Verify key elements are present
    const resultText = await resultElement.textContent();
    expect(resultText).toContain('Request ID');
    expect(resultText).toContain('Decision');
    expect(resultText).toContain('Processing Time');
    
    // Check decision status - should be one of the three possible outcomes
    const heading = await resultElement.locator('h3').textContent();
    const hasValidDecision = 
      heading.includes('Application Approved') || 
      heading.includes('Application Disapproved') || 
      heading.includes('Additional Information Needed');
    expect(hasValidDecision).toBeTruthy();
    
    // Verify the decision field contains a valid value
    expect(resultText).toMatch(/Decision:\s*(APPROVED|DISAPPROVED|ADDITIONAL_INFO_NEEDED)/i);
    
    // Verify processing time is shown in milliseconds
    expect(resultText).toMatch(/Processing Time:\s*\d+ms/);
  });

  test('should submit application with poor credit and get appropriate decision', async ({ page }) => {
    // Check if API is running
    const apiHealthCheck = await page.request.get('http://localhost:8000/health').catch(() => null);
    if (!apiHealthCheck || !apiHealthCheck.ok()) {
      throw new Error('Backend API is not running. Please start the API server on port 8000 before running this test.');
    }

    // Fill in an application with poor credit indicators
    await page.locator('input[name="first_name"]').fill('John');
    await page.locator('input[name="last_name"]').fill('Doe');
    await page.locator('input[name="date_of_birth"]').fill('1990-05-20');
    await page.locator('input[name="ssn"]').fill('987-65-4321');
    await page.locator('input[name="email"]').fill('john.doe@example.com');
    await page.locator('input[name="phone"]').fill('+15559876543');
    await page.locator('input[name="address"]').fill('123 Main Street');
    await page.locator('input[name="city"]').fill('Portland');
    await page.locator('input[name="state"]').fill('OR');
    await page.locator('input[name="zip_code"]').fill('97201');

    // Employment - lower income
    await page.locator('select[name="employment_status"]').selectOption('employed');
    await page.locator('input[name="employer_name"]').fill('Small Shop');
    await page.locator('input[name="job_title"]').fill('Sales Associate');
    await page.locator('input[name="years_employed"]').fill('0.5');
    await page.locator('input[name="monthly_income"]').fill('2500');
    await page.locator('input[name="additional_income"]').fill('0');

    // Financial - minimal savings
    await page.locator('input[name="monthly_debt_payments"]').fill('1200');
    await page.locator('input[name="checking_balance"]').fill('500');
    await page.locator('input[name="savings_balance"]').fill('1000');
    await page.locator('input[name="investment_balance"]').fill('0');
    await page.locator('input[name="retirement_balance"]').fill('0');

    // Credit - poor indicators
    await page.locator('input[name="credit_score"]').fill('580');
    await page.locator('input[name="number_of_credit_cards"]').fill('2');
    await page.locator('input[name="total_credit_limit"]').fill('5000');
    await page.locator('input[name="credit_utilization"]').fill('85');
    await page.locator('input[name="number_of_late_payments_12m"]').fill('3');
    await page.locator('input[name="number_of_late_payments_24m"]').fill('5');
    await page.locator('input[name="number_of_inquiries_6m"]').fill('4');
    await page.locator('input[name="oldest_credit_line_years"]').fill('2');

    // Loan - requesting large amount relative to income
    await page.locator('input[name="loan_amount"]').fill('40000');
    await page.locator('select[name="loan_purpose"]').selectOption('debt_consolidation');
    await page.locator('input[name="term_months"]').fill('48');

    // Submit the form
    await page.locator('button', { hasText: 'Submit Application' }).click();

    // Wait for result
    await page.waitForSelector('.result', { timeout: 30000 });

    // Verify result is displayed
    await expect(page.locator('.result')).toBeVisible();
    
    const resultText = await page.locator('.result').textContent();
    
    // This application should likely be disapproved or need additional info
    // but we just verify we got a valid response
    expect(resultText).toContain('Decision');
    expect(resultText).toContain('Processing Time');
    
    // Verify we get some feedback - either disapproved or with reason/details
    const hasValidOutcome = 
      resultText.includes('disapproved') || 
      resultText.includes('Disapproved') ||
      resultText.includes('additional') ||
      resultText.includes('Reason') ||
      resultText.includes('Additional Info Needed');
    expect(hasValidOutcome).toBeTruthy();
  });
});
