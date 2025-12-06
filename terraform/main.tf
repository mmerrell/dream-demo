terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: Use S3 backend for state storage
#   backend "s3" {
#     bucket = "your-terraform-state-bucket"
#     key    = "dream-demo/terraform.tfstate"
#     region = "us-east-2"
#   }
}

provider "aws" {
  region = var.aws_region
}

# Data source for latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Data source for hosted zone
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

# Security Group (shared across all sprint instances)
resource "aws_security_group" "dream_demo" {
  name_prefix = "dream-demo-"
  description = "Security group for Dream Demo instances"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Frontend"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Backend"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Temporal gRPC"
    from_port   = 7233
    to_port     = 7233
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Temporal UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "dream-demo-sg"
    Project = "DreamDemo"
  }
}

# EC2 Instances for each sprint
resource "aws_instance" "dream_demo" {
  for_each = toset(var.sprints_to_deploy)

  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.dream_demo.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    sprint_name     = each.key
    docker_registry = var.docker_registry
    domain_name     = "${each.key}.${var.domain_name}"
    stripe_secret_key      = var.stripe_secret_key
    stripe_publishable_key = var.stripe_publishable_key
  })

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name    = "dream-demo-${each.key}"
    Sprint  = each.key
    Project = "DreamDemo"
  }
}

# Route 53 A records for each sprint
resource "aws_route53_record" "sprint_records" {
  for_each = toset(var.sprints_to_deploy)

  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${each.key}.${var.domain_name}"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.dream_demo[each.key].public_ip]  # <-- CHANGED
}

# Wait for instances to be ready
# resource "null_resource" "wait_for_instances" {
#   for_each = toset(var.sprints_to_deploy)
#
#   depends_on = [aws_eip.dream_demo]
#
#   provisioner "remote-exec" {
#     inline = [
#       "cloud-init status --wait",
#       "docker --version",
#       "docker-compose --version"
#     ]
#
#     connection {
#       type        = "ssh"
#       user        = "ec2-user"
#       private_key = file("~/.ssh/${var.key_name}.pem")
#       host        = aws_eip.dream_demo[each.key].public_ip
#     }
#   }
# }