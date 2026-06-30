#!/bin/bash
# Deployment script for cocobot using Docker

# Set the path to your cocobot directory
COCOBOT_DIR="/opt/discord/cocobot"

# Navigate to the cocobot directory
cd $COCOBOT_DIR || { echo "❌ cocobot directory not found: $COCOBOT_DIR"; exit 1; }

# Run the deployment script
./script/deploy-as-docker.sh
