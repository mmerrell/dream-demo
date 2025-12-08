# Dream Demo - E-Commerce Flower Shop

A full-stack e-commerce application designed to demonstrate comprehensive testing capabilities. This project features automated infrastructure deployment, multiple sprint versions, and intentionally includes both working features and documented bugs to showcase real-world testing scenarios.

## 🎯 Project Goals

This application serves as the ultimate demo for UI testing features, showcasing:

- **Complex Web Application Testing**: Multi-page flows, authentication, payments
- **Infrastructure as Code**: Automated AWS deployment with Terraform
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
- **Third-Party Integrations**: Stripe payments, future support for Venmo, CashApp
- **API Testing**: RESTful backend with FastAPI
- **Database Operations**: PostgreSQL with inventory management
- **Detailed Logging**: Comprehensive workflow tracking and monitoring
- **Intentional Bugs**: Documented issues for testing and debugging demonstrations

## 🏗️ Infrastructure as Code

This project uses Terraform for automated infrastructure provisioning and GitHub Actions for CI/CD deployment.

### Prerequisites for Infrastructure

- [Terraform](https://terraform.io/downloads.html) >= 1.5.0
- AWS CLI configured with appropriate credentials
- Docker with buildx support
- AWS account with EC2/VPC permissions

### Infrastructure Setup

1. **Configure AWS credentials:**
```bash
aws configure --profile terraform
# Or export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

2. **Set required environment variables:**
```bash
export STRIPE_SECRET_KEY="sk_test_your_key"
export STRIPE_PUBLISHABLE_KEY="pk_test_your_key"
```

3. **Initialize Terraform:**
```bash
cd terraform
terraform init
```

4. **Deploy infrastructure:**
```bash
terraform plan
terraform apply
```

This creates:
- EC2 instance (t3.large) with Docker pre-installed
- Elastic IP for consistent addressing  
- Security groups (SSH, HTTP ports 3000/8000)
- 30GB encrypted EBS storage

### Manual Deployment

For manual deployment to your infrastructure:
```bash
./scripts/deploy.sh
```

This script:
- Gets the instance IP from Terraform
- Configures application with dynamic IP addresses
- Deploys containers with proper platform compatibility
- Seeds the database with test data

Your application will be accessible at:
- **Frontend:** `http://ELASTIC_IP:3000`
- **Backend API:** `http://ELASTIC_IP:8000`

### Automated Deployment

GitHub Actions automatically deploys on push to sprint branches:

1. **Set GitHub Secrets:**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`

2. **Push to sprint branch:**
```bash
git push origin sprint-2
```

The pipeline automatically:
- Provisions infrastructure with Terraform
- Builds platform-specific Docker images (linux/amd64)
- Deploys to EC2 with proper configuration
- Runs database migrations and seeding

## 🔧 Development vs Deployment

### Local Development
- **Repository:** Sprint branches (sprint-1, sprint-2, etc.)
- **Command:** `docker-compose up`
- **Features:** Hot reload, volume mounts, localhost URLs
- **Database:** Local PostgreSQL container

### Production Deployment  
- **Infrastructure:** Terraform in main branch
- **Application:** Configurable sprint version
- **Command:** `./scripts/deploy.sh` or GitHub Actions
- **Features:** Immutable images, dynamic IPs, production config
- **Database:** Cloud PostgreSQL with persistent storage

### Branch Strategy
- **main:** Infrastructure code, deployment scripts, stable releases
- **sprint-X:** Application features, development workflows  
- **Deploy specific sprint:** `terraform apply -var="sprint=sprint-2"`

## 💰 Cost Management

**Tear down infrastructure when not in use:**
```bash
cd terraform
terraform destroy
```

**Typical AWS costs:**
- t3.large EC2: ~$0.08/hour ($60/month if running 24/7)
- Elastic IP: Free when attached to running instance
- EBS storage: ~$3/month for 30GB
- Data transfer: Minimal for demo usage

**Cost optimization:**
- Destroy infrastructure after demos (`terraform destroy`)
- Recreate in minutes when needed (`terraform apply`)
- Use t3.medium for development (half the cost)

## 🚀 Quick Start - Local Development

### Prerequisites

- Docker Desktop installed and running
- Git
- Stripe test account (free at [stripe.com](https://stripe.com))

### Local Installation

1. **Clone and switch to a sprint branch:**
```bash
git clone <repository-url>
cd dream-demo
git checkout sprint-2
```

2. **Set up environment variables:**
```bash
# Create .env file
cat > .env << EOF
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
DATABASE_URL=postgresql://postgres:password@db:5432/dreamdemo
SECRET_KEY=your-super-secret-jwt-key-here
EOF
```

3. **Start local development:**
```bash
docker-compose up --build
```

4. **Seed the database:**
```bash
docker-compose exec backend python seed_database.py
```

5. **Access locally:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

## 🌟 Sprint Versions

### Sprint-1: Core E-Commerce
- ✅ User authentication (JWT)
- ✅ Product catalog (300+ flowers) 
- ✅ Shopping cart
- ✅ Stripe payment processing
- ✅ Order management

### Sprint-2: Enhanced Features  
- ✅ Improved UI/UX
- ✅ Bug fixes and optimizations
- ✅ Enhanced payment flow
- ✅ Better error handling

### Sprint-3: Advanced Workflows (Planned)
- ✅ Temporal workflow integration
- ✅ Enhanced observability
- ✅ Removal of ugly modals
- ✅ Bug fixes

### Sprint-4: UI Improvements
- ✅ Proper fly-out Shopping Cart drawer
- ✅ Order cards
- ✅ Improved product cards
- ✅ Big improvements to Temporal data flow
- ✅ Terraform improvements (Docker, nginx, etc)

### Sprint-5: Advanced Infrastructure, More UI, Inventory System
- 🚧 Cleaning up bugs introduced with shopping cart/order cards
- 🚧 Native Android App
- 🚧 First Cut of an Inventory System
- 🚧 Additional payment methods
- 🚧 Kafka event streaming

## 🏗️ Architecture

**Current Stack:**
- **Frontend**: React with TypeScript, Material-UI
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL 15
- **Payment**: Stripe (test mode)
- **Workflow**: Temporal
- **Infrastructure**: AWS EC2, Terraform
- **CI/CD**: GitHub Actions
- **Containerization**: Docker (and docker-compose) with multi-platform builds

**Production Architecture:**
```
Internet → Elastic IP → EC2 Instance
                       ├── Frontend Container (Port 3000)
                       ├── Backend Container (Port 8000)
                       ├── Temporal Cluster (Ports 7233 (API) & 8080 (UI)) 
                       └── PostgreSQL Container (Port 5432)
```

## 🐛 Known Bugs

This application intentionally contains bugs for testing demonstrations. See [BUGS.md](./BUGS.md) for:
- Documented issues and their severity
- Reproduction steps  
- Expected vs. actual behavior
- Potential fixes (not implemented)

These bugs are valuable for:
- Demonstrating test automation capabilities
- Showcasing bug detection and reporting
- Training on QA workflows
- Proving ROI of testing tools

## 🛠️ Development

### Project Structure
```
dream-demo/
├── terraform/               # Infrastructure as Code
│   ├── main.tf             # Main Terraform configuration
│   ├── variables.tf        # Input variables
│   ├── outputs.tf          # Output values
│   └── user_data.sh        # EC2 initialization script
├── scripts/                # Deployment automation
│   ├── deploy.sh           # Manual deployment script
│   └── seed_database.py    # Database seeding
├── .github/workflows/      # CI/CD pipelines
│   └── deploy.yml         # GitHub Actions workflow
├── frontend-web/           # React frontend (in sprint branches)
├── backend/               # FastAPI backend (in sprint branches)
├── docker-compose.yml     # Local development (in sprint branches)
├── docker-compose.public.yml  # Production deployment template
└── README.md             # This file
```

### Common Commands

**Infrastructure management:**
```bash
# Deploy infrastructure
terraform apply

# Get instance IP
terraform output instance_ip  

# Destroy infrastructure
terraform destroy
```

**Application deployment:**
```bash  
# Deploy to existing infrastructure
./scripts/deploy.sh

# Check deployment status
ssh -i ~/.ssh/key.pem ec2-user@INSTANCE_IP "docker-compose ps"
```

**Local development:**
```bash
# Start services
docker-compose up

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Rebuild after changes
docker-compose build --no-cache
```

## 📋 Testing

### Test Scenarios Available

**Cross-browser testing:**
- Chrome, Firefox, Safari, Edge compatibility
- JavaScript framework testing (React)
- Payment flow testing (Stripe integration)

**Mobile testing:**  
- iOS and Android device testing
- Responsive design validation
- Touch interaction testing

**API testing:**
- RESTful endpoint validation
- Authentication flows (JWT)
- Payment processing workflows
- Database operations

**Performance testing:**
- Page load times
- API response times  
- Database query performance
- Concurrent user simulation

**Visual testing:**
- Screenshot comparison
- Layout regression detection
- Cross-browser visual consistency

### Test Data

**Stripe Test Cards:**
- Success: `4242 4242 4242 4242`
- Declined: `4000 0000 0000 0002`  
- Insufficient funds: `4000 0000 0000 9995`
- Any future expiry date and 3-digit CVC

**User Accounts:**
- Register new accounts via frontend
- Test authentication flows
- 300+ test products available

## 🗺️ Roadmap

### Infrastructure & DevOps
- [ ] Multi-environment support (dev/staging/prod)
- [ ] Blue-green deployment strategy
- [ ] Kubernetes orchestration
- [ ] Auto-scaling configuration

### Application Features  
- [ ] Temporal workflow integration
- [ ] Kafka event streaming
- [ ] OpenTelemetry observability
- [ ] Additional payment methods (Venmo, CashApp)
- [ ] Advanced inventory management

### Testing & Quality
- [ ] Automated test suites (Selenium, Cypress, Playwright)
- [ ] Visual regression testing
- [ ] Performance monitoring
- [ ] Security testing scenarios

## 🆘 Troubleshooting

**Infrastructure issues:**
```bash
# Check Terraform state
terraform show

# Validate configuration  
terraform validate

# Refresh state
terraform refresh
```

**Deployment issues:**
```bash
# Check instance status
aws ec2 describe-instances --instance-ids INSTANCE_ID

# SSH to instance
ssh -i ~/.ssh/key.pem ec2-user@INSTANCE_IP

# Check container logs
docker-compose logs
```

**Common fixes:**
- **Permission denied (publickey):** Check SSH key path and permissions
- **Port already in use:** Verify security group rules in AWS
- **Container won't start:** Check environment variables and image platform
- **Database connection:** Ensure containers are on same network

## 📝 Support

For technical support or questions about this demo:
- **Technical Issues:** Create GitHub issue
- **Infrastructure Questions:** Contact DevOps team

## 📄 License

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines, coding standards, and submission process.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

*This demo showcases modern DevOps practices with Infrastructure as Code, automated 
deployment pipelines, and comprehensive testing capabilities for developing smart 
and adaptive test strategies platform features.*