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

# ---- Appels de modules (à décommenter au fil des sprints) ----

# module "network" {
#   source = "../../modules/network"
#   ...
# }

# module "storage" {
#   source = "../../modules/storage"
#   ...   # S3 bronze/silver/gold, Aurora, DynamoDB
# }

# module "compute" {
#   source = "../../modules/compute"
#   ...   # ECR, ECS Fargate, ALB
# }
