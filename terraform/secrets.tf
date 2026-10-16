data "aws_secretsmanager_secret" "openai_api_key" {
  name = "oms/dev/openai-api-key"
}