#!/bin/bash
# Deployment script for Cocobot Docker container
# This script stops the current container, pulls the latest code, rebuilds the image, and starts the new container

set -e  # Exit on any error

echo "🥥 Starting Cocobot Docker deployment..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in current directory"
    exit 1
fi

echo "📂 Current directory: $(pwd)"

# Pull the latest changes
echo "📥 Pulling latest changes from GitLab..."
git pull origin main

# Log into registry if needed (for private images)
# If using a private registry, uncomment and configure the following lines:
# echo $CI_REGISTRY_PASSWORD | docker login $CI_REGISTRY -u $CI_REGISTRY_USER --password-stdin

# Stop existing containers (if running)
echo "🛑 Stopping existing containers (if any)..."
docker-compose down --remove-orphans || echo "No containers to stop or already stopped"

# Build the new image
echo "🔨 Building new Docker image..."
docker-compose build

# Start the services
echo "🚀 Starting services..."
docker-compose up -d

# Wait a moment for services to start
sleep 5

# Check if the main service is running
if docker-compose ps | grep -q "cocobot.*Up"; then
    echo "✅ Cocobot service is running successfully"
else
    echo "❌ Cocobot service failed to start"
    docker-compose logs cocobot
    exit 1
fi

# Check if database and redis are running too
if docker-compose ps | grep -q "cocobot-db.*Up"; then
    echo "✅ Database service is running"
else
    echo "⚠️ Database service may not be running properly"
fi

if docker-compose ps | grep -q "cocobot-redis.*Up"; then
    echo "✅ Redis service is running"
else
    echo "⚠️ Redis service may not be running properly"
fi

# Show final status
echo "📋 Current container status:"
docker-compose ps

echo "🎉 Deployment complete! Cocobot is now running with the latest changes."