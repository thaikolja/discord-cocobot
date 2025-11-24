# Docker Deployment Guide

This guide provides step-by-step instructions for deploying your Discord bot using Docker and Docker Compose.

## Prerequisites

- Docker Engine (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git
- A Discord application and bot token
- API keys for all required services

## Step 1: Clone the Repository

### 1.1 Open terminal/command prompt
```bash
git clone https://github.com/yourusername/cocobot.git
cd cocobot
```

## Step 2: Configure Environment Variables

### 2.1 Copy the example environment file
```bash
cp .env.example .env
```

### 2.2 Edit the environment file
```bash
nano .env  # or use your preferred text editor
```

### 2.3 Fill in your environment variables:
- `DISCORD_BOT_TOKEN=` - Your Discord bot token
- `WEATHERAPI_API_KEY=` - WeatherAPI key
- `CURRENCYAPI_API_KEY=` - CurrencyAPI key
- `LOCALTIME_API_KEY=` - LocalTime API key
- `GOOGLE_API_KEY=` - Google API key
- `GOOGLE_MAPS_API_KEY=` - Google Maps API key
- `GEOAPFIY_API_KEY=` - Geoapify API key
- `ACQIN_API_KEY=` - AcqIn API key
- `GROQ_API_KEY=` - Groq API key
- `SAMBANOVA_API_KEY=` - Sambanova API key
- `DISCORD_SERVER_ID=` - Your Discord server ID
- `DISCORD_BOT_ID=` - Your Discord bot ID
- `DATABASE_URL=postgresql://cocobot:password@db:5432/cocobot`
- `REDIS_URL=redis://redis:6379/0`
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

## Step 3: Docker Configuration Review

### 3.1 Review the Dockerfile
The `Dockerfile` contains the build instructions for the bot container. No changes are typically needed.

### 3.2 Review the docker-compose.yml
The `docker-compose.yml` defines the services. The main services are:
- `cocobot`: The main application container
- `db`: PostgreSQL database for persistent storage
- `redis`: Redis for caching and rate limiting

## Step 4: Initial Setup

### 4.1 Build the Docker images
```bash
docker-compose build
```

### 4.2 Initialize the database (first time only)
```bash
# The database will be automatically created on first run
# No manual initialization needed
```

## Step 5: Running the Bot

### 5.1 Start all services in detached mode
```bash
docker-compose up -d
```

### 5.2 Check service status
```bash
docker-compose ps
```

### 5.3 View logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs cocobot

# Follow logs in real-time
docker-compose logs -f cocobot
```

## Step 6: Verifying the Setup

### 6.1 Check if the bot is running
```bash
docker-compose ps
```
You should see all three services (cocobot, db, redis) as "Up".

### 6.2 Check bot logs for successful startup
```bash
docker-compose logs cocobot
```
Look for messages like "cocobot is ready!" to confirm the bot started successfully.

### 6.3 Add the bot to your server
1. Get the bot's OAuth2 URL from Discord Developer Portal
2. Add the bot to your Discord server
3. The bot should appear online once connected

## Step 7: Managing the Docker Deployment

### 7.1 Stopping the services
```bash
docker-compose down
```

### 7.2 Stopping and removing volumes (will lose data)
```bash
docker-compose down -v
```

### 7.3 Restarting the services
```bash
docker-compose restart
```

### 7.4 Updating the bot code
```bash
# Pull the latest code
git pull origin main

# Rebuild the image
docker-compose build

# Restart the services
docker-compose up -d
```

### 7.5 Scaling (if needed)
```bash
# To scale to multiple instances (not typically needed for a Discord bot)
docker-compose up -d --scale cocobot=1
```

## Step 8: Database Management

### 8.1 Accessing the database container
```bash
docker-compose exec db psql -U cocobot -d cocobot
```

### 8.2 Backing up the database
```bash
docker-compose exec db pg_dump -U cocobot cocobot > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 8.3 Restoring the database
```bash
cat backup_file.sql | docker-compose exec -T db psql -U cocobot -d cocobot
```

## Step 9: Redis Management

### 9.1 Accessing the Redis container
```bash
docker-compose exec redis redis-cli
```

### 9.2 Checking Redis status
```bash
docker-compose exec redis redis-cli ping
```

## Step 10: Monitoring and Maintenance

### 10.1 Check resource usage
```bash
docker-compose top
```

### 10.2 Check disk usage
```bash
docker system df
```

### 10.3 Cleanup unused Docker objects
```bash
docker system prune -f
```

### 10.4 View detailed container stats
```bash
docker stats
```

## Step 11: Configuration Updates

### 11.1 After changing environment variables
```bash
# Stop the services
docker-compose down

# Start the services with new environment variables
docker-compose up -d
```

### 11.2 After changing docker-compose.yml
```bash
# Rebuild and restart
docker-compose up -d --build
```

## Step 12: Troubleshooting

### 12.1 Bot container failing to start
Check the logs:
```bash
docker-compose logs cocobot
```
Common issues:
- Missing environment variables
- Incorrect API keys
- Database connection issues

### 12.2 Database connection issues
Check database logs:
```bash
docker-compose logs db
```
Verify the `DATABASE_URL` in your `.env` file matches the service name in `docker-compose.yml`.

### 12.3 Redis connection issues
Check Redis logs:
```bash
docker-compose logs redis
```
Verify the `REDIS_URL` in your `.env` file matches the service name in `docker-compose.yml`.

### 12.4 Cannot find Docker Compose command
If you get "docker-compose: command not found", try:
```bash
# On some systems, use:
docker compose up -d  # Note: without the hyphen
```

### 12.5 Port conflicts
If ports 5432 or 6379 are already in use:
- The containers use internal Docker networking
- External ports are only exposed for debugging
- You can comment out the 'ports' sections in `docker-compose.yml`

## Step 13: Production Considerations

### 13.1 Security
- Use strong passwords in production
- Keep environment files secure (never commit to version control)
- Regularly update Docker images
- Monitor access logs

### 13.2 Backup Strategy
- Regularly backup the PostgreSQL volume
- Consider automated backup solutions
- Store backups securely offsite

### 13.3 Monitoring
- Set up health checks
- Monitor resource usage
- Set up alerting for failures
- Log aggregation and analysis

### 13.4 Updates
- Test updates in a staging environment first
- Have a rollback plan
- Schedule maintenance windows
- Monitor after updates

## Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f cocobot

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build

# Check resource usage
docker-compose top
```

## Common Issues and Solutions

- **"Permission denied" errors**: Make sure you're not running Docker commands with sudo unnecessarily
- **"Port already allocated"**: Other services might be using the exposed ports (5432, 6379)
- **"Connection refused"**: The database or Redis might still be starting up; wait a minute and check logs
- **High memory usage**: Check for memory leaks in your code or increase container limits in docker-compose.yml