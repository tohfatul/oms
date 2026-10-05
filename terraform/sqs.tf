resource "aws_sqs_queue" "erp_dlq" {
  name = "${var.project_name}-${var.environment}-order-erp-dlq"

  message_retention_seconds = var.dlq_message_retention_seconds

  sqs_managed_sse_enabled = true
}


resource "aws_sqs_queue" "notification_dlq" {
  name = "${var.project_name}-${var.environment}-order-notification-dlq"

  message_retention_seconds = var.dlq_message_retention_seconds

  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "erp_queue" {
  name = "${var.project_name}-${var.environment}-order-erp-queue"

  visibility_timeout_seconds = 30

  message_retention_seconds = var.message_retention_seconds

  receive_wait_time_seconds = 20

  sqs_managed_sse_enabled = true
}


resource "aws_sqs_queue" "notification_queue" {
  name = "${var.project_name}-${var.environment}-order-notification-queue"

  visibility_timeout_seconds = 30

  message_retention_seconds = var.message_retention_seconds

  receive_wait_time_seconds = 20

  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue_redrive_policy" "erp" {
  queue_url = aws_sqs_queue.erp_queue.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.erp_dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}


resource "aws_sqs_queue_redrive_policy" "notification" {
  queue_url = aws_sqs_queue.notification_queue.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notification_dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}

resource "aws_sqs_queue_redrive_allow_policy" "erp_dlq" {
  queue_url = aws_sqs_queue.erp_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns = [
      aws_sqs_queue.erp_queue.arn
    ]
  })
}


resource "aws_sqs_queue_redrive_allow_policy" "notification_dlq" {
  queue_url = aws_sqs_queue.notification_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns = [
      aws_sqs_queue.notification_queue.arn
    ]
  })
}

data "aws_iam_policy_document" "erp_queue_policy" {

  statement {
    sid    = "AllowSNSToSendMessage"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.erp_queue.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        aws_sns_topic.order_created.arn
      ]
    }
  }
}


resource "aws_sqs_queue_policy" "erp" {
  queue_url = aws_sqs_queue.erp_queue.id

  policy = data.aws_iam_policy_document.erp_queue_policy.json
}

resource "aws_sns_topic_subscription" "erp" {
  topic_arn = aws_sns_topic.order_created.arn

  protocol = "sqs"

  endpoint = aws_sqs_queue.erp_queue.arn

  raw_message_delivery = true
}


resource "aws_sns_topic_subscription" "notification" {
  topic_arn = aws_sns_topic.order_created.arn

  protocol = "sqs"

  endpoint = aws_sqs_queue.notification_queue.arn

  raw_message_delivery = true
}

data "aws_iam_policy_document" "notification_queue_policy" {

  statement {
    sid    = "AllowSNSToSendMessage"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.notification_queue.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        aws_sns_topic.order_created.arn
      ]
    }
  }
}


resource "aws_sqs_queue_policy" "notification" {
  queue_url = aws_sqs_queue.notification_queue.id

  policy = data.aws_iam_policy_document.notification_queue_policy.json
}