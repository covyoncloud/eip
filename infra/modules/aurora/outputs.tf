output "endpoint" {
  value = aws_rds_cluster.this.endpoint
}
output "secret_arn" {
  value = aws_secretsmanager_secret.db.arn
}
output "db_security_group_id" {
  value = aws_security_group.db.id
}
output "db_password" {
  value     = random_password.db.result
  sensitive = true
}