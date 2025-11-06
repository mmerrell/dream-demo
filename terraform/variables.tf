variable "sprint" {
  description = "Sprint name (sprint-1, sprint-2, etc.)"
  type        = string
  default     = "sprint-2"
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
