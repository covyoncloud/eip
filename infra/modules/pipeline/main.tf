locals {
  handlers = {
    parse   = "ingestion.steps.parse_normalize"
    quality = "ingestion.steps.quality_gate"
    load    = "ingestion.steps.load"
  }
}

resource "aws_iam_role" "lambda" {
  name = "${var.project}-${var.env}-pipeline-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_perms" {
  role = aws_iam_role.lambda.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:GetObject"], Resource = "${var.bronze_arn}/*" },
      { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject"], Resource = "${var.silver_arn}/*" },
      { Effect = "Allow", Action = ["dynamodb:GetItem", "dynamodb:PutItem"], Resource = var.dedup_table_arn }
    ]
  })
}

# 3 Lambdas, même image, CMD différent
resource "aws_lambda_function" "step" {
  for_each      = local.handlers
  function_name = "${var.project}-${var.env}-${each.key}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${var.lambda_ecr_url}:latest"
  timeout       = 120
  memory_size   = 512

  image_config {
    command = [each.value] # surcharge le CMD du Dockerfile
  }

  environment {
    variables = {
      DATABASE_URL  = var.database_url
      DEDUP_TABLE   = var.dedup_table_name
      SILVER_BUCKET = var.silver_bucket
    }
  }

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.app_security_group_id]
  }
}

# Rôle de la state machine
resource "aws_iam_role" "sfn" {
  name = "${var.project}-${var.env}-sfn"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole", Effect = "Allow"
      Principal = { Service = "states.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "sfn_invoke" {
  role = aws_iam_role.sfn.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["lambda:InvokeFunction"]
      Resource = [for f in aws_lambda_function.step : f.arn]
    }]
  })
}

# La state machine
resource "aws_sfn_state_machine" "pipeline" {
  name     = "${var.project}-${var.env}-pipeline"
  role_arn = aws_iam_role.sfn.arn

  definition = jsonencode({
    StartAt = "ParseNormalize"
    States = {
      ParseNormalize = {
        Type     = "Task"
        Resource = aws_lambda_function.step["parse"].arn
        Retry    = [{ ErrorEquals = ["States.TaskFailed"], IntervalSeconds = 2, MaxAttempts = 2, BackoffRate = 2.0 }]
        Next     = "QualityGate"
      }
      QualityGate = {
        Type     = "Task"
        Resource = aws_lambda_function.step["quality"].arn
        Next     = "IsValid"
      }
      IsValid = {
        Type    = "Choice"
        Choices = [{ Variable = "$.valid", BooleanEquals = true, Next = "Load" }]
        Default = "QualityFailed"
      }
      Load = {
        Type     = "Task"
        Resource = aws_lambda_function.step["load"].arn
        Retry    = [{ ErrorEquals = ["States.TaskFailed"], IntervalSeconds = 5, MaxAttempts = 3, BackoffRate = 2.0 }]
        End      = true
      }
      QualityFailed = {
        Type  = "Fail"
        Error = "QualityGateFailed"
        Cause = "Le ratio de données valides est sous le seuil"
      }
    }
  })
}