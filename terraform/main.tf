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
  region = "us-east-2"
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

# Security Group
resource "aws_security_group" "dream_demo" {
  name_prefix = "dream-demo-${var.sprint}-"
  description = "Security group for Dream Demo ${var.sprint}"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
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

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name   = "dream-demo-${var.sprint}-sg"
    Sprint = var.sprint
  }
  # In terraform/main.tf, add these ingress rules:

  ingress {
    from_port   = 7233
    to_port     = 7233
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Temporal gRPC"
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Temporal UI"
  }

  ingress {
    from_port   = 5433
    to_port     = 5433
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Temporal Postgres"
  }
}

# EC2 Instance
resource "aws_instance" "dream_demo" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name
  
  vpc_security_group_ids = [aws_security_group.dream_demo.id]
  
  user_data = templatefile("${path.module}/user_data.sh", {
    sprint = var.sprint
  })
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name   = "dream-demo-${var.sprint}"
    Sprint = var.sprint
  }
}

# Elastic IP
resource "aws_eip" "dream_demo" {
  instance = aws_instance.dream_demo.id
  domain   = "vpc"

  tags = {
    Name   = "dream-demo-${var.sprint}-eip"
    Sprint = var.sprint
  }
}

# Wait for instance to be ready
resource "null_resource" "wait_for_instance" {
  depends_on = [aws_eip.dream_demo]
  
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      "docker --version",
      "docker-compose --version"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/${var.key_name}.pem")
      host        = aws_eip.dream_demo.public_ip
    }
  }
}
