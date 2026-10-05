resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb"
  description = "Allow HTTP traffic to OMS ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

// add a rule allowing the alb to reach ecs tasks on port 8080

resource "aws_security_group_rule" "ecs_from_alb" {
  type = "ingress"

  from_port = 8080
  to_port   = 8080
  protocol  = "tcp"

  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.alb.id

  description = "Allow ALB to reach OMS API"
}

// create the load balancer

resource "aws_lb" "api" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb.id
  ]

  subnets = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}


// create the api target group

resource "aws_lb_target_group" "api" {
  name        = "${var.project_name}-${var.environment}-api-tg"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"

  vpc_id = aws_vpc.main.id

  health_check {
    enabled = true

    path     = "/health/ready"
    protocol = "HTTP"

    port = "traffic-port"

    healthy_threshold   = 2
    unhealthy_threshold = 3

    interval = 30
    timeout  = 5

    matcher = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api-tg"
  }
}

// create the alb listener

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.api.arn

  port     = 80
  protocol = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}


resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.api.arn

  port     = 443
  protocol = "HTTPS"

  certificate_arn = aws_acm_certificate.api.arn

  ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}