resource "aws_sns_topic" "order_created" {
  name = "${var.project_name}-${var.environment}-order-created"
}