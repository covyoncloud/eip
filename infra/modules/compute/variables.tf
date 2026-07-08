variable "project" {
  type    = string
  default = "eip"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "eu-west-3"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "app_security_group_id" {
  type = string
}

variable "ecr_url" {
  type = string
}

variable "db_endpoint" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_secret_arn" {
  type = string
}

variable "bronze_arn" {
  type = string
}

variable "bronze_bucket" {
  type = string
}