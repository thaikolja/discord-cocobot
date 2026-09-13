#!/bin/bash
# Script to turn off the cocobot service

# Change to the cocobot installation directory
# Exit with error code 1 if directory doesn't exist
cd "/opt/bots/cocobot" || exit 1

# Display current working directory for verification
echo "📂 Current directory: $(pwd)"
echo "🛑 Stopping cocobot service..."

# Attempt to stop the systemd service
# This is the primary method of stopping the cocobot application
sudo systemctl stop cocobot.service

# Check if docker-compose.yml exists in the installation directory
# This indicates that the bot is running via Docker containers
if [ -f "/opt/bots/cocobot/docker-compose.yml" ]; then
    # Stop and remove all Docker containers defined in docker-compose.yml
    # --remove-orphans flag removes containers for services not defined in the compose file
    echo "🛑 Stopping existing containers..."
    docker-compose down --remove-orphans || echo "No containers to stop or already stopped."

    # Exit successfully after stopping containers
    exit 0
fi

# Verify that the systemd service has actually stopped
# is-active returns 0 if service is running, non-zero otherwise
# --quiet suppresses output
if sudo systemctl is-active --quiet cocobot.service; then
    # Service is still running - report failure
    echo "❌ cocobot service is still running."

    exit 1
else
    # Service has stopped successfully - report success
    echo "✅ cocobot service has been stopped."
    echo "Status:"

    # Display detailed service status without pagination
    # --no-pager prevents output from being piped to 'less'
    # -l shows full log lines without truncation
    sudo systemctl status cocobot.service --no-pager -l
fi

exit 0
