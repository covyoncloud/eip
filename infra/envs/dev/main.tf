terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project = "EIP"
      Env     = "dev"
      Owner   = var.owner
    }
  }
}

resource "aws_security_group" "app" {
  name   = "eip-dev-app"
  vpc_id = module.network.vpc_id
}

resource "aws_ecr_repository" "lambda" {
  name = "eip-ingestion-lambda"
}

resource "aws_ecr_repository" "ingestion" {
  name                 = "eip-ingestion"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true # scan de vulnérabilités automatique
  }
}

output "ecr_url" {
  value = aws_ecr_repository.ingestion.repository_url
}

# le SG app doit pouvoir sortir (vers Aurora, ECR, etc.)
resource "aws_security_group_rule" "app_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.app.id
}

output "app_url" {
  value = module.compute.alb_url
}

resource "aws_security_group_rule" "app_from_alb" {
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = module.compute.alb_security_group_id
  security_group_id        = aws_security_group.app.id
}

output "messaging_queue_url" {
  value = module.messaging.queue_url
}

resource "aws_iam_role_policy" "consumer_start_sfn" {
  role = module.consumer.lambda_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["states:StartExecution"]
      Resource = module.pipeline.state_machine_arn
    }]
  })
}

module "compute" {
  source                = "../../modules/compute"
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  app_security_group_id = aws_security_group.app.id
  ecr_url               = aws_ecr_repository.ingestion.repository_url
  db_endpoint           = module.aurora.endpoint
  db_password           = module.aurora.db_password
  db_secret_arn         = module.aurora.secret_arn
  bronze_bucket         = module.storage.bronze_bucket
  bronze_arn            = module.storage.bronze_arn
}

# ---- Appels de modules (à décommenter au fil des sprints) ----
module "storage" {
  source = "../../modules/storage"
  suffix = var.suffix
}

module "network" {
  source = "../../modules/network"
  region = var.region
}

module "aurora" {
  source                = "../../modules/aurora"
  vpc_id                = module.network.vpc_id
  private_subnet_ids    = module.network.private_subnet_ids
  app_security_group_id = aws_security_group.app.id
}

module "messaging" {
  source        = "../../modules/messaging"
  bronze_bucket = module.storage.bronze_bucket
  bronze_arn    = module.storage.bronze_arn
}

module "consumer" {
  source            = "../../modules/consumer"
  lambda_ecr_url    = aws_ecr_repository.lambda.repository_url
  queue_arn         = module.messaging.queue_arn
  state_machine_arn = module.pipeline.state_machine_arn
}

module "pipeline" {
  source                = "../../modules/pipeline"
  lambda_ecr_url        = aws_ecr_repository.lambda.repository_url
  silver_arn            = module.storage.silver_arn
  bronze_arn            = module.storage.bronze_arn
  silver_bucket         = module.storage.silver_bucket
  dedup_table_arn       = module.storage.dedup_table_arn
  dedup_table_name      = module.storage.dedup_table_name
  private_subnet_ids    = module.network.private_subnet_ids
  app_security_group_id = aws_security_group.app.id
  database_url          = "postgresql+psycopg://eip:${module.aurora.db_password}@${module.aurora.endpoint}:5432/eip"
}
