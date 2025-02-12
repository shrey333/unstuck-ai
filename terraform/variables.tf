variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "unstuck-ai"
}

variable "environment" {
  description = "Environment (prod, dev, etc)"
  type        = string
  default     = "prod"
}

variable "lambda_package_path" {
  description = "Path to the Lambda package zip file"
  type        = string
  default     = "../backend/package/lambda.zip"
}
