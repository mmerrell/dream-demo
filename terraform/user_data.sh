#!/bin/bash
set -e

# DreamDemo Sprint Deployment Script
# Variables from Terraform
SPRINT_NAME="${sprint_name}"
DOCKER_REGISTRY="${docker_registry}"
DOMAIN_NAME="${domain_name}"

echo "Starting deployment for $SPRINT_NAME at $DOMAIN_NAME"

# Update system
yum update -y

# Install Docker and other dependencies
yum install -y docker git curl
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Nginx for reverse proxy
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# Create nginx configuration
cat > /etc/nginx/conf.d/dream-demo.conf << EOF
upstream frontend {
    server localhost:3000;
}

upstream backend {
    server localhost:8000;
}

upstream temporal {
    server localhost:8080;
}

server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /docs {
        proxy_pass http://backend/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /temporal {
        proxy_pass http://temporal;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://backend/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Remove default nginx config
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/conf.d/default.conf

# Test and reload nginx
nginx -t && systemctl reload nginx

# Create application directory
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# Create docker-compose file
cat > docker-compose.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: dreamdemo
      POSTGRES_USER: dreamuser
      POSTGRES_PASSWORD: dreampass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dreamuser -d dreamdemo"]
      interval: 10s
      timeout: 5s
      retries: 5

  temporal:
    image: temporalio/auto-setup:1.22.4
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=dreamuser
      - POSTGRES_PWD=dreampass
      - POSTGRES_SEEDS=db
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development-sql.yaml
    ports:
      - "7233:7233"
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy

  backend:
    image: $DOCKER_REGISTRY/dream-demo-backend:$SPRINT_NAME
    environment:
      DATABASE_URL: postgresql://dreamuser:dreampass@db:5432/dreamdemo
      TEMPORAL_ADDRESS: temporal:7233
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      temporal:
        condition: service_started
    restart: unless-stopped

  frontend:
    image: $DOCKER_REGISTRY/dream-demo-frontend:$SPRINT_NAME
    environment:
      REACT_APP_SPRINT_VERSION: $SPRINT_NAME
      REACT_APP_API_URL: http://$DOMAIN_NAME/api
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Create environment file
cat > .env << EOF
DOCKER_REGISTRY=$DOCKER_REGISTRY
SPRINT_NAME=$SPRINT_NAME
DOMAIN_NAME=$DOMAIN_NAME
EOF

# Set ownership
chown -R ec2-user:ec2-user /home/ec2-user/app

# Pull and start services
echo "Pulling Docker images for $SPRINT_NAME..."
docker-compose pull

echo "Starting services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 60

# Health check
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is healthy"
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 10
done

# Verify installations
docker --version
docker-compose --version

# Mark complete
touch /home/ec2-user/.user_data_complete

echo "Deployment complete for $SPRINT_NAME at $DOMAIN_NAME"
echo "Services available at http://$DOMAIN_NAME"