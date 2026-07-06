variable "region" {
  type    = string
  default = "eu-west-3"
}
variable "owner" {
  type    = string
  default = "covyoncloud"
}

variable "suffix" {
  type        = string
  description = "Suffixe unique pour les noms de bucket"
}
