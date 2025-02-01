#!/bin/bash
#
# Copyright (C) 2025 by Kolja Nolte
# kolja.nolte@gmail.com
# https://gitlab.com/thaikolja/discord-cocobot
#
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
# - Give appropriate credit to the original author.
# - Provide a link to the license.
# - Distribute your contributions under the same license.
#
# For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author:    Kolja Nolte
# Email:     kolja.nolte@gmail.com
# License:   CC BY-NC-SA 4.0
# Date:      2014-2025
# Package:   Thailand Discord
#

# Log: This script is used to deploy the bot to the server.
echo "Starting deployment..."

# Stop the service
systemctl stop cocobot.service

# Log: Change into the bot directory
echo "Changing into /home/api/cocobot"

# Change into the bot directory
cd /home/api/cocobot || exit

# Log: Pull the latest changes
echo "Pulling the latest changes..."

# Pull the latest changes
git pull origin main

# Log: Install dependencies
echo "Installing dependencies..."

# Install dependencies
pip install -r requirements.txt

# Log: Enable the service
echo "Enabling the service..."

# Log: Enable the service
systemctl enable cocobot.service

# Log: Restart the service
echo "Restarting the service..."

# Restart the service
systemctl start cocobot.service

# Log: Check the status
echo "Deployment complete!"
