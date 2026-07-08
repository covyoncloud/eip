resource "aws_iam_role" "lambda" {
  name = "${var.project}-${var.env}-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole", Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# accès VPC (créer les ENI dans les subnets privés)
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# permissions applicatives : lire S3, consommer SQS
resource "aws_iam_role_policy" "lambda_perms" {
  role = aws_iam_role.lambda.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = var.queue_arn
      },
      {
        Effect   = "Allow"
        Action   = ["states:StartExecution"]
        Resource = var.state_machine_arn
      }
    ]
  })
}

resource "aws_lambda_function" "consumer" {
  function_name = "${var.project}-${var.env}-consumer"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${var.lambda_ecr_url}:latest"
  timeout       = 60
  memory_size   = 512

  environment {
    variables = {
      STATE_MACHINE_ARN = var.state_machine_arn
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = var.queue_arn
  function_name    = aws_lambda_function.consumer.arn
  batch_size       = 5

  function_response_types = ["ReportBatchItemFailures"]
}