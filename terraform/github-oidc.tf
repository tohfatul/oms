resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}


data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repository}@${var.github_repository_id}:ref:refs/heads/${var.github_branch}"
      ]
    }
  }
}


resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-${var.environment}-github-actions"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
}


data "aws_iam_policy_document" "github_actions" {

  statement {
    sid    = "EcrAuthorization"
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "PushImagesToEcr"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage"
    ]

    resources = [
      aws_ecr_repository.api.arn,
      aws_ecr_repository.erp_worker.arn,
      aws_ecr_repository.notification_worker.arn
    ]
  }

  statement {
    sid    = "TaskDefinitionsAndMigrations"
    effect = "Allow"

    actions = [
      "ecs:RegisterTaskDefinition",
      "ecs:DescribeTaskDefinition",
      "ecs:RunTask",
      "ecs:DescribeTasks"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "UpdateOmsServices"
    effect = "Allow"

    actions = [
      "ecs:UpdateService",
      "ecs:DescribeServices"
    ]

    resources = [
      aws_ecs_service.api.id,
      aws_ecs_service.erp_worker.id,
      aws_ecs_service.notification_worker.id
    ]
  }

  statement {
    sid    = "PassEcsTaskRoles"
    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      aws_iam_role.ecs_execution.arn,
      aws_iam_role.api_task.arn,
      aws_iam_role.erp_worker_task.arn,
      aws_iam_role.notification_worker_task.arn
    ]
  }
}


resource "aws_iam_role_policy" "github_actions" {
  name = "${var.project_name}-${var.environment}-github-actions-policy"

  role = aws_iam_role.github_actions.id

  policy = data.aws_iam_policy_document.github_actions.json
}