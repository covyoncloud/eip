# Configure le backend remote (rempli APRÈS le bootstrap).
terraform {
  backend "s3" {
    bucket       = "eip-tfstate-covyoncloud-4271" # <-- reporte ici le bucket du bootstrap
    key          = "dev/terraform.tfstate"
    region       = "eu-west-3"
    use_lockfile = true
    encrypt      = true
  }
}
