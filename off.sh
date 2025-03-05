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
echo "Stopping cocobot..."

# Stop the service
systemctl stop cocobot.service
systemctl disable cocobot.service

exit 1