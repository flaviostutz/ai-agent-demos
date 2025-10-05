# ECS Cluster for Agent APIs

resource "aws_ecs_cluster" "agents" {
  name = "${var.project_name}-${var.environment}-agents"

  setting {
    name  = "containerInsights"
    value = var.enable_monitoring ? "enabled" : "disabled"
  }

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "agents" {
  name              = "/ecs/${var.project_name}-${var.environment}-agents"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = var.tags
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-${var.environment}-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-${var.environment}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Policy for accessing Secrets Manager, S3, etc.
resource "aws_iam_role_policy" "ecs_task_policy" {
  name = "${var.project_name}-${var.environment}-ecs-task-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "s3:GetObject",
          "s3:PutObject",
        ]
        Resource = "*"
      }
    ]
  })
}

# ECR Repository for agent images
resource "aws_ecr_repository" "loan_approval" {
  name                 = "${var.project_name}/${var.environment}/loan-approval"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ECS Task Definition for Loan Approval Agent
resource "aws_ecs_task_definition" "loan_approval" {
  family                   = "${var.project_name}-${var.environment}-loan-approval"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_configs["loan_approval"].cpu
  memory                   = var.agent_configs["loan_approval"].memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "loan-approval"
      image = "${aws_ecr_repository.loan_approval.repository_url}:latest"

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "LOG_LEVEL"
          value = var.environment == "prod" ? "INFO" : "DEBUG"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.openai_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.agents.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "loan-approval"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = var.tags
}

# Application Load Balancer
resource "aws_lb" "agents" {
  name               = "${var.project_name}-${var.environment}-agents-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.agent_api.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "prod"

  tags = var.tags
}

# Target Group
resource "aws_lb_target_group" "loan_approval" {
  name        = "${var.project_name}-${var.environment}-loan-approval"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  tags = var.tags
}

# Listener
resource "aws_lb_listener" "agents" {
  load_balancer_arn = aws_lb.agents.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.loan_approval.arn
  }
}

# ECS Service
resource "aws_ecs_service" "loan_approval" {
  name            = "loan-approval"
  cluster         = aws_ecs_cluster.agents.id
  task_definition = aws_ecs_task_definition.loan_approval.arn
  desired_count   = var.agent_configs["loan_approval"].min_instances
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.agent_api.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.loan_approval.arn
    container_name   = "loan-approval"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.agents]

  tags = var.tags
}

# Auto Scaling
resource "aws_appautoscaling_target" "loan_approval" {
  max_capacity       = var.agent_configs["loan_approval"].max_instances
  min_capacity       = var.agent_configs["loan_approval"].min_instances
  resource_id        = "service/${aws_ecs_cluster.agents.name}/${aws_ecs_service.loan_approval.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "loan_approval_cpu" {
  name               = "${var.project_name}-${var.environment}-loan-approval-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.loan_approval.resource_id
  scalable_dimension = aws_appautoscaling_target.loan_approval.scalable_dimension
  service_namespace  = aws_appautoscaling_target.loan_approval.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Secrets Manager for sensitive data
resource "aws_secretsmanager_secret" "openai_api_key" {
  name = "${var.project_name}/${var.environment}/openai-api-key"

  tags = var.tags
}
