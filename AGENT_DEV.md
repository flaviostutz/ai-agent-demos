## Initial creation

This project was initially created using the following prompt:

## functional requirements:

Create an AI Agent that receives a "new loan" request data (you can create the schema for this) and returns outcomes: approved (with associated risk from 0-100), disaproved (with reason), and additional_info_needed (description). The agent should check the loan rules in a set of documents that it has internally but also follow the best practices in the market (generate 2 pdfs as example rules).

## non-functional requirements:
gh workflow pipelines for lint, test and deployment when the repo is tagged
all code necessary for it to be create/deployed in a new databricks account

### Development practices
Pull Request review process integrated in the whole development cycle
Monorepo that comprises multiple agents and tools
Ability to run agents locally during development
Makefiles with build, lint, test, deploy, undeploy targets related to agent development for easy handover between platforms/new devs that can be run locally
Guide with developer instructions on how to create a new Agent from start to the final deployment

### Release and Provisioning
Automated deployments in Test, Acceptance and Production environments
Software and cloud resources deployed via ADO pipelines
AI Models, K8S, Databricks, AWS and Azure resources
Terraform CDK for IaaC, CDK for AWS
Automated quality checks during release pipelines
AI Agent performance checks, lint, test
Use Makefile targets used during local development for repeatability

### Quality checks
Automated AI agent performance measurement against dataset with groundtruth for each agent
Python code checked against Lint (custom set of rules) and Unit Tests (80% coverage)

### Observability
Agent tracing, logging, metrics (time to finish, errors, rejections)
Alarm notification on MS Teams Channel

### Security
Agent Tools with context permissioning
prevent data leakages even during LLM hallucinations or bugs

### Architecture
Compatible with Synera platform stack (Databricks, LangGraph, MLFlow etc)
Exposition of agents as REST services in Asgard API management
Interoperability with AWS resources for UI, workflows and custom services

Create the whole monorepo because this project is just starting

remove prometheus for monitoring and use databricks mosaic for everything that it's capable of. also use MLFlow for everything possible and add a dataset with automated model performance checks

all commands from the pipeline should run Makefile targets so the developer can also run the same commands that the pipeline executes locally

use the info found in the internal documents to help with the credit risk decision
