variable "github_repo" {
  description = "GitHub repo allowed to assume the OIDC role, format: owner/repo"
  type        = string
  default     = "Hirva-Desai-A/Secure-Kube"
}

variable "aws_region" {
  description = "AWS region for ECR/S3/DynamoDB"
  type        = string
  default     = "ap-south-1"
}
