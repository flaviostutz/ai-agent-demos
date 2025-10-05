# Production Environment Configuration

environment      = "prod"
aws_region       = "us-east-1"
databricks_host  = "https://your-databricks-workspace.cloud.databricks.com"

# Production-grade resources
agent_configs = {
  loan_approval = {
    name          = "loan-approval"
    cpu           = 2048
    memory        = 4096
    min_instances = 3
    max_instances = 20
  }
}

vpc_cidr            = "10.1.0.0/16"
enable_monitoring   = true
enable_nat_gateway  = true

tags = {
  CostCenter  = "Production"
  Team        = "AI-Platform"
  Compliance  = "SOC2"
}
