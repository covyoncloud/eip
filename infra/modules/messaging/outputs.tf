output "queue_url" {
  value = aws_sqs_queue.ingest.url
}
output "queue_arn" {
  value = aws_sqs_queue.ingest.arn
}
output "dlq_url" {
  value = aws_sqs_queue.ingest_dlq.url
}