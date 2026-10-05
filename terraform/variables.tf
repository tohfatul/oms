variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "oms"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "max_receive_count" {
  description = "Number of failed receives before sending message to DLQ"
  type        = number
  default     = 3
}

variable "message_retention_seconds" {
  description = "Retention period for normal queues"
  type        = number
  default     = 345600
}

variable "dlq_message_retention_seconds" {
  description = "Retention period for dead-letter queues"
  type        = number
  default     = 1209600
}

variable "vpc_cidr" {
  description = "CIDR block for the OMS VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_1_cidr" {
  description = "CIDR for public subnet 1"
  type        = string
  default     = "10.20.1.0/24"
}

variable "public_subnet_2_cidr" {
  description = "CIDR for public subnet 2"
  type        = string
  default     = "10.20.2.0/24"
}

variable "db_subnet_1_cidr" {
  description = "CIDR for database subnet 1"
  type        = string
  default     = "10.20.11.0/24"
}

variable "db_subnet_2_cidr" {
  description = "CIDR for database subnet 2"
  type        = string
  default     = "10.20.12.0/24"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "orderdb"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "omsadmin"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "api_domain_name" {
  description = "Public DNS name for the OMS API"
  type        = string
  default     = "api.digizerones.com"
}