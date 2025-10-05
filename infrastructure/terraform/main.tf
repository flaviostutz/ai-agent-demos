# Terraform Configuration for AI Agents Platform

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }

  backend "s3" {
    bucket         = "ai-agents-terraform-state"
    key            = "ai-agents.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "ai-agents-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Agents"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "databricks" {
  host = var.databricks_host
}
