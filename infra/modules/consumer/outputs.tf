output "function_name" {
  value = aws_lambda_function.consumer.function_name
}
output "lambda_role_arn" {
  value = aws_iam_role.lambda.arn
}
output "lambda_role_name" {
  value = aws_iam_role.lambda.name
}