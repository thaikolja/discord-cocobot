# GitLab CI/CD Pipeline Setup

This guide explains how to set up the GitLab CI/CD pipeline for automated testing and deployment of Cocobot.

## Prerequisites

- GitLab account with project access
- SSH key for server access
- Docker and Docker Compose installed on the target server
- Environment variables configured in GitLab CI/CD settings

## Environment Variables Setup

In your GitLab project, go to **Settings > CI/CD > Variables** and add these variables:

- `SSH_PRIVATE_KEY`: Your SSH private key (type: File, protected: yes, masked: yes)
- `SSH_HOST`: Your server hostname or IP address
- `SSH_USER`: Your SSH username on the server
- `REMOTE_SCRIPT_PATH`: Path to the deployment script on the server (e.g., `/home/user/deploy_cocobot.sh`)
- `OPENAI_API_KEY`: Your OpenAI API key (or other API keys as needed)

## Target Server Setup

### 1. Server Requirements
Your target server should have:
- Debian 12 (or compatible Linux distribution)
- Docker installed
- Docker Compose installed
- Git installed
- SSH access configured

### 2. Initial Setup
On your target server:

```bash
# Install Docker (if not already installed)
sudo apt update
sudo apt install -y docker.io docker-compose

# Add your user to the docker group
sudo usermod -aG docker $USER

# Create a directory for cocobot
mkdir -p ~/cocobot
cd ~/cocobot

# Clone the repository or copy the initial codebase
git clone <your-gitlab-repo-url> .
```

### 3. Environment Configuration
Create a `.env` file in your cocobot directory with all required API keys and configuration:

```bash
# Example .env file
DISCORD_BOT_TOKEN=your_bot_token
WEATHERAPI_API_KEY=your_weather_api_key
CURRENCYAPI_API_KEY=your_currency_api_key
# ... add all other required environment variables
```

### 4. Create Remote Deployment Script
Create the remote deployment script on your server:

```bash
#!/bin/bash
# /home/user/deploy_cocobot.sh

# Set the path to your cocobot directory
COCOBOT_DIR="/home/user/cocobot"

# Navigate to the cocobot directory
cd $COCOBOT_DIR || { echo "❌ Cocobot directory not found: $COCOBOT_DIR"; exit 1; }

# Pull the latest changes and deploy
./deploy_docker.sh
```

Make it executable:
```bash
chmod +x /home/user/deploy_cocobot.sh
```

## How the Pipeline Works

1. **Test Stage**: 
   - Runs on every push to any branch
   - Uses Python 3.13-slim Docker image
   - Sets up virtual environment and installs dependencies
   - Runs pytest on all tests

2. **Deploy Stage**:
   - Runs only on pushes to the `main` branch
   - Uses Alpine Linux with SSH, Docker CLI, and Docker Compose
   - SSH into the target server using configured credentials
   - Executes the remote deployment script

## Deployment Script Features

The `deploy_docker.sh` script:
1. Pulls the latest code from the repository
2. Stops existing Docker containers
3. Builds new Docker images with the latest code
4. Starts the services
5. Verifies that all services are running
6. Reports the final status

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   - Check that your SSH key has proper permissions (400)
   - Ensure the deploy script on the server is executable

2. **Docker Commands Failing**:
   - Verify that your SSH user is in the docker group
   - Check that Docker and Docker Compose are properly installed

3. **Environment Variables Missing**:
   - Ensure all required environment variables are set in `.env` file
   - Verify that the `.env` file is properly included in the Docker setup

### Verification Commands

After deployment, you can verify the status on your server:

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs cocobot

# Check Docker service status
sudo systemctl status docker
```

## Security Considerations

- Keep API keys in GitLab CI/CD variables, not in the repository
- Use masked and protected variables for sensitive data
- Regularly rotate SSH keys
- Monitor deployment logs for any suspicious activity

## Rollback Procedure

In case of deployment issues:
1. Check the GitLab CI/CD pipeline logs
2. Use `docker-compose logs` to examine container logs
3. Revert to a previous commit if needed
4. The pipeline will automatically deploy the fixed version when pushed to main