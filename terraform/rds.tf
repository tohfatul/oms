// rds subnet group

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-${var.environment}-db-subnet-group"

  subnet_ids = [
    aws_subnet.db_1.id,
    aws_subnet.db_2.id
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

// rds security group

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds"
  description = "Allow PostgreSQL access from OMS ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "PostgreSQL from ECS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"

    security_groups = [
      aws_security_group.ecs_tasks.id
    ]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds"
  }
}

// create the postgres rds instance

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  engine = "postgres"

  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 50
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  port     = 5432

  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.main.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 1

  deletion_protection = false
  skip_final_snapshot = true

  apply_immediately = true

  tags = {
    Name = "${var.project_name}-${var.environment}-postgres"
  }
}