resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}


//api task definition

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-${var.environment}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.api_task.arn

  container_definitions = jsonencode([
    {
      name      = "oms-api"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ASPNETCORE_ENVIRONMENT"
          value = "Production"
        },
        {
          name  = "ASPNETCORE_URLS"
          value = "http://+:8080"
        },
        {
          name  = "AWS__SNS__Region"
          value = var.aws_region
        },
        {
          name  = "AWS__SNS__TopicArn"
          value = aws_sns_topic.order_created.arn
        },
        {
          name  = "Database__Host"
          value = aws_db_instance.postgres.address
        },
        {
          name  = "Database__Port"
          value = tostring(aws_db_instance.postgres.port)
        },
        {
          name  = "Database__Name"
          value = var.db_name
        },
        {
          name  = "Database__Username"
          value = var.db_username
        },
        {
          name  = "Database__RunMigrationsOnly"
          value = "false"
        },
        {
          name  = "AzureAd__Instance"
          value = "https://login.microsoftonline.com/"
        },
        {
          name  = "AzureAd__TenantId"
          value = "7a971eb6-18c3-4d21-a9d4-cde169b35a09"
        },
        {
          name  = "AzureAd__ClientId"
          value = "13a4204d-792f-4ec3-9c1a-80a507104a9b"
        }
      ]

      secrets = [
        {
          name = "Database__Password"

          valueFrom = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }
    }
  ])
}


// erp task definition

resource "aws_ecs_task_definition" "erp_worker" {
  family                   = "${var.project_name}-${var.environment}-erp-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.erp_worker_task.arn

  container_definitions = jsonencode([
    {
      name      = "oms-erp-worker"
      image     = "${aws_ecr_repository.erp_worker.repository_url}:latest"
      essential = true

      environment = [
        {
          name  = "DOTNET_ENVIRONMENT"
          value = "Production"
        },
        {
          name  = "AWS__SQS__Region"
          value = var.aws_region
        },
        {
          name  = "AWS__SQS__QueueUrl"
          value = aws_sqs_queue.erp_queue.id
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.erp_worker.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "erp"
        }
      }
    }
  ])
}

// notification worker definition

resource "aws_ecs_task_definition" "notification_worker" {
  family                   = "${var.project_name}-${var.environment}-notification-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.notification_worker_task.arn

  container_definitions = jsonencode([
    {
      name      = "oms-notification-worker"
      image     = "${aws_ecr_repository.notification_worker.repository_url}:latest"
      essential = true

      environment = [
        {
          name  = "DOTNET_ENVIRONMENT"
          value = "Production"
        },
        {
          name  = "AWS__SQS__Region"
          value = var.aws_region
        },
        {
          name  = "AWS__SQS__QueueUrl"
          value = aws_sqs_queue.notification_queue.id
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.notification_worker.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "notification"
        }
      }
    }
  ])
}


// erp worker

resource "aws_ecs_service" "erp_worker" {
  name            = "${var.project_name}-${var.environment}-erp-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.erp_worker.arn

  launch_type   = "FARGATE"
  desired_count = 1

  network_configuration {
    subnets = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id
    ]

    security_groups = [
      aws_security_group.ecs_tasks.id
    ]

    assign_public_ip = true
  }
}

// notification worker

resource "aws_ecs_service" "notification_worker" {
  name            = "${var.project_name}-${var.environment}-notification-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.notification_worker.arn

  launch_type   = "FARGATE"
  desired_count = 1

  network_configuration {
    subnets = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id
    ]

    security_groups = [
      aws_security_group.ecs_tasks.id
    ]

    assign_public_ip = true
  }
}

// create api service

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn

  launch_type = "FARGATE"

  desired_count = 1

  network_configuration {
    subnets = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id
    ]

    security_groups = [
      aws_security_group.ecs_tasks.id
    ]

    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "oms-api"
    container_port   = 8080
  }

  depends_on = [
    aws_lb_listener.http,
    aws_lb_listener.https
  ]

}