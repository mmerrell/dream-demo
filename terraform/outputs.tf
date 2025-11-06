output "instance_ip" {
  description = "Public IP address of the instance"
  value       = aws_eip.dream_demo.public_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.dream_demo.id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.dream_demo.id
}

output "frontend_url" {
  description = "Frontend URL"
  value       = "http://${aws_eip.dream_demo.public_ip}:3000"
}

output "backend_url" {
  description = "Backend URL"  
  value       = "http://${aws_eip.dream_demo.public_ip}:8000"
}
