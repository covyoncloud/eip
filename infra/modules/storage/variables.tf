variable "project" {
  type    = string
  default = "eip"
}

variable "suffix" {
  type        = string
  description = "Suffixe unique (les noms de bucket S3 sont GLOBALEMENT uniques)"
}