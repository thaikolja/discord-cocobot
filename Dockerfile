# syntax=docker/dockerfile:1

# Match local/CI runtime (audioop-lts and discord.py need 3.13+)
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user for security and a logs dir the bot can write
RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app
USER appuser

# Run the bot
CMD ["python", "bot.py"]