# Loan Approval Agent

AI agent for automated loan application processing and risk assessment.

## Overview

This agent evaluates loan applications based on:
- Applicant personal and employment information
- Financial history and current status
- Credit history and score
- Loan-specific policies from internal documents
- Industry best practices

## Outcomes

- **Approved**: Loan approved with risk score (0-100)
- **Disapproved**: Loan rejected with detailed reason
- **Additional Info Needed**: More information required with description

## Features

- LangGraph-based multi-step decision workflow
- MLFlow model tracking and versioning
- Policy document integration (PDF)
- Security context with permission checking
- Comprehensive observability (tracing, metrics, logging)
- Automated performance testing against ground truth dataset

## Local Development

### Setup

```bash
cd agents/loan-approval
make install
```

### Run Locally

```bash
make run-local
```

### Test

```bash
make test
make performance-test
```

### Lint

```bash
make lint
```

## Deployment

### Deploy to Test Environment

```bash
make deploy ENV=test
```

### Deploy to Production

```bash
make deploy ENV=production
```

### Undeploy

```bash
make undeploy
```

## Configuration

Configure via environment variables:

- `OPENAI_API_KEY`: OpenAI API key for LLM
- `MLFLOW_TRACKING_URI`: MLFlow tracking server URI
- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Databricks access token
- `TEAMS_WEBHOOK_URL`: MS Teams webhook for notifications
- `ENVIRONMENT`: Deployment environment (development/test/production)

## Project Structure

```
loan-approval/
├── src/
│   ├── agent.py           # Main agent implementation
│   ├── graph.py           # LangGraph workflow definition
│   ├── tools.py           # Agent tools and functions
│   ├── config.py          # Configuration management
│   └── api.py             # REST API service
├── tests/
│   ├── test_agent.py      # Unit tests
│   ├── test_integration.py # Integration tests
│   └── test_performance.py # Performance tests
├── datasets/
│   ├── ground_truth.json  # Ground truth dataset
│   └── test_cases.json    # Test cases
├── policies/
│   ├── loan_policy_v1.pdf # Internal loan policies
│   └── best_practices.pdf # Industry best practices
├── Makefile               # Build targets
└── README.md
```

## Performance Metrics

The agent tracks:
- Processing time per request
- Decision accuracy against ground truth
- Error rates and types
- Risk score distribution
- Approval/rejection rates

Metrics are logged to MLFlow and monitored via Databricks Mosaic AI.