# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial monorepo structure
- Loan approval AI agent with LangGraph
- Comprehensive data models for loan processing
- MLFlow integration for experiment tracking
- Databricks Mosaic AI integration for monitoring
- Security context with permission-based access control
- MS Teams notifications for deployments and alerts
- Ground truth dataset with 6 test cases
- Performance testing framework
- CI/CD pipelines for automated testing and deployment
- Terraform infrastructure configuration
- Developer guide and documentation
- Pull request templates
- Makefile targets for development workflow

### Features

#### Loan Approval Agent
- Multi-step decision workflow using LangGraph
- Credit risk assessment (0-100 risk score)
- Policy document integration (PDF)
- Three decision outcomes: approved, disapproved, additional_info_needed
- Comprehensive validation and eligibility checks
- DTI ratio calculation and evaluation
- Employment verification
- Credit history analysis
- Bankruptcy and foreclosure handling

#### Observability
- Structured logging with configurable levels
- MLFlow experiment tracking
- Processing time metrics
- Risk score tracking
- Decision outcome tracking
- Agent trace IDs for debugging

#### Security
- Context-based permissioning system
- Data filtering based on permissions
- PII, financial, and credit data protection
- Environment-based access control

#### Development Tools
- Automated code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- Unit tests with 80% coverage target
- Integration tests
- Performance tests against ground truth

#### CI/CD
- Automated testing on PR
- Security scanning with Trivy
- Test coverage reporting
- Automated deployment to test/acceptance/production
- MS Teams notifications for deployment status
- Manual approval for production deployments

#### Infrastructure
- Databricks MLFlow experiment configuration
- Databricks cluster provisioning
- AWS S3 for artifact storage
- AWS DynamoDB for state management
- CloudWatch logging
- IAM roles and policies

## [0.1.0] - 2024-01-15

### Added
- Initial project setup
- Core monorepo structure
- Loan approval agent implementation
- Basic documentation

---

## Version Guidelines

- **Major version (X.0.0)**: Breaking changes
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, backward compatible

## Release Process

1. Update CHANGELOG.md with changes
2. Update version in pyproject.toml
3. Create Git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`
5. GitHub Actions will handle deployment