# Test Environment Configuration

environment      = "test"
aws_region       = "us-east-1"
databricks_host  = "https://your-databricks-workspace.cloud.databricks.com"

# Smaller resources for test
agent_configs = {
  loan_approval = {
    name          = "loan-approval"
    cpu           = 512
    memory        = 1024
    min_instances = 1
    max_instances = 3
  }
}

vpc_cidr            = "10.0.0.0/16"
enable_monitoring   = true
enable_nat_gateway  = false

tags = {
  CostCenter = "Engineering"
  Team       = "AI-Platform"
}
