#!/bin/bash
# Deployment script for cocobot
# This script deploys the bot to the production server.

set -e # Exit on any error

echo "🥥 Starting cocobot deployment..."

# Stop the service
echo "🛑 Stopping cocobot service..."
systemctl stop cocobot.service || echo "Service was not running"

# Change into the bot directory
echo "📁 Changing to bot directory..."
cd /opt/discord/cocobot || {
  echo "❌ Failed to change directory"
  exit 1
}

# Activate Python environment
echo "🐍 Activating virtual environment..."
source ./venv/bin/activate

# Pull the latest changes
echo "📥 Pulling latest changes from GitLab..."
git pull origin main || {
  echo "❌ Failed to pull changes"
  exit 1
}

# Install dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt || {
  echo "❌ Failed to install dependencies"
  exit 1
}

# Enable the service
echo "⚙️ Enabling cocobot service..."
systemctl enable cocobot.service

# Restart the service
echo "🚀 Starting cocobot service..."
systemctl start cocobot.service

# Check service status
echo "🔍 Checking service status..."
sleep 3
if systemctl is-active --quiet cocobot.service; then
  echo "✅ Deployment successful! cocobot is running."
else
  echo "❌ Deployment failed! cocobot is not running."
  echo "Service status:"
  systemctl status cocobot.service
  exit 1
fi

echo "🎉 Deployment complete!"
