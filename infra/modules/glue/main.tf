resource "aws_iam_role" "glue" {
  name = "${var.project}-${var.env}-glue"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3" {
  role = aws_iam_role.glue.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
      Resource = [
        var.bronze_arn, "${var.bronze_arn}/*",
        var.silver_arn, "${var.silver_arn}/*",
      ]
    }]
  })
}

resource "aws_glue_job" "normalize" {
  name              = "${var.project}-${var.env}-normalize"
  role_arn          = aws_iam_role.glue.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2  # minimum absolu
  timeout           = 15 # minutes : coupe-circuit anti-facture

  command {
    script_location = "s3://${var.bronze_bucket}/scripts/normalize_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--bronze_path"    = var.bronze_path
    "--silver_path"    = "s3://${var.silver_bucket}/works_parquet/"
    "--TempDir"        = "s3://${var.silver_bucket}/glue-temp/"
    "--enable-metrics" = "true"
    "--job-language"   = "python"
  }
}