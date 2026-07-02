resource "aws_ecr_repository" "securekube_api" {
  name                 = "securekube-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "securekube_api" {
  repository = aws_ecr_repository.securekube_api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the most recent image"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 1
        }
        action = { type = "expire" }
      }
    ]
  })
}
