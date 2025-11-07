# Main Terraform configuration for AI Agents infrastructure

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Configure S3 backend for state management
    bucket = "ai-agents-terraform-state"
    key    = "agents/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Variables
variable "environment" {
  description = "Environment name (test, acceptance, production)"
  type        = string
}

variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks access token"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Providers
provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

provider "aws" {
  region = var.aws_region
}

# Databricks Workspace Configuration
resource "databricks_mlflow_experiment" "loan_approval" {
  name        = "/Shared/loan-approval-${var.environment}"
  description = "MLFlow experiment for loan approval agent - ${var.environment}"
  
  tags = {
    environment = var.environment
    agent       = "loan-approval"
    managed_by  = "terraform"
  }
}

resource "databricks_secret_scope" "agents" {
  name = "ai-agents-${var.environment}"
}

resource "databricks_secret" "openai_api_key" {
  scope      = databricks_secret_scope.agents.name
  key        = "openai-api-key"
  string_value = "placeholder" # Set via Databricks UI or CI/CD
}

# Databricks Cluster for agents
resource "databricks_cluster" "agents_cluster" {
  cluster_name            = "ai-agents-${var.environment}"
  spark_version           = "13.3.x-scala2.12"
  node_type_id            = "i3.xlarge"
  autotermination_minutes = 30
  
  autoscale {
    min_workers = 1
    max_workers = 4
  }

  spark_conf = {
    "spark.databricks.delta.preview.enabled" = "true"
  }

  custom_tags = {
    environment = var.environment
    purpose     = "ai-agents"
  }
}

# AWS Resources

# S3 Bucket for artifacts
resource "aws_s3_bucket" "agent_artifacts" {
  bucket = "ai-agents-artifacts-${var.environment}"
  
  tags = {
    Environment = var.environment
    Purpose     = "agent-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "agent_artifacts" {
  bucket = aws_s3_bucket.agent_artifacts.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "agent_artifacts" {
  bucket = aws_s3_bucket.agent_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# DynamoDB table for agent state (if needed)
resource "aws_dynamodb_table" "agent_state" {
  name           = "ai-agents-state-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "agent_id"
  range_key      = "timestamp"

  attribute {
    name = "agent_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "expiration_time"
    enabled        = true
  }

  tags = {
    Environment = var.environment
    Purpose     = "agent-state"
  }
}

# CloudWatch Log Group for agents
resource "aws_cloudwatch_log_group" "agents" {
  name              = "/aws/ai-agents/${var.environment}"
  retention_in_days = 30

  tags = {
    Environment = var.environment
    Purpose     = "agent-logs"
  }
}

# IAM Role for agents
resource "aws_iam_role" "agents" {
  name = "ai-agents-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "agents_policy" {
  name = "ai-agents-policy"
  role = aws_iam_role.agents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.agent_artifacts.arn,
          "${aws_s3_bucket.agent_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.agent_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.agents.arn}:*"
      }
    ]
  })
}

# Outputs
output "mlflow_experiment_id" {
  description = "MLFlow experiment ID"
  value       = databricks_mlflow_experiment.loan_approval.id
}

output "databricks_cluster_id" {
  description = "Databricks cluster ID"
  value       = databricks_cluster.agents_cluster.id
}

output "s3_bucket_name" {
  description = "S3 bucket for artifacts"
  value       = aws_s3_bucket.agent_artifacts.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table for agent state"
  value       = aws_dynamodb_table.agent_state.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group"
  value       = aws_cloudwatch_log_group.agents.name
}