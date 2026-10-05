resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}-${var.environment}-api"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "erp_worker" {
  name              = "/ecs/${var.project_name}-${var.environment}-erp-worker"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "notification_worker" {
  name              = "/ecs/${var.project_name}-${var.environment}-notification-worker"
  retention_in_days = 7
}