variable "domain_name" {
  description = "Base domain name"
  type        = string
  default     = "dreamdemo.xyz"
}

variable "sprints_to_deploy" {
  description = "List of sprints to deploy"
  type        = list(string)
  default     = ["sprint-1", "sprint-2", "sprint-3"]
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"  # Keeping your existing region
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.large"
}

variable "key_name" {
  description = "AWS key pair name"
  type        = string
  default     = "mmerrell-sauce"
}

variable "docker_registry" {
  description = "Docker registry prefix"
  type        = string
  default     = "mmerrell"
}

# Legacy variables for backward compatibility
variable "sprint" {
  description = "Sprint name (deprecated - use sprints_to_deploy)"
  type        = string
  default     = "sprint-1"
}

variable "stripe_secret_key" {
  description = "Stripe secret key for backend"
  type        = string
  sensitive   = true
}

variable "stripe_publishable_key" {
  description = "Stripe publishable key for frontend"
  type        = string
}