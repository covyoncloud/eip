# Configure le backend remote (rempli APRÈS le bootstrap).
terraform {
  backend "s3" {
    bucket         = "eip-tfstate-CHANGE-ME-123" # <-- reporte ici le bucket du bootstrap
    key            = "dev/terraform.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "eip-tflock"
    encrypt        = true
  }
}
