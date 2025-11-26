#!/bin/bash
# Template for remote deployment script
# This script should be placed on the target server and configured with the correct path to your cocobot directory

# Set the path to your cocobot directory
COCOBOT_DIR="/opt/bots/cocobot"

# Navigate to the cocobot directory
cd $COCOBOT_DIR || { echo "❌ Cocobot directory not found: $COCOBOT_DIR"; exit 1; }

# Run the deployment script
./deploy_docker.sh