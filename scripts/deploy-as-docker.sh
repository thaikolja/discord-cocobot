#!/bin/bash
# Deployment script for Cocobot Docker containers.
# Stops current containers, fast-forwards git, rebuilds, and starts services.

set -e

COCOBOT_DIR="/opt/discord/cocobot"

echo "🥥 Starting Cocobot Docker deployment..."

cd "$COCOBOT_DIR" || { echo "❌ Failed to change directory: $COCOBOT_DIR"; exit 1; }

if [ ! -f "$COCOBOT_DIR/docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in $COCOBOT_DIR"
    exit 1
fi

if [ ! -f "$COCOBOT_DIR/.env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "❌ docker compose is not installed"
    exit 1
fi

echo "📂 Current directory: $(pwd)"

echo "📥 Resetting checkout to origin/main (keeps untracked .env)..."
git fetch origin
git reset --hard origin/main

echo "🛑 Stopping existing containers (if any)..."
$COMPOSE down --remove-orphans || echo "No containers to stop or already stopped"

echo "🔨 Building new Docker image..."
$COMPOSE build

echo "🚀 Starting services..."
$COMPOSE up -d

sleep 5

if $COMPOSE ps --status running --services 2>/dev/null | grep -qx cocobot \
    || $COMPOSE ps | grep -Eq "cocobot.*(Up|running)"; then
    echo "✅ Cocobot service is running successfully"
else
    echo "❌ Cocobot service failed to start"
    $COMPOSE logs cocobot
    exit 1
fi

if $COMPOSE ps --status running --services 2>/dev/null | grep -qx db \
    || $COMPOSE ps | grep -Eq "cocobot-db.*(Up|running)"; then
    echo "✅ Database service is running"
else
    echo "⚠️ Database service may not be running properly"
fi

if $COMPOSE ps --status running --services 2>/dev/null | grep -qx redis \
    || $COMPOSE ps | grep -Eq "cocobot-redis.*(Up|running)"; then
    echo "✅ Redis service is running"
else
    echo "⚠️ Redis service may not be running properly"
fi

echo "📋 Current container status:"
$COMPOSE ps

echo "🎉 Deployment complete! Cocobot is now running with the latest changes."
