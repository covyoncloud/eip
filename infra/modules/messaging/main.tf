# File principale
resource "aws_sqs_queue" "ingest" {
  name                       = "${var.project}-${var.env}-ingest"
  visibility_timeout_seconds = 300
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ingest_dlq.arn
    maxReceiveCount     = 3
  })
}

# Dead Letter Queue
resource "aws_sqs_queue" "ingest_dlq" {
  name = "${var.project}-${var.env}-ingest-dlq"
}

# Autoriser S3 à écrire dans la file
resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.ingest.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "s3.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.ingest.arn
      Condition = { ArnEquals = { "aws:SourceArn" = var.bronze_arn } }
    }]
  })
}

# Notification S3 -> SQS
resource "aws_s3_bucket_notification" "bronze" {
  bucket = var.bronze_bucket

  queue {
    queue_arn     = aws_sqs_queue.ingest.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "uploads/"
  }

  depends_on = [aws_sqs_queue_policy.allow_s3]
}