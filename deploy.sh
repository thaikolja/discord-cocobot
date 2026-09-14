#!/bin/bash
# Deployment shortcut for cocobot using Docker

set -e

COCOBOT_DIR="/opt/discord/cocobot"

cd "$COCOBOT_DIR" || { echo "❌ cocobot directory not found: $COCOBOT_DIR"; exit 1; }

./scripts/deploy-as-docker.sh
