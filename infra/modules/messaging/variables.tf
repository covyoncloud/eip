variable "project" {
  type    = string
  default = "eip"
}
variable "env" {
  type    = string
  default = "dev"
}
variable "bronze_bucket" {
  type        = string
  description = "Nom du bucket bronze (pour la notification)"
}
variable "bronze_arn" {
  type        = string
  description = "ARN du bucket bronze (pour la condition de la policy)"
}