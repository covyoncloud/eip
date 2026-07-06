# Module compute — TODO
# variables.tf / outputs.tf / main.tf à remplir au sprint correspondant.
# ---- Cluster ECS : le "groupe" où tournent tes conteneurs ----
resource "aws_ecs_cluster" "this" {
  name = "${var.project}-${var.env}"
}

# ---- Rôle IAM : permissions que Fargate a besoin (tirer l'image, lire le secret) ----
resource "aws_iam_role" "execution" {
  name = "${var.project}-${var.env}-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# autorise la lecture du secret DB
resource "aws_iam_role_policy" "read_secret" {
  role = aws_iam_role.execution.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = var.db_secret_arn
    }]
  })
}

# ---- Définition de la tâche : QUEL conteneur, avec quelles ressources ----
resource "aws_ecs_task_definition" "this" {
  family                   = "${var.project}-${var.env}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.execution.arn

  container_definitions = jsonencode([{
    name         = "ingestion"
    image        = "${var.ecr_url}:latest"
    essential    = true
    portMappings = [{ containerPort = 8080 }]
    environment = [
      { name = "DATABASE_URL", value = "postgresql+psycopg://eip:${var.db_password}@${var.db_endpoint}:5432/eip" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.this.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "ingestion"
      }
    }
  }])
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/ecs/${var.project}-${var.env}"
  retention_in_days = 7
}

# ---- Load Balancer : la porte publique vers ton app ----
resource "aws_lb" "this" {
  name               = "${var.project}-${var.env}"
  load_balancer_type = "application"
  subnets            = var.public_subnet_ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "this" {
  name        = "${var.project}-${var.env}"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check { path = "/health" }
}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

# ---- Security group de l'ALB : accepte le trafic internet sur :80 ----
resource "aws_security_group" "alb" {
  name   = "${var.project}-${var.env}-alb"
  vpc_id = var.vpc_id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---- Le service ECS : maintient ton conteneur en vie, derrière l'ALB ----
resource "aws_ecs_service" "this" {
  name            = "${var.project}-${var.env}"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.public_subnet_ids
    security_groups  = [var.app_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = "ingestion"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.this]
}