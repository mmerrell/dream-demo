# DreamDemo Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- AWS CLI configured with appropriate permissions
- Terraform installed (for AWS deployment)
- Git repository access
- Stripe API keys (optional for payment features)

## Environment Variables Setup

Create a `.env` file in your project root:

```bash
# Stripe Configuration (optional)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

---

## A) Local Deployment

### Step 1: Choose Your Sprint Branch
```bash
# Switch to the sprint you want to deploy
git checkout sprint-1    # or sprint-2, sprint-3, etc.
```

### Step 2: Verify Environment Configuration
Ensure your `docker-compose.yml` has the correct sprint version:

```yaml
# In docker-compose.yml, frontend service should have:
environment:
  REACT_APP_SPRINT_VERSION: sprint-1  # Match your current branch
```

### Step 3: Start the Database
```bash
# Remove any existing database data (if needed)
docker-compose down -v
docker volume rm dream-demo_postgres_data 2>/dev/null || true

# Start all services
docker-compose up --build
```

### Step 4: Verify Local Deployment
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend docs: http://localhost:8000/docs
- Database: localhost:5432

### Step 5: Seed Database (Optional)
```bash
# In another terminal, seed the database with sample data
docker-compose exec backend python /app/scripts/seed_database.py
```

### Troubleshooting Local Deployment
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Restart specific service
docker-compose restart backend

# Clean restart
docker-compose down
docker-compose up --build
```

---

## B) AWS Deployment

### Step 1: Setup Infrastructure (Main Branch)
```bash
# Switch to main branch for infrastructure management
git checkout main

# Navigate to terraform directory
cd terraform

# Initialize terraform (first time only)
terraform init

# Configure your deployment
# Edit terraform.tfvars or create it:
cat > terraform.tfvars << EOF
sprint = "sprint-2"
key_name = "your-aws-key-pair-name"
docker_registry = "your-dockerhub-username"
EOF
```

### Step 2: Build and Push Docker Images
```bash
# Switch to the sprint branch you want to deploy
git checkout sprint-2  # or your target sprint

# Build images with sprint tags
docker build -t your-username/dream-demo-frontend:sprint-2 ./frontend-web
docker build -t your-username/dream-demo-backend:sprint-2 ./backend

# Push to Docker Hub
docker push your-username/dream-demo-frontend:sprint-2
docker push your-username/dream-demo-backend:sprint-2
```

### Step 3: Deploy Infrastructure
```bash
# Switch back to main branch
git checkout main
cd terraform

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
# Type 'yes' when prompted

# Get the public IP
terraform output instance_public_ip
```

### Step 4: Manual Deployment to EC2 (Alternative)
If you prefer manual deployment to existing EC2:

```bash
# Switch to your sprint branch
git checkout sprint-2

# Run the deployment script
chmod +x scripts/deploy.sh
./scripts/deploy.sh your-ec2-ip-address
```

### Step 5: Verify AWS Deployment
```bash
# Get the instance IP from terraform
INSTANCE_IP=$(terraform output -raw instance_public_ip)

# Check the services
echo "Frontend: http://${INSTANCE_IP}:3000"
echo "Backend API: http://${INSTANCE_IP}:8000"
echo "Backend docs: http://${INSTANCE_IP}:8000/docs"
```

### Step 6: Monitor Deployment
```bash
# SSH into the instance
ssh -i ~/.ssh/your-key.pem ubuntu@${INSTANCE_IP}

# Check container status
docker ps

# View logs
docker logs dream-demo-backend-1
docker logs dream-demo-frontend-1
docker logs dream-demo-db-1
```

### Step 7: Cleanup (When Done)
```bash
# From terraform directory on main branch
terraform destroy
# Type 'yes' when prompted
```

---

## Sprint-Specific Considerations

### Sprint 1 (🌹)
- Basic e-commerce functionality
- Contains intentional bugs for testing demonstrations
- Uses: `REACT_APP_SPRINT_VERSION: sprint-1`

### Sprint 2 (🌸)
- Enhanced with Temporal workflow orchestration
- Bug fixes from Sprint 1
- Payment processing improvements
- Uses: `REACT_APP_SPRINT_VERSION: sprint-2`

### Sprint 3 (🌻)
- UX improvements with Material-UI Snackbars
- Enhanced error handling
- Uses: `REACT_APP_SPRINT_VERSION: sprint-3`

---

## Common Issues and Solutions

### Database Connection Issues
```bash
# If backend can't connect to database
docker-compose logs db
docker-compose restart db
docker-compose down -v && docker-compose up --build
```

### Port Conflicts
```bash
# If ports 3000, 8000, or 5432 are in use
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Kill processes or change ports in docker-compose.yml
```

### Image Build Failures
```bash
# Clear Docker cache and rebuild
docker system prune -f
docker-compose build --no-cache
```

### AWS Permissions Issues
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check EC2 key pair exists
aws ec2 describe-key-pairs --key-names your-key-name
```

### Environment Variable Issues
```bash
# Verify environment variables are set
docker-compose config

# Check container environment
docker-compose exec frontend env | grep REACT_APP
```

---

## Automated Deployment (Future)

For fully automated deployments, consider setting up:

1. **GitHub Actions** workflow that triggers on sprint branch pushes
2. **Terraform Cloud** for remote state management
3. **Docker Hub** automated builds
4. **AWS ECS/EKS** for production-grade container orchestration

---

## Security Notes

- Never commit `.env` files or AWS credentials
- Use AWS IAM roles for EC2 instances in production
- Rotate Stripe API keys regularly
- Consider using AWS Secrets Manager for production secrets
- Enable HTTPS with SSL certificates for production deployments

---

## Support

For issues:
1. Check container logs: `docker-compose logs`
2. Verify environment variables: `docker-compose config`
3. Check network connectivity: `docker network ls`
4. Review AWS CloudWatch logs (for AWS deployments)
