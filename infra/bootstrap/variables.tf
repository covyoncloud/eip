variable "region" {
  type    = string
  default = "eu-west-3"
}
variable "state_bucket_name" {
  type        = string
  description = "Nom GLOBALEMENT unique. Ex: eip-tfstate-<toninitiales>-<random>"
}
variable "lock_table_name" {
  type    = string
  default = "eip-tflock"
}
