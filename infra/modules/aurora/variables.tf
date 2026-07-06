variable "project" {
  type    = string
  default = "eip"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "app_security_group_id" {
  type        = string
  description = "SG de Fargate, autorisé à joindre la base"
}