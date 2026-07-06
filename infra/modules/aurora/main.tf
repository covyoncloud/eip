# Mot de passe généré aléatoirement, stocké dans Secrets Manager
resource "random_password" "db" {
  length  = 20
  special = false
}

resource "aws_secretsmanager_secret" "db" {
  name = "${var.project}-${var.env}-db-password"
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = random_password.db.result
}

# Groupe de subnets : Aurora doit vivre dans les subnets privés, sur 2 AZ
resource "aws_db_subnet_group" "this" {
  name       = "${var.project}-${var.env}"
  subnet_ids = var.private_subnet_ids
}

# Security group : qui a le droit de parler à la base
resource "aws_security_group" "db" {
  name   = "${var.project}-${var.env}-db"
  vpc_id = var.vpc_id

  # entrée :5432 autorisée uniquement depuis le SG de l'app (Fargate)
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }
}

# Le cluster Aurora PostgreSQL Serverless v2
resource "aws_rds_cluster" "this" {
  cluster_identifier = "${var.project}-${var.env}"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned" # requis pour Serverless v2
  engine_version     = "16.4"
  database_name      = "eip"
  master_username    = "eip"
  master_password    = random_password.db.result

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
  skip_final_snapshot    = true # lab : pas de snapshot à la destruction

  serverlessv2_scaling_configuration {
    min_capacity = 0 # scale à zéro quand inactif (coût mini)
    max_capacity = 1 # plafond bas pour le lab
  }
}

resource "aws_rds_cluster_instance" "this" {
  cluster_identifier = aws_rds_cluster.this.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.this.engine
  engine_version     = aws_rds_cluster.this.engine_version
}