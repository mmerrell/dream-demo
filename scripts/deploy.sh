#!/bin/bash
set -e

# Get instance IP and clean it
INSTANCE_IP=$(terraform -chdir=terraform output -raw instance_ip | tr -d '\n\r ')
echo "Deploying to instance: $INSTANCE_IP"

# Generate docker-compose with substituted IP
INSTANCE_IP=$INSTANCE_IP envsubst < docker-compose.public.yml > docker-compose.generated.yml

# Copy files to instance
scp -i ~/.ssh/mmerrell-sauce.pem docker-compose.generated.yml ec2-user@$INSTANCE_IP:~/docker-compose.yml
scp -i ~/.ssh/mmerrell-sauce.pem .env.template ec2-user@$INSTANCE_IP:~/
scp -i ~/.ssh/mmerrell-sauce.pem scripts/seed_database.py ec2-user@$INSTANCE_IP:~/  # Add seed script

# Deploy and seed database
ssh -i ~/.ssh/mmerrell-sauce.pem ec2-user@$INSTANCE_IP "
    cp .env.template .env
    echo 'STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}' >> .env
    echo 'STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}' >> .env
    export INSTANCE_IP=$INSTANCE_IP
    
    # Start containers
    docker-compose up -d
    
    # Wait for database to be ready
    sleep 10
    
    # Seed the database
    docker cp ~/seed_database.py \$(docker-compose ps -q backend):/app/seed_database.py

    docker-compose exec -T backend python seed_database.py
"

echo "Deployment complete! Frontend: http://$INSTANCE_IP:3000"
