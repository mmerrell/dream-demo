#!/bin/bash
set -e

# Check if terraform.tfvars exists, otherwise use parameter
if [ -f "terraform/terraform.tfvars" ]; then
    SPRINT_VERSION=$(grep 'sprint =' terraform/terraform.tfvars | cut -d'"' -f2)
    echo "Using sprint version from terraform.tfvars: $SPRINT_VERSION"
elif [ ! -z "$1" ]; then
    SPRINT_VERSION="$1"
    echo "Using sprint version from parameter: $SPRINT_VERSION"
else
    echo "Error: No terraform.tfvars found and no sprint version provided"
    echo "Usage: $0 [sprint-version]"
    echo "   or create terraform/terraform.tfvars with sprint variable"
    exit 1
fi

# Check for required environment variables
if [ -z "$STRIPE_SECRET_KEY" ] || [ -z "$STRIPE_PUBLISHABLE_KEY" ]; then
    echo "Error: Stripe keys not set!"
    echo "Please set environment variables:"
    echo "export STRIPE_SECRET_KEY='sk_test_...'"
    echo "export STRIPE_PUBLISHABLE_KEY='pk_test_...'"
    exit 1
fi

INSTANCE_IP=$(terraform -chdir=terraform output -raw instance_public_ip | tr -d '\n\r ')
echo "Deploying to instance: $INSTANCE_IP"

# Select the appropriate template based on sprint version
if [ -f "docker-compose.${SPRINT_VERSION}.yml" ]; then
    TEMPLATE_FILE="docker-compose.${SPRINT_VERSION}.yml"
    echo "Using template: $TEMPLATE_FILE"
else
    TEMPLATE_FILE="docker-compose.sprint-1.yml"  # fallback
    echo "Template for $SPRINT_VERSION not found, using fallback: $TEMPLATE_FILE"
fi

# Generate docker-compose with substituted variables
SPRINT_VERSION=$SPRINT_VERSION INSTANCE_IP=$INSTANCE_IP envsubst < $TEMPLATE_FILE > docker-compose.generated.yml

# Copy files to instance
scp -i ~/.ssh/mmerrell-sauce.pem docker-compose.generated.yml ec2-user@$INSTANCE_IP:~/docker-compose.yml
scp -i ~/.ssh/mmerrell-sauce.pem scripts/seed_database.py ec2-user@$INSTANCE_IP:~/

# Deploy and seed database
ssh -i ~/.ssh/mmerrell-sauce.pem ec2-user@$INSTANCE_IP "
    # Create .env with actual values
    cat > .env << EOF
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
DATABASE_URL=postgresql://postgres:password@db:5432/dreamdemo
EOF

    export INSTANCE_IP=$INSTANCE_IP
    export REACT_APP_SPRINT_VERSION=$SPRINT_VERSION

    docker-compose up -d
    sleep 10

    # Copy seed script and run
    docker cp ~/seed_database.py \$(docker-compose ps -q backend):/app/seed_database.py
    docker-compose exec -T backend python seed_database.py
"

echo "Deployment complete! Frontend: http://$INSTANCE_IP:3000"