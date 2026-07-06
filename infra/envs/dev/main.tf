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

module "compute" {
  source                = "../../modules/compute"
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  app_security_group_id = aws_security_group.app.id
  ecr_url               = aws_ecr_repository.ingestion.repository_url
  db_endpoint           = module.aurora.endpoint
  db_password           = module.aurora.db_password
  db_secret_arn         = module.aurora.secret_arn
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
