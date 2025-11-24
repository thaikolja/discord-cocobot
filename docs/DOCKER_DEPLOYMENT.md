# Docker Deployment Guide for Cocobot

This guide explains how to deploy the Cocobot Discord bot using Docker and Docker Compose.

## Prerequisites

- Docker Engine (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- The `.env` file with your bot configuration

## Quick Start

### 1. Environment Configuration

Make sure you have your `.env` file configured with all required environment variables:

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 2. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Docker Compose Services

The `docker-compose.yml` defines the following services:

### `cocobot`
- Main application container
- Built from the `Dockerfile` in this directory
- Automatically restarts if stopped

### `db` (PostgreSQL)
- Database for storing user data, settings, etc.
- Persistent storage using Docker volumes
- Exposes port 5432 for external access (optional)

### `redis` (Redis)
- Caching layer for API responses and rate limiting
- Persistent storage using Docker volumes
- Exposes port 6379 for external access (optional)

## Building the Docker Image

You can build the image separately:

```bash
# Build the image
docker build -t cocobot:latest .

# Run the image (with .env file)
docker run --env-file .env --rm cocobot:latest
```

## Advanced Configuration

### Custom Database Configuration

The database is preconfigured but can be customized in `docker-compose.yml`:

```yaml
db:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=your_database_name
    - POSTGRES_USER=your_username
    - POSTGRES_PASSWORD=your_secure_password
```

### Redis Configuration

Redis is configured with persistence. You can customize it in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Environment Variables

When using Docker, these environment variables are particularly important:

- `DATABASE_URL` - Connection string for database (should match docker-compose)
- `REDIS_URL` - Connection string for Redis (should match docker-compose) 
- `ENVIRONMENT` - Set to 'production' for production deployments
- `LOG_LEVEL` - Set logging level (INFO, DEBUG, WARNING, ERROR)
- All the API keys and bot tokens

## Production Deployment Tips

1. **Secure your `.env` file** - Never commit sensitive information to version control
2. **Use secrets management** - For production, consider using Docker secrets or a vault
3. **Monitor container logs** - Use centralized logging for production systems
4. **Set up monitoring** - Monitor container health and resource usage
5. **Regular updates** - Keep base images updated

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check if database container is running
   docker-compose ps
   # Check database logs
   docker-compose logs db
   ```

2. **Redis Connection Issues**
   ```bash
   # Check if redis container is running
   docker-compose ps
   # Check redis logs
   docker-compose logs redis
   ```

3. **Bot Not Starting**
   ```bash
   # Check bot logs
   docker-compose logs cocobot
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Verify environment variables
   docker-compose exec cocobot env
   ```

### Useful Commands

```bash
# View all container logs
docker-compose logs

# View specific container logs
docker-compose logs cocobot

# Execute command in running container
docker-compose exec cocobot bash

# Check container resource usage
docker-compose top

# Scale services (though not typically needed for cocobot)
docker-compose up -d --scale cocobot=1
```

## Health Checks

The containers include basic health checks. Docker Compose will report the health status:

- Cocobot: Health is determined by whether the process is running
- PostgreSQL: Health is checked via built-in PostgreSQL health check
- Redis: Health is checked via built-in Redis health check

## Cleanup

To completely remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

The `-v` flag removes the named volumes, including the database data.

For regular cleanup without data loss:

```bash
# Stop and remove containers but keep volumes
docker-compose down

# Remove unused Docker objects
docker system prune
```