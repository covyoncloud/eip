output "bronze_bucket" {
  value = aws_s3_bucket.bronze.id
}

output "silver_bucket" {
  value = aws_s3_bucket.silver.id
}

output "bronze_arn" {
  value = aws_s3_bucket.bronze.arn
}

output "silver_arn" {
  value = aws_s3_bucket.silver.arn
}

output "dedup_table_arn" {
  value = aws_dynamodb_table.dedup.arn
}

output "dedup_table_name" {
  value = aws_dynamodb_table.dedup.name
}