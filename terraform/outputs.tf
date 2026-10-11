output "order_created_topic_arn" {
  description = "OrderCreated SNS topic ARN"
  value       = aws_sns_topic.order_created.arn
}


output "erp_queue_url" {
  description = "ERP SQS queue URL"
  value       = aws_sqs_queue.erp_queue.id
}


output "erp_queue_arn" {
  description = "ERP SQS queue ARN"
  value       = aws_sqs_queue.erp_queue.arn
}


output "notification_queue_url" {
  description = "Notification SQS queue URL"
  value       = aws_sqs_queue.notification_queue.id
}


output "notification_queue_arn" {
  description = "Notification SQS queue ARN"
  value       = aws_sqs_queue.notification_queue.arn
}


output "erp_dlq_url" {
  description = "ERP DLQ URL"
  value       = aws_sqs_queue.erp_dlq.id
}


output "notification_dlq_url" {
  description = "Notification DLQ URL"
  value       = aws_sqs_queue.notification_dlq.id
}

output "api_ecr_repository_url" {
  description = "API ECR repository URL"
  value       = aws_ecr_repository.api.repository_url
}

output "erp_worker_ecr_repository_url" {
  description = "ERP Worker ECR repository URL"
  value       = aws_ecr_repository.erp_worker.repository_url
}

output "notification_worker_ecr_repository_url" {
  description = "Notification Worker ECR repository URL"
  value       = aws_ecr_repository.notification_worker.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "api_ecs_service_name" {
  value = aws_ecs_service.api.name
}

output "erp_worker_ecs_service_name" {
  value = aws_ecs_service.erp_worker.name
}

output "notification_worker_ecs_service_name" {
  value = aws_ecs_service.notification_worker.name
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id
  ]
}

// rds outputs
output "rds_endpoint" {
  description = "PostgreSQL RDS endpoint"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "PostgreSQL RDS port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "PostgreSQL database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_master_secret_arn" {
  description = "Secrets Manager ARN containing RDS credentials"
  value       = aws_db_instance.postgres.master_user_secret[0].secret_arn
}

output "alb_dns_name" {
  description = "Public DNS name of the OMS API load balancer"
  value       = aws_lb.api.dns_name
}

output "api_url" {
  description = "Public HTTPS URL of the OMS API"
  value       = "https://${var.api_domain_name}"
}

output "api_certificate_arn" {
  description = "ACM certificate ARN for the OMS API"
  value       = aws_acm_certificate.api.arn
}

output "api_certificate_validation_records" {
  description = "DNS records required to validate the ACM certificate"

  value = {
    for option in aws_acm_certificate.api.domain_validation_options :
    option.domain_name => {
      name  = option.resource_record_name
      type  = option.resource_record_type
      value = option.resource_record_value
    }
  }
}

output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions through OIDC"
  value       = aws_iam_role.github_actions.arn
}