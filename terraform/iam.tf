//ecs trust policy

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

// ecs task execution role

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project_name}-${var.environment}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

// api task role

resource "aws_iam_role" "api_task" {
  name               = "${var.project_name}-${var.environment}-api-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "api_task" {
  statement {
    sid    = "PublishOrderEvents"
    effect = "Allow"

    actions = [
      "sns:Publish"
    ]

    resources = [
      aws_sns_topic.order_created.arn
    ]
  }
}

resource "aws_iam_role_policy" "api_task" {
  name   = "${var.project_name}-${var.environment}-api-policy"
  role   = aws_iam_role.api_task.id
  policy = data.aws_iam_policy_document.api_task.json
}


// erp worjer task role

resource "aws_iam_role" "erp_worker_task" {
  name               = "${var.project_name}-${var.environment}-erp-worker-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "erp_worker_task" {
  statement {
    sid    = "ConsumeERPQueue"
    effect = "Allow"

    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ChangeMessageVisibility"
    ]

    resources = [
      aws_sqs_queue.erp_queue.arn
    ]
  }
}

resource "aws_iam_role_policy" "erp_worker_task" {
  name   = "${var.project_name}-${var.environment}-erp-worker-policy"
  role   = aws_iam_role.erp_worker_task.id
  policy = data.aws_iam_policy_document.erp_worker_task.json
}

//notification worker task role

resource "aws_iam_role" "notification_worker_task" {
  name               = "${var.project_name}-${var.environment}-notification-worker-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "notification_worker_task" {
  statement {
    sid    = "ConsumeNotificationQueue"
    effect = "Allow"

    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ChangeMessageVisibility"
    ]

    resources = [
      aws_sqs_queue.notification_queue.arn
    ]
  }
}

resource "aws_iam_role_policy" "notification_worker_task" {
  name   = "${var.project_name}-${var.environment}-notification-worker-policy"
  role   = aws_iam_role.notification_worker_task.id
  policy = data.aws_iam_policy_document.notification_worker_task.json
}

// let ecs retrieve the database secret

data "aws_iam_policy_document" "ecs_execution_secrets" {
  statement {
    sid    = "ReadRdsSecret"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue"
    ]

    resources = [
      aws_db_instance.postgres.master_user_secret[0].secret_arn
    ]
  }
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name   = "${var.project_name}-${var.environment}-ecs-secrets-policy"
  role   = aws_iam_role.ecs_execution.id
  policy = data.aws_iam_policy_document.ecs_execution_secrets.json
}


// ai task role

resource "aws_iam_role" "ai_task" {
  name = "${var.project_name}-${var.environment}-ai-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}


data "aws_iam_policy_document" "ai_task" {
  statement {
    sid = "InvokeBedrock"

    actions = [
      "bedrock:InvokeModel"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role_policy" "ai_task" {
  name   = "${var.project_name}-${var.environment}-ai-task-policy"
  role   = aws_iam_role.ai_task.id
  policy = data.aws_iam_policy_document.ai_task.json
}