# Infrastructure Makefile

.PHONY: help init plan deploy undeploy destroy

ENV ?= test
REGION ?= us-east-1

help: ## Show this help message
	@echo 'Infrastructure Management'
	@echo ''
	@echo 'Usage: make [target] ENV=<environment>'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo 'Environments: test, acceptance, prod'

init: ## Initialize Terraform
	@echo "Initializing Terraform for $(ENV) environment..."
	cd terraform && terraform init -backend-config="key=ai-agents-$(ENV).tfstate"

plan: ## Plan infrastructure changes
	@echo "Planning infrastructure changes for $(ENV)..."
	cd terraform && terraform plan -var-file="environments/$(ENV).tfvars" -out=$(ENV).tfplan

deploy: ## Deploy infrastructure
	@echo "Deploying infrastructure to $(ENV)..."
	cd terraform && terraform apply -var-file="environments/$(ENV).tfvars" -auto-approve

undeploy: destroy ## Alias for destroy

destroy: ## Destroy infrastructure
	@echo "⚠️  WARNING: This will destroy all infrastructure in $(ENV)!"
	@read -p "Are you sure? [yes/NO]: " confirm && [ "$$confirm" = "yes" ]
	cd terraform && terraform destroy -var-file="environments/$(ENV).tfvars" -auto-approve

validate: ## Validate Terraform configuration
	@echo "Validating Terraform configuration..."
	cd terraform && terraform validate

format: ## Format Terraform files
	@echo "Formatting Terraform files..."
	cd terraform && terraform fmt -recursive

clean: ## Clean Terraform artifacts
	@echo "Cleaning Terraform artifacts..."
	cd terraform && rm -rf .terraform *.tfplan *.tfstate*
