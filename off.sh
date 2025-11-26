#!/bin/bash
# Script to turn off the cocobot service

echo "🛑 Stopping cocobot service..."

# Stop the service
sudo systemctl stop cocobot.service

# Check if the service stopped successfully
if sudo systemctl is-active --quiet cocobot.service; then
    echo "❌ cocobot service is still running"
    exit 1
else
    echo "✅ cocobot service has been stopped"
    echo "Status:"
    sudo systemctl status cocobot.service --no-pager -l
fi