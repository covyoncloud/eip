# Module network — TODO
# variables.tf / outputs.tf / main.tf à remplir au sprint correspondant.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-${var.env}"
  cidr = "10.0.0.0/16"

  # 2 zones de disponibilité (requis par Aurora)
  azs             = ["${var.region}a", "${var.region}b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]

  # Pas de NAT Gateway : elle coûte ~32€/mois. On s'en passe pour le lab.
  enable_nat_gateway = false

  # DNS interne (nécessaire pour Aurora et les endpoints)
  enable_dns_hostnames = true
  enable_dns_support   = true
}