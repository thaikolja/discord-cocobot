# Production Deployment Guide

This guide provides step-by-step instructions for deploying your Discord bot to production environments.

## Prerequisites

- Linux server (Ubuntu 20.04 LTS or newer recommended)
- Python 3.8 or higher
- Git
- A Discord application and bot token
- API keys for all required services
- Basic Linux command line knowledge

## Step 1: Server Setup

### 1.1 Update the system
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install required packages
```bash
sudo apt install python3 python3-pip python3-venv git curl supervisor nginx -y
```

### 1.3 Create a dedicated user for the bot
```bash
sudo useradd -m -s /bin/bash discord-bot
sudo usermod -aG sudo discord-bot
```

## Step 2: Application Setup

### 2.1 Switch to the bot user
```bash
sudo su - discord-bot
```

### 2.2 Clone the repository
```bash
cd ~
git clone https://github.com/yourusername/cocobot.git
cd cocobot
```

### 2.3 Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.4 Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 3: Configuration

### 3.1 Create environment file
```bash
cp .env.example .env
nano .env
```

### 3.2 Fill in your environment variables:
- `DISCORD_BOT_TOKEN=` - Your Discord bot token
- `WEATHERAPI_API_KEY=` - WeatherAPI key
- `CURRENCYAPI_API_KEY=` - CurrencyAPI key
- `DATABASE_URL=` - Database connection string (e.g., `postgresql://user:pass@localhost/cocobot`)
- `REDIS_URL=` - Redis connection string (e.g., `redis://localhost:6379/0`)
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

## Step 4: Database Setup (Optional)

### 4.1 Install PostgreSQL (if using PostgreSQL)
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4.2 Create database and user
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE cocobot;
CREATE USER cocobot WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE cocobot TO cocobot;
\q
```

### 4.3 Install PostgreSQL client libraries
```bash
sudo apt install libpq-dev -y
pip install psycopg2-binary
```

## Step 5: Redis Setup (Optional)

### 5.1 Install Redis
```bash
sudo apt install redis-server -y
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## Step 6: Testing

### 6.1 Test the bot manually (once)
```bash
source venv/bin/activate
python bot.py
```

> Press Ctrl+C to stop after confirming it starts successfully

## Step 7: Process Management with Supervisor

### 7.1 Create supervisor configuration
```bash
exit  # Return to your regular user
sudo nano /etc/supervisor/conf.d/cocobot.conf
```

### 7.2 Add the following configuration:
```ini
[program:cocobot]
command=/home/discord-bot/cocobot/venv/bin/python /home/discord-bot/cocobot/bot.py
directory=/home/discord-bot/cocobot
user=discord-bot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cocobot.log
environment=PYTHONPATH="/home/discord-bot/cocobot"
startsecs=10
stopwaitsecs=10
```

### 7.3 Reload supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cocobot
```

### 7.4 Check the bot status
```bash
sudo supervisorctl status cocobot
```

## Step 8: Log Management

### 8.1 Create logrotate configuration
```bash
sudo nano /etc/logrotate.d/cocobot
```

### 8.2 Add:
```
/var/log/cocobot.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 640 discord-bot adm
    postrotate
        supervisorctl restart cocobot > /dev/null 2>&1 || true
    endscript
}
```

## Step 9: Monitoring and Maintenance

### 9.1 Check logs regularly
```bash
sudo tail -f /var/log/cocobot.log
```

### 9.2 Monitor bot status
```bash
sudo supervisorctl status cocobot
```

### 9.3 Update the bot (when new code is available)
```bash
sudo su - discord-bot
cd ~/cocobot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart cocobot
```

## Step 10: Backup Strategy

### 10.1 Create backup script
```bash
sudo nano /home/discord-bot/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/discord-bot/backups"

mkdir -p $BACKUP_DIR

# Backup database (example for PostgreSQL)
pg_dump -U cocobot -h localhost cocobot > $BACKUP_DIR/database_$DATE.sql

# Backup config files
cp -r /home/discord-bot/cocobot/.env $BACKUP_DIR/config_$DATE.bak

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "config_*.bak" -mtime +7 -delete
```

### 10.2 Make it executable and set up cron job
```bash
chmod +x /home/discord-bot/backup.sh

# Edit crontab
crontab -e
```

Add this line to backup daily at 2 AM:
```
0 2 * * * /home/discord-bot/backup.sh
```

## Troubleshooting

### Bot won't start
- Check logs: `sudo tail -f /var/log/cocobot.log`
- Verify environment variables in `.env`
- Ensure all API keys are correct

### Database connection issues
- Verify PostgreSQL service is running: `sudo systemctl status postgresql`
- Check database credentials
- Ensure the database user has proper permissions

### Rate limiting issues
- Verify Redis is running: `sudo systemctl status redis-server`
- Check Redis connection string in `.env`

### Permission errors
- Ensure the `discord-bot` user owns all bot files
- Check file permissions: `ls -la /home/discord-bot/cocobot/`