#!/bin/bash
# Script to turn on the cocobot service

echo "🚀 Starting cocobot service..."

# Start the service
sudo systemctl start cocobot.service

# Check if the service started successfully
sleep 3
if sudo systemctl is-active --quiet cocobot.service; then
    echo "✅ cocobot service has been started"
    echo "Status:"
    sudo systemctl status cocobot.service --no-pager -l
else
    echo "❌ cocobot service failed to start"
    sudo systemctl status cocobot.service --no-pager -l
    exit 1
fi