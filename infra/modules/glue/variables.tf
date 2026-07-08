variable "project" {
  type    = string
  default = "eip"
}
variable "env" {
  type    = string
  default = "dev"
}
variable "silver_bucket" {
  type = string
}
variable "bronze_arn" {
  type = string
}
variable "bronze_bucket" {
  type = string
}
variable "bronze_path" {
  type = string
}
variable "silver_arn" {
  type = string
}