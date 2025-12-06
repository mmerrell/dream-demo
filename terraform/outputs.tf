output "sprint_urls" {
  description = "URLs for each deployed sprint"
  value = {
    for sprint in var.sprints_to_deploy : sprint => "http://${sprint}.${var.domain_name}"
  }
}

output "instance_ips" {
  description = "Public IP addresses for each sprint instance"
  value = {
    for sprint in var.sprints_to_deploy : sprint => aws_instance.dream_demo[sprint].public_ip
  }
}

output "instance_ids" {
  description = "IDs of the EC2 instances"
  value = {
    for sprint in var.sprints_to_deploy : sprint => aws_instance.dream_demo[sprint].id
  }
}

output "security_group_id" {
  description = "ID of the security group"
  value = aws_security_group.dream_demo.id
}

output "ssh_commands" {
  description = "SSH commands to connect to each instance"
  value = {
    for sprint in var.sprints_to_deploy : sprint => "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.dream_demo[sprint].public_ip}"  }
  }

output "direct_urls" {
  description = "Direct IP-based URLs for troubleshooting"
  value = {
    for sprint in var.sprints_to_deploy : sprint => {
      frontend = "http://${aws_instance.dream_demo[sprint].public_ip}:3000"
      backend  = "http://${aws_instance.dream_demo[sprint].public_ip}:8000"
      temporal = "http://${aws_instance.dream_demo[sprint].public_ip}:8080"
    }
  }
}

# Legacy outputs for backward compatibility
output "instance_ip" {
  description = "Public IP address of the first instance (legacy)"
  value = length(var.sprints_to_deploy) > 0 ? aws_instance.dream_demo[var.sprints_to_deploy[0]].public_ip : null
}

output "frontend_url" {
  description = "Frontend URL for first sprint (legacy)"
  value = length(var.sprints_to_deploy) > 0 ? "http://${var.sprints_to_deploy[0]}.${var.domain_name}" : null
}

output "backend_url" {
  description = "Backend URL for first sprint (legacy)"
  value = length(var.sprints_to_deploy) > 0 ? "http://${var.sprints_to_deploy[0]}.${var.domain_name}/api" : null
}