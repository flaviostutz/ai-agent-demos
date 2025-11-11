import { useState } from 'react';
import LoanApplicationForm from './components/LoanApplicationForm';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>Loan Application Portal</h1>
        <p>AI-Powered Instant Loan Evaluation</p>
      </header>
      <div className="form-container">
        <LoanApplicationForm />
      </div>
    </div>
  );
}

export default App;
