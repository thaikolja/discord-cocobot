#!/bin/bash
# Start cocobot: Docker Compose if present, otherwise systemd.

set -e

COCOBOT_DIR="/opt/bots/cocobot"

if [ -f "$COCOBOT_DIR/docker-compose.yml" ]; then
    cd "$COCOBOT_DIR" || { echo "❌ cocobot directory not found: $COCOBOT_DIR"; exit 1; }
    echo "🚀 Starting cocobot Docker services..."
    if docker compose version >/dev/null 2>&1; then
        COMPOSE="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE="docker-compose"
    else
        echo "❌ docker compose is not installed"
        exit 1
    fi
    $COMPOSE up -d
    sleep 3
    if $COMPOSE ps --status running --services 2>/dev/null | grep -qx cocobot \
        || $COMPOSE ps | grep -Eq "cocobot.*(Up|running)"; then
        echo "✅ cocobot container is running"
        $COMPOSE ps
        exit 0
    fi
    echo "❌ cocobot container failed to start"
    $COMPOSE logs cocobot
    exit 1
fi

echo "🚀 Starting cocobot systemd service..."
sudo systemctl start cocobot.service
sleep 3
if sudo systemctl is-active --quiet cocobot.service; then
    echo "✅ cocobot service has been started"
    sudo systemctl status cocobot.service --no-pager -l
else
    echo "❌ cocobot service failed to start"
    sudo systemctl status cocobot.service --no-pager -l
    exit 1
fi
