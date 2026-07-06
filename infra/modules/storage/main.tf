# Module storage — TODO
# variables.tf / outputs.tf / main.tf à remplir au sprint correspondant.
# Buckets du data lake : bronze (brut) et silver (normalisé)

resource "aws_s3_bucket" "bronze" {
  bucket = "${var.project}-bronze-${var.suffix}"
}

resource "aws_s3_bucket" "silver" {
  bucket = "${var.project}-silver-${var.suffix}"
}

# Versioning : garde l'historique des objets (protection contre écrasement)
resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_versioning" "silver" {
  bucket = aws_s3_bucket.silver.id
  versioning_configuration { status = "Enabled" }
}

# Chiffrement au repos (SSE-S3, gratuit)
resource "aws_s3_bucket_server_side_encryption_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver" {
  bucket = aws_s3_bucket.silver.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Bloquer tout accès public (bonne pratique sécurité par défaut)
resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket                  = aws_s3_bucket.bronze.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "silver" {
  bucket                  = aws_s3_bucket.silver.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}