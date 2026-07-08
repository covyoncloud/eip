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
variable "queue_arn" {
  type = string
}
variable "state_machine_arn" {
  type = string
}