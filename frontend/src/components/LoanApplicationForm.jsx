import { useState } from 'react';
import { loanAPI } from '../api';

const LoanApplicationForm = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errors, setErrors] = useState({});

  const [formData, setFormData] = useState({
    request_id: `REQ-${Date.now()}`,
    
    // Applicant Info
    first_name: '',
    last_name: '',
    date_of_birth: '',
    ssn: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',

    // Employment
    employment_status: 'employed',
    employer_name: '',
    job_title: '',
    years_employed: '',
    monthly_income: '',
    additional_income: '0',
    industry: '',
    industry_outlook: '',

    // Financial
    monthly_debt_payments: '0',
    checking_balance: '',
    savings_balance: '',
    investment_balance: '0',
    retirement_balance: '0',
    asset_reserves_months: '',
    has_bankruptcy: false,
    bankruptcy_date: '',
    has_foreclosure: false,
    foreclosure_date: '',

    // Credit History
    credit_score: '',
    number_of_credit_cards: '0',
    total_credit_limit: '0',
    credit_utilization: '0',
    number_of_late_payments_12m: '0',
    number_of_late_payments_24m: '0',
    number_of_inquiries_6m: '0',
    oldest_credit_line_years: '',
    payment_history: '',
    credit_mix: '',
    public_records: '',
    recent_inquiries: '',

    // Loan Details
    loan_amount: '',
    loan_purpose: 'personal',
    term_months: '',
    property_value: '',
    down_payment: '0',
    loan_to_value: '',
    front_end_dti: '',
    back_end_dti: '',
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Basic validations
    if (!formData.first_name) newErrors.first_name = 'First name is required';
    if (!formData.last_name) newErrors.last_name = 'Last name is required';
    if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required';
    if (!formData.ssn) newErrors.ssn = 'SSN is required';
    else if (!/^\d{3}-\d{2}-\d{4}$/.test(formData.ssn)) {
      newErrors.ssn = 'SSN must be in format XXX-XX-XXXX';
    }
    if (!formData.email) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.phone) newErrors.phone = 'Phone is required';
    if (!formData.address) newErrors.address = 'Address is required';
    if (!formData.city) newErrors.city = 'City is required';
    if (!formData.state) newErrors.state = 'State is required';
    if (!formData.zip_code) newErrors.zip_code = 'Zip code is required';

    // Employment validations
    if (!formData.monthly_income || parseFloat(formData.monthly_income) <= 0) {
      newErrors.monthly_income = 'Monthly income is required and must be positive';
    }
    if ((formData.employment_status === 'employed' || formData.employment_status === 'self_employed')) {
      if (!formData.employer_name) newErrors.employer_name = 'Employer name is required';
      if (!formData.job_title) newErrors.job_title = 'Job title is required';
    }

    // Credit validations
    if (!formData.credit_score) newErrors.credit_score = 'Credit score is required';
    else if (parseInt(formData.credit_score) < 300 || parseInt(formData.credit_score) > 850) {
      newErrors.credit_score = 'Credit score must be between 300 and 850';
    }

    // Loan validations
    if (!formData.loan_amount || parseFloat(formData.loan_amount) <= 0) {
      newErrors.loan_amount = 'Loan amount is required and must be positive';
    }
    if (!formData.term_months || parseInt(formData.term_months) <= 0) {
      newErrors.term_months = 'Loan term is required and must be positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      alert('Please fix the errors in the form');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Transform form data to API format
      const payload = {
        request_id: formData.request_id,
        applicant: {
          first_name: formData.first_name,
          last_name: formData.last_name,
          date_of_birth: formData.date_of_birth,
          ssn: formData.ssn,
          email: formData.email,
          phone: formData.phone,
          address: formData.address,
          city: formData.city,
          state: formData.state,
          zip_code: formData.zip_code,
        },
        employment: {
          status: formData.employment_status,
          employer_name: formData.employer_name || null,
          job_title: formData.job_title || null,
          years_employed: formData.years_employed ? parseFloat(formData.years_employed) : null,
          monthly_income: parseFloat(formData.monthly_income),
          additional_income: parseFloat(formData.additional_income) || 0,
          industry: formData.industry || null,
          industry_outlook: formData.industry_outlook || null,
        },
        financial: {
          monthly_debt_payments: parseFloat(formData.monthly_debt_payments) || 0,
          monthly_debt_breakdown: null,
          checking_balance: formData.checking_balance ? parseFloat(formData.checking_balance) : null,
          savings_balance: formData.savings_balance ? parseFloat(formData.savings_balance) : null,
          investment_balance: parseFloat(formData.investment_balance) || null,
          retirement_balance: parseFloat(formData.retirement_balance) || null,
          asset_reserves_months: formData.asset_reserves_months ? parseFloat(formData.asset_reserves_months) : null,
          has_bankruptcy: formData.has_bankruptcy,
          bankruptcy_date: formData.bankruptcy_date || null,
          has_foreclosure: formData.has_foreclosure,
          foreclosure_date: formData.foreclosure_date || null,
        },
        credit_history: {
          credit_score: parseInt(formData.credit_score),
          number_of_credit_cards: parseInt(formData.number_of_credit_cards) || 0,
          total_credit_limit: parseFloat(formData.total_credit_limit) || 0,
          credit_utilization: parseFloat(formData.credit_utilization) || 0,
          number_of_late_payments_12m: parseInt(formData.number_of_late_payments_12m) || 0,
          number_of_late_payments_24m: parseInt(formData.number_of_late_payments_24m) || 0,
          number_of_inquiries_6m: parseInt(formData.number_of_inquiries_6m) || 0,
          oldest_credit_line_years: formData.oldest_credit_line_years ? parseFloat(formData.oldest_credit_line_years) : null,
          payment_history: formData.payment_history || null,
          credit_mix: formData.credit_mix || null,
          public_records: formData.public_records || null,
          recent_inquiries: formData.recent_inquiries || null,
        },
        loan_details: {
          amount: parseFloat(formData.loan_amount),
          purpose: formData.loan_purpose,
          term_months: parseInt(formData.term_months),
          property_value: formData.property_value ? parseFloat(formData.property_value) : null,
          down_payment: parseFloat(formData.down_payment) || 0,
          loan_to_value: formData.loan_to_value ? parseFloat(formData.loan_to_value) : null,
          front_end_dti: formData.front_end_dti ? parseFloat(formData.front_end_dti) : null,
          back_end_dti: formData.back_end_dti ? parseFloat(formData.back_end_dti) : null,
        },
      };

      const response = await loanAPI.submitApplication(payload);
      setResult(response);
      
      // Scroll to result
      setTimeout(() => {
        document.querySelector('.result')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      request_id: `REQ-${Date.now()}`,
      first_name: '',
      last_name: '',
      date_of_birth: '',
      ssn: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      employment_status: 'employed',
      employer_name: '',
      job_title: '',
      years_employed: '',
      monthly_income: '',
      additional_income: '0',
      industry: '',
      industry_outlook: '',
      monthly_debt_payments: '0',
      checking_balance: '',
      savings_balance: '',
      investment_balance: '0',
      retirement_balance: '0',
      asset_reserves_months: '',
      has_bankruptcy: false,
      bankruptcy_date: '',
      has_foreclosure: false,
      foreclosure_date: '',
      credit_score: '',
      number_of_credit_cards: '0',
      total_credit_limit: '0',
      credit_utilization: '0',
      number_of_late_payments_12m: '0',
      number_of_late_payments_24m: '0',
      number_of_inquiries_6m: '0',
      oldest_credit_line_years: '',
      payment_history: '',
      credit_mix: '',
      public_records: '',
      recent_inquiries: '',
      loan_amount: '',
      loan_purpose: 'personal',
      term_months: '',
      property_value: '',
      down_payment: '0',
      loan_to_value: '',
      front_end_dti: '',
      back_end_dti: '',
    });
    setErrors({});
    setResult(null);
  };

  const generateRandomData = () => {
    const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Maria'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
    const streets = ['Main St', 'Oak Ave', 'Maple Dr', 'Cedar Ln', 'Pine Rd', 'Elm St', 'Washington Blvd', 'Park Ave', '1st Street', 'Broadway'];
    const cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Seattle', 'Boston', 'Austin', 'Denver', 'Portland'];
    const states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'WA', 'MA', 'TX', 'CO', 'OR'];
    const employers = ['Tech Corp', 'Financial Services Inc', 'Healthcare Solutions', 'Manufacturing Co', 'Retail Group', 'Consulting Partners', 'Engineering Firm', 'Design Studio'];
    const jobTitles = ['Software Engineer', 'Project Manager', 'Accountant', 'Sales Manager', 'Data Analyst', 'Marketing Specialist', 'Operations Manager', 'Business Analyst'];
    const industries = ['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Consulting', 'Engineering', 'Education'];
    const loanPurposes = ['personal', 'auto', 'home_purchase', 'debt_consolidation', 'business', 'education'];

    const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
    const randomChoice = (arr) => arr[random(0, arr.length - 1)];
    const randomFloat = (min, max, decimals = 2) => (Math.random() * (max - min) + min).toFixed(decimals);

    // Generate date of birth (25-65 years old)
    const today = new Date();
    const birthYear = today.getFullYear() - random(25, 65);
    const birthMonth = String(random(1, 12)).padStart(2, '0');
    const birthDay = String(random(1, 28)).padStart(2, '0');
    
    const firstName = randomChoice(firstNames);
    const lastName = randomChoice(lastNames);
    const cityIndex = random(0, cities.length - 1);
    const loanPurpose = randomChoice(loanPurposes);
    const creditScore = random(650, 820);
    const monthlyIncome = random(4000, 15000);
    const loanAmount = random(10000, 300000);

    setFormData({
      request_id: `REQ-${Date.now()}`,
      
      // Personal Info
      first_name: firstName,
      last_name: lastName,
      date_of_birth: `${birthYear}-${birthMonth}-${birthDay}`,
      ssn: `${random(100, 999)}-${random(10, 99)}-${random(1000, 9999)}`,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
      phone: `+1${random(200, 999)}${random(100, 999)}${random(1000, 9999)}`,
      address: `${random(100, 9999)} ${randomChoice(streets)}`,
      city: cities[cityIndex],
      state: states[cityIndex],
      zip_code: `${random(10000, 99999)}`,

      // Employment
      employment_status: random(0, 10) > 1 ? 'employed' : 'self_employed',
      employer_name: randomChoice(employers),
      job_title: randomChoice(jobTitles),
      years_employed: randomFloat(0.5, 15, 1),
      monthly_income: monthlyIncome.toString(),
      additional_income: random(0, 2000).toString(),
      industry: randomChoice(industries),
      industry_outlook: 'Stable with growth prospects',

      // Financial
      monthly_debt_payments: random(500, 3000).toString(),
      checking_balance: random(1000, 20000).toString(),
      savings_balance: random(5000, 80000).toString(),
      investment_balance: random(0, 100000).toString(),
      retirement_balance: random(10000, 200000).toString(),
      asset_reserves_months: randomFloat(2, 12, 1),
      has_bankruptcy: false,
      bankruptcy_date: '',
      has_foreclosure: false,
      foreclosure_date: '',

      // Credit History
      credit_score: creditScore.toString(),
      number_of_credit_cards: random(1, 6).toString(),
      total_credit_limit: random(10000, 80000).toString(),
      credit_utilization: randomFloat(5, 40, 1),
      number_of_late_payments_12m: random(0, 2).toString(),
      number_of_late_payments_24m: random(0, 3).toString(),
      number_of_inquiries_6m: random(0, 3).toString(),
      oldest_credit_line_years: randomFloat(2, 20, 1),
      payment_history: 'Generally good payment history',
      credit_mix: 'Diversified credit portfolio',
      public_records: 'None',
      recent_inquiries: 'Standard credit inquiries',

      // Loan Details
      loan_amount: loanAmount.toString(),
      loan_purpose: loanPurpose,
      term_months: loanPurpose === 'home_purchase' ? '360' : loanPurpose === 'auto' ? '60' : random(12, 84).toString(),
      property_value: loanPurpose === 'home_purchase' || loanPurpose === 'home_refinance' ? (loanAmount * 1.2).toString() : '',
      down_payment: loanPurpose === 'home_purchase' ? (loanAmount * 0.2).toString() : '0',
      loan_to_value: '',
      front_end_dti: '',
      back_end_dti: '',
    });
    
    setErrors({});
    setResult(null);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* Personal Information Section */}
      <div className="section">
        <h2>Personal Information</h2>
        <div className="form-grid">
          <div className={`form-group ${errors.first_name ? 'error' : ''}`}>
            <label>First Name *</label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              placeholder="John"
            />
            {errors.first_name && <span className="error-message">{errors.first_name}</span>}
          </div>

          <div className={`form-group ${errors.last_name ? 'error' : ''}`}>
            <label>Last Name *</label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              placeholder="Doe"
            />
            {errors.last_name && <span className="error-message">{errors.last_name}</span>}
          </div>

          <div className={`form-group ${errors.date_of_birth ? 'error' : ''}`}>
            <label>Date of Birth *</label>
            <input
              type="date"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleChange}
            />
            {errors.date_of_birth && <span className="error-message">{errors.date_of_birth}</span>}
          </div>

          <div className={`form-group ${errors.ssn ? 'error' : ''}`}>
            <label>SSN * (XXX-XX-XXXX)</label>
            <input
              type="text"
              name="ssn"
              value={formData.ssn}
              onChange={handleChange}
              placeholder="123-45-6789"
            />
            {errors.ssn && <span className="error-message">{errors.ssn}</span>}
          </div>

          <div className={`form-group ${errors.email ? 'error' : ''}`}>
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="john.doe@example.com"
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className={`form-group ${errors.phone ? 'error' : ''}`}>
            <label>Phone *</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+15551234567"
            />
            {errors.phone && <span className="error-message">{errors.phone}</span>}
          </div>

          <div className={`form-group full-width ${errors.address ? 'error' : ''}`}>
            <label>Address *</label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="123 Main Street"
            />
            {errors.address && <span className="error-message">{errors.address}</span>}
          </div>

          <div className={`form-group ${errors.city ? 'error' : ''}`}>
            <label>City *</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="New York"
            />
            {errors.city && <span className="error-message">{errors.city}</span>}
          </div>

          <div className={`form-group ${errors.state ? 'error' : ''}`}>
            <label>State * (2 letters)</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              placeholder="NY"
              maxLength="2"
            />
            {errors.state && <span className="error-message">{errors.state}</span>}
          </div>

          <div className={`form-group ${errors.zip_code ? 'error' : ''}`}>
            <label>Zip Code *</label>
            <input
              type="text"
              name="zip_code"
              value={formData.zip_code}
              onChange={handleChange}
              placeholder="10001"
            />
            {errors.zip_code && <span className="error-message">{errors.zip_code}</span>}
          </div>
        </div>
      </div>

      {/* Employment Information Section */}
      <div className="section">
        <h2>Employment Information</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Employment Status *</label>
            <select
              name="employment_status"
              value={formData.employment_status}
              onChange={handleChange}
            >
              <option value="employed">Employed</option>
              <option value="self_employed">Self Employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="retired">Retired</option>
              <option value="student">Student</option>
            </select>
          </div>

          <div className={`form-group ${errors.employer_name ? 'error' : ''}`}>
            <label>Employer Name {(formData.employment_status === 'employed' || formData.employment_status === 'self_employed') ? '*' : ''}</label>
            <input
              type="text"
              name="employer_name"
              value={formData.employer_name}
              onChange={handleChange}
              placeholder="Company Name"
            />
            {errors.employer_name && <span className="error-message">{errors.employer_name}</span>}
          </div>

          <div className={`form-group ${errors.job_title ? 'error' : ''}`}>
            <label>Job Title {(formData.employment_status === 'employed' || formData.employment_status === 'self_employed') ? '*' : ''}</label>
            <input
              type="text"
              name="job_title"
              value={formData.job_title}
              onChange={handleChange}
              placeholder="Software Engineer"
            />
            {errors.job_title && <span className="error-message">{errors.job_title}</span>}
          </div>

          <div className="form-group">
            <label>Years Employed</label>
            <input
              type="number"
              name="years_employed"
              value={formData.years_employed}
              onChange={handleChange}
              placeholder="5.5"
              step="0.1"
              min="0"
            />
          </div>

          <div className={`form-group ${errors.monthly_income ? 'error' : ''}`}>
            <label>Monthly Income * ($)</label>
            <input
              type="number"
              name="monthly_income"
              value={formData.monthly_income}
              onChange={handleChange}
              placeholder="5000"
              step="0.01"
              min="0"
            />
            {errors.monthly_income && <span className="error-message">{errors.monthly_income}</span>}
          </div>

          <div className="form-group">
            <label>Additional Income ($)</label>
            <input
              type="number"
              name="additional_income"
              value={formData.additional_income}
              onChange={handleChange}
              placeholder="0"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group full-width">
            <label>Industry</label>
            <input
              type="text"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              placeholder="Technology"
            />
          </div>

          <div className="form-group full-width">
            <label>Industry Outlook</label>
            <textarea
              name="industry_outlook"
              value={formData.industry_outlook}
              onChange={handleChange}
              placeholder="Stable with strong growth prospects"
              rows="2"
            />
          </div>
        </div>
      </div>

      {/* Financial Information Section */}
      <div className="section">
        <h2>Financial Information</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Monthly Debt Payments ($)</label>
            <input
              type="number"
              name="monthly_debt_payments"
              value={formData.monthly_debt_payments}
              onChange={handleChange}
              placeholder="1000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Checking Balance ($)</label>
            <input
              type="number"
              name="checking_balance"
              value={formData.checking_balance}
              onChange={handleChange}
              placeholder="5000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Savings Balance ($)</label>
            <input
              type="number"
              name="savings_balance"
              value={formData.savings_balance}
              onChange={handleChange}
              placeholder="10000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Investment Balance ($)</label>
            <input
              type="number"
              name="investment_balance"
              value={formData.investment_balance}
              onChange={handleChange}
              placeholder="20000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Retirement Balance ($)</label>
            <input
              type="number"
              name="retirement_balance"
              value={formData.retirement_balance}
              onChange={handleChange}
              placeholder="50000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Asset Reserves (months)</label>
            <input
              type="number"
              name="asset_reserves_months"
              value={formData.asset_reserves_months}
              onChange={handleChange}
              placeholder="6"
              step="0.1"
              min="0"
            />
          </div>

          <div className="form-group checkbox-group">
            <input
              type="checkbox"
              name="has_bankruptcy"
              checked={formData.has_bankruptcy}
              onChange={handleChange}
              id="has_bankruptcy"
            />
            <label htmlFor="has_bankruptcy">Has Bankruptcy</label>
          </div>

          {formData.has_bankruptcy && (
            <div className="form-group">
              <label>Bankruptcy Date</label>
              <input
                type="date"
                name="bankruptcy_date"
                value={formData.bankruptcy_date}
                onChange={handleChange}
              />
            </div>
          )}

          <div className="form-group checkbox-group">
            <input
              type="checkbox"
              name="has_foreclosure"
              checked={formData.has_foreclosure}
              onChange={handleChange}
              id="has_foreclosure"
            />
            <label htmlFor="has_foreclosure">Has Foreclosure</label>
          </div>

          {formData.has_foreclosure && (
            <div className="form-group">
              <label>Foreclosure Date</label>
              <input
                type="date"
                name="foreclosure_date"
                value={formData.foreclosure_date}
                onChange={handleChange}
              />
            </div>
          )}
        </div>
      </div>

      {/* Credit History Section */}
      <div className="section">
        <h2>Credit History</h2>
        <div className="form-grid">
          <div className={`form-group ${errors.credit_score ? 'error' : ''}`}>
            <label>Credit Score * (300-850)</label>
            <input
              type="number"
              name="credit_score"
              value={formData.credit_score}
              onChange={handleChange}
              placeholder="700"
              min="300"
              max="850"
            />
            {errors.credit_score && <span className="error-message">{errors.credit_score}</span>}
          </div>

          <div className="form-group">
            <label>Number of Credit Cards</label>
            <input
              type="number"
              name="number_of_credit_cards"
              value={formData.number_of_credit_cards}
              onChange={handleChange}
              placeholder="3"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Total Credit Limit ($)</label>
            <input
              type="number"
              name="total_credit_limit"
              value={formData.total_credit_limit}
              onChange={handleChange}
              placeholder="30000"
              step="0.01"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Credit Utilization (%)</label>
            <input
              type="number"
              name="credit_utilization"
              value={formData.credit_utilization}
              onChange={handleChange}
              placeholder="20"
              step="0.1"
              min="0"
              max="100"
            />
          </div>

          <div className="form-group">
            <label>Late Payments (12 months)</label>
            <input
              type="number"
              name="number_of_late_payments_12m"
              value={formData.number_of_late_payments_12m}
              onChange={handleChange}
              placeholder="0"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Late Payments (24 months)</label>
            <input
              type="number"
              name="number_of_late_payments_24m"
              value={formData.number_of_late_payments_24m}
              onChange={handleChange}
              placeholder="0"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Credit Inquiries (6 months)</label>
            <input
              type="number"
              name="number_of_inquiries_6m"
              value={formData.number_of_inquiries_6m}
              onChange={handleChange}
              placeholder="0"
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Oldest Credit Line (years)</label>
            <input
              type="number"
              name="oldest_credit_line_years"
              value={formData.oldest_credit_line_years}
              onChange={handleChange}
              placeholder="10"
              step="0.1"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Loan Details Section */}
      <div className="section">
        <h2>Loan Details</h2>
        <div className="form-grid">
          <div className={`form-group ${errors.loan_amount ? 'error' : ''}`}>
            <label>Loan Amount * ($)</label>
            <input
              type="number"
              name="loan_amount"
              value={formData.loan_amount}
              onChange={handleChange}
              placeholder="50000"
              step="0.01"
              min="0"
            />
            {errors.loan_amount && <span className="error-message">{errors.loan_amount}</span>}
          </div>

          <div className="form-group">
            <label>Loan Purpose *</label>
            <select
              name="loan_purpose"
              value={formData.loan_purpose}
              onChange={handleChange}
            >
              <option value="home_purchase">Home Purchase</option>
              <option value="home_refinance">Home Refinance</option>
              <option value="auto">Auto</option>
              <option value="personal">Personal</option>
              <option value="business">Business</option>
              <option value="education">Education</option>
              <option value="debt_consolidation">Debt Consolidation</option>
            </select>
          </div>

          <div className={`form-group ${errors.term_months ? 'error' : ''}`}>
            <label>Loan Term * (months)</label>
            <input
              type="number"
              name="term_months"
              value={formData.term_months}
              onChange={handleChange}
              placeholder="60"
              min="1"
              max="360"
            />
            {errors.term_months && <span className="error-message">{errors.term_months}</span>}
          </div>

          {(formData.loan_purpose === 'home_purchase' || formData.loan_purpose === 'home_refinance') && (
            <>
              <div className="form-group">
                <label>Property Value ($)</label>
                <input
                  type="number"
                  name="property_value"
                  value={formData.property_value}
                  onChange={handleChange}
                  placeholder="300000"
                  step="0.01"
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Down Payment ($)</label>
                <input
                  type="number"
                  name="down_payment"
                  value={formData.down_payment}
                  onChange={handleChange}
                  placeholder="60000"
                  step="0.01"
                  min="0"
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="button-container">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span> Processing...
            </>
          ) : (
            'Submit Application'
          )}
        </button>
        <button type="button" className="btn btn-secondary" onClick={generateRandomData} disabled={loading}>
          🎲 Generate Random Data
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleReset} disabled={loading}>
          Reset Form
        </button>
      </div>

      {/* Result Display */}
      {result && (
        <div className={`result ${result.decision.decision}`}>
          <h3>
            {result.decision.decision === 'approved' && '✓ Application Approved!'}
            {result.decision.decision === 'disapproved' && '✗ Application Disapproved'}
            {result.decision.decision === 'additional_info_needed' && '⚠ Additional Information Needed'}
          </h3>
          <p><strong>Request ID:</strong> {result.request_id}</p>
          <p><strong>Decision:</strong> {result.decision.decision.replace('_', ' ').toUpperCase()}</p>
          {result.decision.risk_score !== null && result.decision.risk_score !== undefined && (
            <p><strong>Risk Score:</strong> {result.decision.risk_score}</p>
          )}
          {result.decision.disapproval_reason && (
            <p><strong>Reason:</strong> {result.decision.disapproval_reason}</p>
          )}
          {result.decision.additional_info_description && (
            <p><strong>Additional Info Needed:</strong> {result.decision.additional_info_description}</p>
          )}
          {result.decision.recommended_amount && (
            <p><strong>Recommended Amount:</strong> ${parseFloat(result.decision.recommended_amount).toLocaleString()}</p>
          )}
          {result.decision.recommended_term_months && (
            <p><strong>Recommended Term:</strong> {result.decision.recommended_term_months} months</p>
          )}
          {result.decision.interest_rate && (
            <p><strong>Interest Rate:</strong> {result.decision.interest_rate}%</p>
          )}
          {result.decision.monthly_payment && (
            <p><strong>Monthly Payment:</strong> ${parseFloat(result.decision.monthly_payment).toLocaleString()}</p>
          )}
          <p><strong>Processing Time:</strong> {result.processing_time_ms}ms</p>
          {result.timestamp && (
            <p><strong>Timestamp:</strong> {new Date(result.timestamp).toLocaleString()}</p>
          )}
        </div>
      )}
    </form>
  );
};

export default LoanApplicationForm;
