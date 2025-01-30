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

echo "Starting deployment..."

# Stop the existing service
systemctl stop cocobot.service

echo "Changing into /home/api/cocobot"
cd /home/api/cocobot

git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart the service
systemctl start cocobot.service

echo "Deployment complete!"