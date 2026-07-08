variable "project" {
  type    = string
  default = "eip"
}
variable "env" {
  type    = string
  default = "dev"
}
variable "lambda_ecr_url" {
  type = string
}
variable "database_url" {
  type = string
}
variable "dedup_table_arn" {
  type = string
}
variable "dedup_table_name" {
  type = string
}
variable "silver_bucket" {
  type = string
}
variable "private_subnet_ids" {
  type = list(string)
}
variable "app_security_group_id" {
  type = string
}
variable "bronze_arn" {
  type = string
}
variable "silver_arn" {
  type = string
}