variable "environment" {
  description = "Environment name (test, acceptance, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-agents"
}

variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks authentication token"
  type        = string
  sensitive   = true
}

variable "agent_configs" {
  description = "Configuration for agents"
  type = map(object({
    name          = string
    cpu           = number
    memory        = number
    min_instances = number
    max_instances = number
  }))
  default = {
    loan_approval = {
      name          = "loan-approval"
      cpu           = 1024
      memory        = 2048
      min_instances = 1
      max_instances = 10
    }
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
